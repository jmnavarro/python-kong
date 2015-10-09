# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import uuid
import copy
import hashlib

from .contract import KongAdminContract, APIPluginConfigurationAdminContract, APIAdminContract, ConsumerAdminContract, \
    PluginAdminContract, BasicAuthAdminContract, KeyAuthAdminContract, OAuth2AdminContract
from .utils import timestamp, uuid_or_string, add_url_params, assert_dict_keys_in, ensure_trailing_slash
from .compat import OrderedDict
from .exceptions import ConflictError

INVALID_FIELD_ERROR_TEMPLATE = '%r is not a valid field. Allowed fields: %r'


def filter_api_struct(api_struct, filter_dict):
    """
    This utility removes keys from a dictionary if their respective value did not differ from their default value.
      This is used by the Simulator classes to match the responses with Kong's responses.
    """

    return dict((k, v) for k, v in api_struct.items() if k not in filter_dict or filter_dict[k] != api_struct[k])


def filter_dict_list(list_of_dicts, **field_filter):
    """
    This utility filters a list of dictionaries based on the values of one or more keys
    """
    def _filter(_dicts, key, value):
        return [d for d in _dicts if d[key] == value]

    list_of_dicts = copy.copy(list_of_dicts)
    for key in field_filter:
        list_of_dicts = _filter(list_of_dicts, key, field_filter[key])

    return list_of_dicts


class SimulatorDataStore(object):
    def __init__(self, api_url, data_struct_filter=None):
        self.api_url = api_url
        self._data_struct_filter = data_struct_filter or {}
        self._data = OrderedDict()

    def destroy(self):
        self.api_url = None
        self._data_struct_filter = None
        self._data = None

    def count(self):
        return len(self._data.keys())

    def create(self, data_struct, check_conflict_keys=None):
        assert 'id' not in data_struct

        # Prevent conflicts
        if check_conflict_keys:
            errors = []
            for key in check_conflict_keys:
                assert key in data_struct

                existing_value = self._get_by_field(key, data_struct[key])
                if existing_value is not None:
                    errors.append('%s already exists with value \'%s\'' % (key, existing_value[key]))
            if errors:
                raise ConflictError(', '.join(errors))

        id = str(uuid.uuid4())
        data_struct['id'] = id

        self._data[id] = data_struct
        return filter_api_struct(data_struct, self._data_struct_filter)

    def update(self, value_or_id, key, data_struct_update):
        value_or_id = uuid_or_string(value_or_id)

        if value_or_id in self._data:
            self._data[value_or_id].update(data_struct_update)
            return filter_api_struct(self._data[value_or_id], self._data_struct_filter)

        if key is not None:
            for id in self._data:
                if self._data[id][key] == value_or_id:
                    self._data[id].update(data_struct_update)
                    return filter_api_struct(self._data[id], self._data_struct_filter)

    def retrieve(self, value_or_id, key):
        value_or_id = uuid_or_string(value_or_id)

        if value_or_id in self._data:
            return filter_api_struct(self._data[value_or_id], self._data_struct_filter)

        if key is not None:
            for id in self._data:
                if self._data[id][key] == value_or_id:
                    return filter_api_struct(self._data[id], self._data_struct_filter)

    def list(self, size, offset, **filter_fields):
        data_list = [filter_api_struct(data_struct, self._data_struct_filter)
                     for data_struct in filter_dict_list(self._data.values(), **filter_fields)]

        offset_index = 0
        if offset is not None:
            keys = list([item['id'] for item in self._data.values()])
            offset_index = keys.index(uuid_or_string(offset))

        sliced_data = data_list[offset_index:offset_index + size]

        next_url = None
        next_index = offset_index + size
        if next_index < len(data_list):
            next_offset = data_list[next_index]['id']
            next_url = add_url_params(self.api_url, {
                'size': size,
                'offset': next_offset
            })

        result = {
            # 'total': len(sliced_data),  # Appearantly, the real API doesn't return this value either...
            'data': sliced_data,
        }

        if next_url:
            result['next'] = next_url

        return result

    def delete(self, value_or_id, key):
        value_or_id = uuid_or_string(value_or_id)

        if value_or_id in self._data:
            del self._data[value_or_id]

        if key is not None:
            for id in self._data:
                if self._data[id][key] == value_or_id:
                    del self._data[id]
                    break

    def _get_by_field(self, field, value):
        for data_struct in self._data.values():
            if data_struct[field] == value:
                return data_struct


