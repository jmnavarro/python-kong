# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from collections import OrderedDict
import uuid

from .contract import KongAdminContract, APIAdminContract, ConsumerAdminContract, PluginConfigurationAdminContract
from .utils import timestamp, uuid_or_string, add_url_params, filter_api_struct, filter_dict_list, assert_dict_keys_in, \
    ensure_trailing_slash
from .exceptions import ConflictError


class SimulatorDataStore(object):
    def __init__(self, base_url, data_struct_filter=None):
        self._base_url = base_url
        self._data_struct_filter = data_struct_filter or {}
        self._data = OrderedDict()

    def count(self):
        return len(self._data)

    def create(self, data_struct):
        assert 'id' not in data_struct

        # Prevent conflicts
        errors = []
        for key in ('name', 'target_url'):
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

        offset_index = self._data.keys().index(uuid_or_string(offset))
        sliced_data = data_list[offset_index:size]

        next_url = None
        next_index = offset_index + size + 1
        if next_index < len(data_list):
            next_offset = data_list[next_index]['id']
            next_url = add_url_params(self._base_url, {
                'size': size,
                'offset': next_offset
            })

        result = {
            'total': len(sliced_data),
            'data': sliced_data,
            'next': next_url
        }

        return result

    def delete(self, value_or_id, key):
        value_or_id = uuid_or_string(value_or_id)

        if value_or_id in self._data:
            del self._data[value_or_id]

        for id in self._data:
            if self._data[id][key] == value_or_id:
                del self._data[id]
                break

    def clear(self):
        self._data = OrderedDict()

    def _get_by_field(self, field, value):
        for data_struct in self._data.values():
            if data_struct[field] == value:
                return data_struct


class APIAdminSimulator(APIAdminContract):
    def __init__(self, base_url=None):
        self._store = SimulatorDataStore(
            base_url or 'http://localhost:8001/apis/',
            data_struct_filter={
                'public_dns': None,
                'path': None,
                'strip_path': False
            })

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
        })

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
        return self._store.delete(name_or_id, 'name')

    def clear(self):
        self._store.clear()


class ConsumerAdminSimulator(ConsumerAdminContract):
    def __init__(self, base_url=None):
        self._store = SimulatorDataStore(
            base_url or 'http://localhost:8001/consumers/',
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
        })

    def update(self, username_or_id, **fields):
        return self._store.update(username_or_id, 'username', **fields)

    def retrieve(self, username_or_id):
        return self._store.retrieve(username_or_id, 'username')

    def list(self, size=100, offset=None, **filter_fields):
        return self._store.list(size, offset, **filter_fields)

    def delete(self, username_or_id):
        return self._store.delete(username_or_id, 'username')

    def clear(self):
        self._store.clear()


class PluginConfigurationAdminSimulator(PluginConfigurationAdminContract):
    def create(self, api_name_or_id, name, value, consumer_id=None):
        return super(PluginConfigurationAdminSimulator, self).create(api_name_or_id, name, value, consumer_id)

    def list(self, size=100, offset=None, **filter_fields):
        return super(PluginConfigurationAdminSimulator, self).list(size, offset, **filter_fields)

    def delete(self, api_name_or_id, plugin_configuration_name_or_id):
        super(PluginConfigurationAdminSimulator, self).delete(api_name_or_id, plugin_configuration_name_or_id)

    def update(self, api_name_or_id, plugin_configuration_name_or_id, name, value, **fields):
        return super(PluginConfigurationAdminSimulator, self).update(api_name_or_id, plugin_configuration_name_or_id,
                                                                     name, value, **fields)


class KongAdminSimulator(KongAdminContract):
    def __init__(self):
        super(KongAdminSimulator, self).__init__(
            apis=APIAdminSimulator(),
            consumers=ConsumerAdminSimulator(),
            plugin_configurations=PluginConfigurationAdminSimulator())
