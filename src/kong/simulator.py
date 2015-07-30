# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import uuid

from .contract import KongAdminContract, APIPluginConfigurationAdminContract, APIAdminContract, ConsumerAdminContract, \
    PluginAdminContract
from .utils import timestamp, uuid_or_string, add_url_params, filter_api_struct, filter_dict_list, assert_dict_keys_in, \
    ensure_trailing_slash
from .compat import OrderedDict
from .exceptions import ConflictError


class SimulatorDataStore(object):
    def __init__(self, api_url, data_struct_filter=None):
        self.api_url = api_url
        self._data_struct_filter = data_struct_filter or {}
        self._data = OrderedDict()

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

        for id in self._data:
            if self._data[id][key] == value_or_id:
                self._data[id].update(data_struct_update)
                return filter_api_struct(self._data[id], self._data_struct_filter)

    def retrieve(self, value_or_id, key):
        value_or_id = uuid_or_string(value_or_id)

        if value_or_id in self._data:
            return filter_api_struct(self._data[value_or_id], self._data_struct_filter)

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
            'value': fields,
            'created_at': timestamp(),
            'enabled': True if enabled is None else enabled
        }

        if consumer_id is not None:
            self._data[plugin_name]['consumer_id'] = consumer_id

        return self._data[plugin_name]

    def create_or_update(self, plugin_name, plugin_configuration_id=None, enabled=None, consumer_id=None, **fields):
        if plugin_configuration_id is not None:
            current_plugin_name = None
            for obj in self._data.values():
                if obj['id'] == plugin_configuration_id:
                    current_plugin_name = obj['name']
                    break
            assert current_plugin_name is not None
            return self.update(current_plugin_name, enabled=enabled, consumer_id=consumer_id, **fields)
        return self.create(plugin_name, enabled=enabled, consumer_id=consumer_id, **fields)

    def update(self, plugin_name, enabled=None, consumer_id=None, **fields):
        current_plugin_id = None
        current_plugin_name = None

        for obj in self._data.values():
            if obj['name'] == plugin_name:
                current_plugin_id = obj['id']
                current_plugin_name = obj['name']
                break

        if current_plugin_name is None or current_plugin_id is None:
            raise ValueError('Unknown plugin_name: %s' % plugin_name)

        if current_plugin_name not in PluginAdminSimulator.PLUGINS.keys():
            raise ValueError('Unknown plugin_name: %s' % current_plugin_name)

        for key in fields:
            if key not in PluginAdminSimulator.PLUGINS[current_plugin_name]['fields']:
                raise ValueError('Unknown value field "%s" for plugin: %s' % (key, current_plugin_name))

        data_struct_update = {
            'name': plugin_name,
            'value': fields
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

    def delete(self, plugin_name_or_id):
        plugin_name_or_id = uuid_or_string(plugin_name_or_id)

        if plugin_name_or_id in self._data:
            del self._data[plugin_name_or_id]

        for plugin_name in self._data:
            if self._data[plugin_name]['id'] == plugin_name_or_id:
                del self._data[plugin_name]
                break

    def count(self):
        return len(self._data.keys())


class APIAdminSimulator(APIAdminContract):
    def __init__(self, api_url=None):
        self._store = SimulatorDataStore(
            api_url or 'http://localhost:8001/apis/',
            data_struct_filter={
                'public_dns': None,
                'path': None,
                'strip_path': False
            })
        self._plugin_admins = {}

    def count(self):
        return self._store.count()

    def add(self, target_url, name=None, public_dns=None, path=None, strip_path=False):
        assert target_url is not None
        assert public_dns or path

        # ensure trailing slash
        target_url = ensure_trailing_slash(target_url)

        return self._store.create({
            'name': name or public_dns,
            'public_dns': public_dns,
            'path': path,
            'target_url': target_url,
            'strip_path': strip_path,
            'created_at': timestamp()
        }, check_conflict_keys=('name', 'public_dns'))

    def add_or_update(self, target_url, api_id=None, name=None, public_dns=None, path=None, strip_path=False):
        data = {
            'name': name or public_dns,
            'public_dns': public_dns,
            'path': path,
            'target_url': target_url,
            'strip_path': strip_path
        }

        if api_id is not None:
            return self.update(api_id, **data)

        return self.add(**data)

    def update(self, name_or_id, target_url, **fields):
        # ensure trailing slash
        target_url = ensure_trailing_slash(target_url)

        return self._store.update(name_or_id, 'name', dict({
            'target_url': target_url
        }, **fields))

    def retrieve(self, name_or_id):
        return self._store.retrieve(name_or_id, 'name')

    def list(self, size=100, offset=None, **filter_fields):
        assert_dict_keys_in(filter_fields, ['id', 'name', 'public_dns', 'target_url'])
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


class ConsumerAdminSimulator(ConsumerAdminContract):
    def __init__(self, api_url=None):
        self._store = SimulatorDataStore(
            api_url or 'http://localhost:8001/consumers/',
            data_struct_filter={
                'custom_id': None,
                'username': None
            })

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
        return self._store.delete(username_or_id, 'username')


class PluginAdminSimulator(PluginAdminContract):
    # Copied from real kong server, v0.4.0
    PLUGINS = OrderedDict({
        'ssl': {'fields': {'_cert_der_cache': {'type': 'string', 'immutable': True},
                           'cert': {'required': True, 'type': 'string', 'func': 'function'},
                           'key': {'required': True, 'type': 'string', 'func': 'function'},
                           'only_https': {'default': False, 'required': False, 'type': 'boolean'},
                           '_key_der_cache': {'type': 'string', 'immutable': True}}, 'no_consumer': True},
        'keyauth': {'fields': {'key_names': {'default': 'function', 'required': True, 'type': 'array'},
                               'hide_credentials': {'default': False, 'type': 'boolean'}}},
        'basicauth': {'fields': {'hide_credentials': {'default': False, 'type': 'boolean'}}},
        'oauth2': {'fields': {'scopes': {'required': False, 'type': 'array'},
                              'token_expiration': {'default': 7200, 'required': True, 'type': 'number'},
                              'enable_implicit_grant': {'default': False, 'required': True, 'type': 'boolean'},
                              'hide_credentials': {'default': False, 'type': 'boolean'},
                              'provision_key': {'unique': True, 'type': 'string', 'func': 'function',
                                                'required': False},
                              'mandatory_scope': {'default': False, 'required': True, 'type': 'boolean',
                                                  'func': 'function'}}},
        'ratelimiting': {
            'fields': {'hour': {'type': 'number'}, 'month': {'type': 'number'}, 'second': {'type': 'number'},
                       'year': {'type': 'number'}, 'day': {'type': 'number'}, 'minute': {'type': 'number'}},
            'self_check': 'function'},
        'tcplog': {
            'fields': {'host': {'required': True, 'type': 'string'}, 'port': {'required': True, 'type': 'number'},
                       'timeout': {'default': 10000, 'type': 'number'},
                       'keepalive': {'default': 60000, 'type': 'number'}}},
        'udplog': {
            'fields': {'host': {'required': True, 'type': 'string'}, 'port': {'required': True, 'type': 'number'},
                       'timeout': {'default': 10000, 'type': 'number'}}},
        'filelog': {'fields': {'path': {'required': True, 'type': 'string', 'func': 'function'}}},
        'httplog': {'fields': {'http_endpoint': {'required': True, 'type': 'url'},
                               'method': {'default': 'POST', 'enum': ['POST', 'PUT', 'PATCH']},
                               'timeout': {'default': 10000, 'type': 'number'},
                               'keepalive': {'default': 60000, 'type': 'number'}}},
        'cors': {'fields': {'origin': {'type': 'string'}, 'max_age': {'type': 'number'},
                            'exposed_headers': {'type': 'array'},
                            'methods': {'enum': ['HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'], 'type': 'array'},
                            'headers': {'type': 'array'}, 'preflight_continue': {'default': False, 'type': 'boolean'},
                            'credentials': {'default': False, 'type': 'boolean'}}},
        'request_transformer': {'fields': {'origin': {'type': 'string'}, 'max_age': {'type': 'number'},
                                           'exposed_headers': {'type': 'array'},
                                           'methods': {'enum': ['HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                                                       'type': 'array'}, 'headers': {'type': 'array'},
                                           'preflight_continue': {'default': False, 'type': 'boolean'},
                                           'credentials': {'default': False, 'type': 'boolean'}}},
        'response_transformer': {'fields': {
            'add': {'type': 'table', 'schema': {'fields': {'headers': {'type': 'array'}, 'json': {'type': 'array'}}}},
            'remove': {'type': 'table',
                       'schema': {'fields': {'headers': {'type': 'array'}, 'json': {'type': 'array'}}}}}},
        'requestsizelimiting': {'fields': {'allowed_payload_size': {'default': 128, 'type': 'number'}}}
    })

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