class APIPluginConfigurationAdminSimulator(APIPluginConfigurationAdminContract):
    def __init__(self, api_admin, api_name_or_id, api_url):
        self.api_admin = api_admin
        self.api_name_or_id = api_name_or_id
        self.api_url = api_url
        self._data = OrderedDict()

    def destroy(self):
        self.api_admin = None
        self.api_name_or_id = None
        self.api_url = None
        self._data = None

    def create(self, plugin_name, enabled=None, consumer_id=None, **fields):
        plugins = PluginAdminSimulator.PLUGINS

        if plugin_name not in plugins.keys():
            raise ValueError('Unknown plugin_name: %s' % plugin_name)

        if plugin_name in self._data:
            raise ConflictError('Plugin configuration already exists')

        known_fields = plugins[plugin_name].get('fields')

        for key in fields:
            if key not in known_fields:
                raise ValueError('Unknown value field: %s' % key)

        for key in known_fields:
            if known_fields[key].get('required', False) and key not in fields:
                raise ValueError('Missing required value field: %s' % key)

        id = str(uuid.uuid4())
        api_data = self.api_admin.retrieve(self.api_name_or_id)
        api_id = api_data['id']

        self._data[plugin_name] = {
            'id': id,
            'api_id': api_id,
            'name': plugin_name,
            'config': fields,
            'created_at': timestamp(),
            'enabled': True if enabled is None else enabled
        }

        if consumer_id is not None:
            self._data[plugin_name]['consumer_id'] = consumer_id

        return self._data[plugin_name]

    def create_or_update(self, plugin_name, plugin_configuration_id=None, enabled=None, consumer_id=None, **fields):
        if plugin_configuration_id is not None:
            return self.update(plugin_configuration_id, enabled=enabled, consumer_id=consumer_id, **fields)
        return self.create(plugin_name, enabled=enabled, consumer_id=consumer_id, **fields)

    def update(self, plugin_id, enabled=None, consumer_id=None, **fields):
        current_plugin_id = None
        current_plugin_name = None

        for obj in self._data.values():
            if obj['id'] == plugin_id:
                current_plugin_id = obj['id']
                current_plugin_name = obj['name']
                break

        if current_plugin_name is None or current_plugin_id is None:
            raise ValueError('Unknown plugin_id: %s' % plugin_id)

        if current_plugin_name not in PluginAdminSimulator.PLUGINS.keys():
            raise ValueError('Unknown plugin_name: %s' % current_plugin_name)

        for key in fields:
            if key not in PluginAdminSimulator.PLUGINS[current_plugin_name]['fields']:
                raise ValueError('Unknown value field "%s" for plugin: %s' % (key, current_plugin_name))

        data_struct_update = {
            'config': fields
        }

        if consumer_id is not None:
            data_struct_update['consumer_id'] = consumer_id

        if enabled is not None and isinstance(enabled, bool):
            data_struct_update['enabled'] = enabled

        self._data[current_plugin_name].update(data_struct_update)

        return self._data[current_plugin_name]

    def list(self, size=100, offset=None, **filter_fields):
        data_list = [data_struct for data_struct in filter_dict_list(self._data.values(), **filter_fields)]

        offset_index = 0
        if offset is not None:
            keys = list([plugin_configuration['id'] for plugin_configuration in self._data.values()])
            offset_index = keys.index(uuid_or_string(offset))

        sliced_data = data_list[offset_index:offset_index + size]

        next_url = None
        next_index = offset_index + size
        if next_index < len(data_list):
            next_offset = data_list[next_index]['id']
            next_url = add_url_params(self.api_url, {
                'size': size,
                'offset': next_offset
            })

        result = {
            # 'total': len(sliced_data),  # Appearantly, the real API doesn't return this value either...
            'data': sliced_data,
        }

        if next_url:
            result['next'] = next_url

        return result

    def delete(self, plugin_id):
        plugin_id = uuid_or_string(plugin_id)

        if plugin_id in self._data:
            del self._data[plugin_id]

        for plugin_name in self._data:
            if self._data[plugin_name]['id'] == plugin_id:
                del self._data[plugin_name]
                break

    def retrieve(self, plugin_id):
        plugin_id = uuid_or_string(plugin_id)

        if plugin_id in self._data:
            return self._data[plugin_id]

        for plugin_name in self._data:
            if self._data[plugin_name]['id'] == plugin_id:
                return self._data[plugin_name]

    def count(self):
        return len(self._data.keys())


class APIAdminSimulator(APIAdminContract):
    def __init__(self, api_url=None):
        self._store = SimulatorDataStore(
            api_url or 'http://localhost:8001/apis/',
            data_struct_filter={
                'request_host': None,
                'request_path': None
            })
        self._plugin_admins = {}

    def destroy(self):
        self._store.destroy()
        self._store = None

        for key in self._plugin_admins:
            self._plugin_admins[key].destroy()
            del self._plugin_admins[key]
        self._plugin_admins = None

    def count(self):
        return self._store.count()

    def create(self, upstream_url, name=None, request_host=None, request_path=None, strip_request_path=False,
               preserve_host=False):
        assert upstream_url is not None
        if not request_host and not request_path:
            raise ValueError('At least a \'request_host\' or a \'request_path\' must be specified, '
                             'At least a \'request_host\' or a \'request_path\' must be specified')  # According to spec

        # ensure trailing slash
        upstream_url = ensure_trailing_slash(upstream_url)

        return self._store.create({
            'name': name or request_host,
            'request_host': request_host,
            'request_path': request_path,
            'strip_request_path': strip_request_path,
            'preserve_host': preserve_host,
            'upstream_url': upstream_url,
            'created_at': timestamp()
        }, check_conflict_keys=('name', 'request_host'))

    def create_or_update(self, upstream_url, api_id=None, name=None, request_host=None, request_path=None,
                         strip_request_path=False, preserve_host=False):
        data = {
            'name': name or request_host,
            'request_host': request_host,
            'request_path': request_path,
            'strip_request_path': strip_request_path,
            'preserve_host': preserve_host,
            'upstream_url': upstream_url,
        }

        if api_id is not None:
            return self.update(api_id, **data)

        return self.create(**data)

    def update(self, name_or_id, upstream_url, **fields):
        assert_dict_keys_in(
            fields, ['name', 'request_host', 'request_path', 'strip_request_path', 'preserve_host'],
            INVALID_FIELD_ERROR_TEMPLATE)

        # ensure trailing slash
        upstream_url = ensure_trailing_slash(upstream_url)

        return self._store.update(name_or_id, 'name', dict({
            'upstream_url': upstream_url
        }, **fields))

    def retrieve(self, name_or_id):
        return self._store.retrieve(name_or_id, 'name')

    def list(self, size=100, offset=None, **filter_fields):
        assert_dict_keys_in(filter_fields, ['id', 'name', 'request_host', 'upstream_url'], INVALID_FIELD_ERROR_TEMPLATE)
        return self._store.list(size, offset, **filter_fields)

    def delete(self, name_or_id):
        api_id = self.retrieve(name_or_id).get('id')

        if api_id is None:
            raise ValueError('Unknown name_or_id: %s' % name_or_id)

        if api_id in self._plugin_admins:
            self._plugin_admins[api_id].api_admin = None
            del self._plugin_admins[api_id]

        return self._store.delete(name_or_id, 'name')

    def plugins(self, name_or_id):
        api_id = self.retrieve(name_or_id).get('id')

        if api_id is None:
            raise ValueError('Unknown name_or_id: %s' % name_or_id)

        if api_id not in self._plugin_admins:
            self._plugin_admins[api_id] = APIPluginConfigurationAdminSimulator(self, name_or_id, self._store.api_url)

        return self._plugin_admins[api_id]


class BasicAuthAdminSimulator(BasicAuthAdminContract):
    def __init__(self, consumer_admin, consumer_id, api_url):
        self.consumer_admin = consumer_admin
        self.consumer_id = consumer_id
        self._store = SimulatorDataStore(api_url or 'http://localhost:8001/consumers/%s/basicauth' % self.consumer_id)

    def destroy(self):
        self.consumer_admin = None
        self.consumer_id = None

        self._store.destroy()
        self._store = None

    def create_or_update(self, basic_auth_id=None, username=None, password=None):
        data = {
            'username': username,
            'password': password
        }

        if basic_auth_id is not None:
            return self.update(basic_auth_id, **data)

        return self.create(**data)

    def create(self, username, password):
        assert username and password

        return self._store.create({
            'username': username,
            'password': password,
            'created_at': timestamp()
        }, check_conflict_keys=('username',))

    def update(self, basic_auth_id, **fields):
        return self._store.update(basic_auth_id, None, fields)

    def list(self, size=100, offset=None, **filter_fields):
        return self._store.list(size=size, offset=offset, **filter_fields)

    def delete(self, basic_auth_id):
        return self._store.delete(basic_auth_id, None)

    def retrieve(self, basic_auth_id):
        return self._store.retrieve(basic_auth_id, None)

    def count(self):
        return self._store.count()


class KeyAuthAdminSimulator(KeyAuthAdminContract):
    def __init__(self, consumer_admin, consumer_id, api_url):
        self.consumer_admin = consumer_admin
        self.consumer_id = consumer_id
        self._store = SimulatorDataStore(api_url or 'http://localhost:8001/consumers/%s/keyauth' % self.consumer_id)

    def destroy(self):
        self.consumer_admin = None
        self.consumer_id = None

        self._store.destroy()
        self._store = None

    def create_or_update(self, key_auth_id=None, key=None):
        data = {
            'key': key or self._generate_key()
        }

        if key_auth_id is not None:
            return self.update(key_auth_id, **data)

        return self.create(**data)

    def create(self, key=None):
        return self._store.create({
            'key': key or self._generate_key(),
            'created_at': timestamp()
        }, check_conflict_keys=('key',))

    def update(self, key_auth_id, **fields):
        return self._store.update(key_auth_id, None, fields)

    def list(self, size=100, offset=None, **filter_fields):
        return self._store.list(size=size, offset=offset, **filter_fields)

    def delete(self, key_auth_id):
        return self._store.delete(key_auth_id, None)

    def retrieve(self, key_auth_id):
        return self._store.retrieve(key_auth_id, None)

    def count(self):
        return self._store.count()

    def _generate_key(self):
        data = str(uuid.uuid4()).encode('utf-8')

        m = hashlib.sha1()
        m.update(data)
        return m.hexdigest()


class OAuth2AdminSimulator(OAuth2AdminContract):
    def __init__(self, consumer_admin, consumer_id, api_url):
        self.consumer_admin = consumer_admin
        self.consumer_id = consumer_id
        self._store = SimulatorDataStore(api_url or 'http://localhost:8001/consumers/%s/oauth2' % self.consumer_id)

    def destroy(self):
        self.consumer_admin = None
        self.consumer_id = None

        self._store.destroy()
        self._store = None

    def create_or_update(self, oauth2_id=None, name=None, redirect_uri=None, client_id=None, client_secret=None):
        data = {
            'name': name,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }

        if oauth2_id is not None:
            return self.update(oauth2_id, **data)

        return self.create(**data)

    def create(self, name, redirect_uri, client_id=None, client_secret=None):
        assert name and redirect_uri

        return self._store.create({
            'name': name,
            'redirect_uri': redirect_uri,
            'created_at': timestamp()
        }, check_conflict_keys=('name', 'redirect_uri'))

    def update(self, oauth2_id, **fields):
        return self._store.update(oauth2_id, None, fields)

    def list(self, size=100, offset=None, **filter_fields):
        return self._store.list(size=size, offset=offset, **filter_fields)

    def delete(self, oauth2_id):
        return self._store.delete(oauth2_id, None)

    def retrieve(self, oauth2_id):
        return self._store.retrieve(oauth2_id, None)

    def count(self):
        return self._store.count()


class ConsumerAdminSimulator(ConsumerAdminContract):
    def __init__(self, api_url=None):
        self._store = SimulatorDataStore(
            api_url or 'http://localhost:8001/consumers/',
            data_struct_filter={
                'custom_id': None,
                'username': None
            })
        self._basic_auth_admins = {}
        self._key_auth_admins = {}
        self._oauth2_admins = {}

    def destroy(self):
        self._store.destroy()
        self._store = None

        for related_admin in (self._basic_auth_admins, self._key_auth_admins, self._oauth2_admins):
            for key in related_admin:
                related_admin[key].destroy()
                del related_admin[key]

        self._basic_auth_admins = None
        self._key_auth_admins = None
        self._oauth2_admins = None

    def count(self):
        return self._store.count()

    def create(self, username=None, custom_id=None):
        assert username or custom_id

        return self._store.create({
            'username': username,
            'custom_id': custom_id,
            'created_at': timestamp()
        }, check_conflict_keys=('username', 'custom_id'))

    def create_or_update(self, consumer_id=None, username=None, custom_id=None):
        data = {
            'username': username,
            'custom_id': custom_id
        }

        if consumer_id is not None:
            return self.update(consumer_id, **data)

        return self.create(**data)

    def update(self, username_or_id, **fields):
        return self._store.update(username_or_id, 'username', fields)

    def retrieve(self, username_or_id):
        return self._store.retrieve(username_or_id, 'username')

    def list(self, size=100, offset=None, **filter_fields):
        return self._store.list(size, offset, **filter_fields)

    def delete(self, username_or_id):
        consumer_id = self.retrieve(username_or_id).get('id')

        if consumer_id is None:
            raise ValueError('Unknown username_or_id: %s' % username_or_id)

        if consumer_id in self._basic_auth_admins:
            self._basic_auth_admins[consumer_id].consumer_admin = None
            del self._basic_auth_admins[consumer_id]

        if consumer_id in self._oauth2_admins:
            self._oauth2_admins[consumer_id].consumer_admin = None
            del self._oauth2_admins[consumer_id]

        return self._store.delete(username_or_id, 'username')

    def basic_auth(self, username_or_id):
        consumer_id = self.retrieve(username_or_id).get('id')

        if consumer_id is None:
            raise ValueError('Unknown username_or_id: %s' % username_or_id)

        if consumer_id not in self._basic_auth_admins:
            self._basic_auth_admins[consumer_id] = BasicAuthAdminSimulator(self, consumer_id, self._store.api_url)

        return self._basic_auth_admins[consumer_id]

    def key_auth(self, username_or_id):
        consumer_id = self.retrieve(username_or_id).get('id')

        if consumer_id is None:
            raise ValueError('Unknown username_or_id: %s' % username_or_id)

        if consumer_id not in self._key_auth_admins:
            self._key_auth_admins[consumer_id] = KeyAuthAdminSimulator(self, consumer_id, self._store.api_url)

        return self._key_auth_admins[consumer_id]

    def oauth2(self, username_or_id):
        consumer_id = self.retrieve(username_or_id).get('id')

        if consumer_id is None:
            raise ValueError('Unknown username_or_id: %s' % username_or_id)

        if consumer_id not in self._oauth2_admins:
            self._oauth2_admins[consumer_id] = OAuth2AdminSimulator(self, consumer_id, self._store.api_url)

        return self._oauth2_admins[consumer_id]


class PluginAdminSimulator(PluginAdminContract):
    # Copied from real kong server, v0.4.0
    PLUGINS = OrderedDict({
        'ssl': {'fields': {'_cert_der_cache': {'type': 'string', 'immutable': True},
                           'cert': {'required': True, 'type': 'string', 'func': 'function'},
                           'key': {'required': True, 'type': 'string', 'func': 'function'},
                           'only_https': {'default': False, 'required': False, 'type': 'boolean'},
                           '_key_der_cache': {'type': 'string', 'immutable': True}}, 'no_consumer': True},
        'key-authentication': {'fields': {'key_names': {'default': 'function', 'required': True, 'type': 'array'},
                                          'hide_credentials': {'default': False, 'type': 'boolean'}}},
        'basic-authentication': {'fields': {'hide_credentials': {'default': False, 'type': 'boolean'}}},
        'oauth2-authentication': {'fields': {'scopes': {'required': False, 'type': 'array'},
                                             'token_expiration': {'default': 7200, 'required': True, 'type': 'number'},
                                             'enable_implicit_grant': {
                                                 'default': False, 'required': True, 'type': 'boolean'},
                                             'hide_credentials': {'default': False, 'type': 'boolean'},
                                             'provision_key': {
                                                 'unique': True, 'type': 'string', 'func': 'function',
                                                 'required': False},
                                             'mandatory_scope': {
                                                 'default': False, 'required': True, 'type': 'boolean', 'func':
                                                     'function'}}},
        'rate-limiting': {
            'fields': {'hour': {'type': 'number'}, 'month': {'type': 'number'}, 'second': {'type': 'number'},
                       'year': {'type': 'number'}, 'day': {'type': 'number'}, 'minute': {'type': 'number'}},
            'self_check': 'function'},
        'tcp-log': {
            'fields': {'host': {'required': True, 'type': 'string'}, 'port': {'required': True, 'type': 'number'},
                       'timeout': {'default': 10000, 'type': 'number'},
                       'keepalive': {'default': 60000, 'type': 'number'}}},
        'udp-log': {
            'fields': {'host': {'required': True, 'type': 'string'}, 'port': {'required': True, 'type': 'number'},
                       'timeout': {'default': 10000, 'type': 'number'}}},
        'file-log': {'fields': {'path': {'required': True, 'type': 'string', 'func': 'function'}}},
        'http-log': {'fields': {'http_endpoint': {'required': True, 'type': 'url'},
                                'method': {'default': 'POST', 'enum': ['POST', 'PUT', 'PATCH']},
                                'timeout': {'default': 10000, 'type': 'number'},
                                'keepalive': {'default': 60000, 'type': 'number'}}},
        'cors': {'fields': {'origin': {'type': 'string'}, 'max_age': {'type': 'number'},
                            'exposed_headers': {'type': 'array'},
                            'methods': {'enum': ['HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'], 'type': 'array'},
                            'headers': {'type': 'array'}, 'preflight_continue': {'default': False, 'type': 'boolean'},
                            'credentials': {'default': False, 'type': 'boolean'}}},
        'request-transformer': {'fields': {'origin': {'type': 'string'}, 'max_age': {'type': 'number'},
                                           'exposed_headers': {'type': 'array'},
                                           'methods': {'enum': ['HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                                                       'type': 'array'}, 'headers': {'type': 'array'},
                                           'preflight_continue': {'default': False, 'type': 'boolean'},
                                           'credentials': {'default': False, 'type': 'boolean'}}},
        'response-transformer': {'fields': {
            'add': {'type': 'table', 'schema': {'fields': {'headers': {'type': 'array'}, 'json': {'type': 'array'}}}},
            'remove': {'type': 'table',
                       'schema': {'fields': {'headers': {'type': 'array'}, 'json': {'type': 'array'}}}}}},
        'request-size-limiting': {'fields': {'allowed_payload_size': {'default': 128, 'type': 'number'}}}
    })

    def destroy(self):
        pass

    def list(self):
        return {
            'enabled_plugins': self.PLUGINS.keys()
        }

    def retrieve_schema(self, plugin_name):
        return self.PLUGINS.get(plugin_name)


class KongAdminSimulator(KongAdminContract):
    def __init__(self, api_url=None):
        super(KongAdminSimulator, self).__init__(
            apis=APIAdminSimulator(api_url=api_url),
            consumers=ConsumerAdminSimulator(api_url=api_url),
            plugins=PluginAdminSimulator())

    def close(self):
        self.apis.destroy()
        self.consumers.destroy()
        self.plugins.destroy()
