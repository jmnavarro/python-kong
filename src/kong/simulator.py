# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from collections import OrderedDict
import uuid
import copy

from .contract import KongAdminContract, APIAdminContract, ConsumerAdminContract, PluginConfigurationAdminContract
from .utils import timestamp, uuid_or_string, field_filter, add_url_params


class APIAdminSimulator(APIAdminContract):
    API_STRUCT_FILTER = {
        'public_dns': None,
        'path': None,
        'strip_path': False
    }

    def __init__(self, base_url=None):
        self._base_url = base_url or 'http://localhost:8001/apis/'
        self._apis = OrderedDict()

    def add(self, target_url, name=None, public_dns=None, path=None, strip_path=False):
        assert target_url is not None
        assert public_dns or path

        # Generate a new API id
        api_id = str(uuid.uuid4())

        result = {
            'id': api_id,
            'name': name or public_dns,
            'public_dns': public_dns,
            'path': path,
            'target_url': target_url,
            'strip_path': strip_path,
            'created_at': timestamp()
        }

        self._apis[api_id] = result

        return self._filter_api_struct(result)

    def retrieve(self, name_or_id):
        name_or_id = uuid_or_string(name_or_id)

        if name_or_id in self._apis:
            return self._apis[name_or_id]

        for api_id in self._apis:
            if self._apis[api_id]['name'] == name_or_id:
                return self._filter_api_struct(self._apis[api_id])

    def list(self, id=None, name=None, public_dns=None, target_url=None, size=100, offset=None):
        data = []

        if id is not None:
            return self._apis.get(str(id), None)

        for api_id in self._apis:
            conflict = False

            for key, value in field_filter(name=name, public_dns=public_dns, target_url=target_url):
                if value is not None and self._apis[api_id][key] != value:
                    conflict = True
                    continue

            if conflict:
                continue

            data.append(self._filter_api_struct(self._apis[api_id]))

        offset_index = self._apis.keys().index(uuid_or_string(offset))
        sliced_data = data[offset_index:size]

        next_url = None
        next_index = offset_index + size + 1
        if next_index < len(data):
            next_offset = data[next_index]['id']
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

    def delete(self, name_or_id):
        name_or_id = uuid_or_string(name_or_id)

        if name_or_id in self._apis:
            del self._apis[name_or_id]

        for api_id in self._apis:
            if self._apis[api_id]['name'] == name_or_id:
                del self._apis[name_or_id]
                break

    def update(self, name_or_id, target_url, name=None, public_dns=None, path=None, strip_path=False):
        name_or_id = uuid_or_string(name_or_id)

        new_data = {
            'name': name,
            'public_dns': public_dns,
            'path': path,
            'target_url': target_url,
            'strip_path': strip_path
        }

        if name_or_id in self._apis:
            self._apis[name_or_id].update(new_data)
            return self._filter_api_struct(self._apis[name_or_id])

        for api_id in self._apis:
            if self._apis[api_id]['name'] == name_or_id:
                self._apis[name_or_id].update(new_data)
                return self._filter_api_struct(self._apis[name_or_id])

    def _filter_api_struct(self, api_struct):
        result = copy.copy(api_struct)

        keys_to_remove = []

        for key in APIAdminSimulator.API_STRUCT_FILTER:
            if result[key] == APIAdminSimulator.API_STRUCT_FILTER[key]:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del result[key]

        return result


class ConsumerAdminSimulator(ConsumerAdminContract):
    def create(self, username=None, custom_id=None):
        return super(ConsumerAdminSimulator, self).create(username, custom_id)

    def list(self, id=None, custom_id=None, username=None, size=100, offset=None):
        return super(ConsumerAdminSimulator, self).list(id, custom_id, username, size, offset)

    def delete(self, username_or_id):
        super(ConsumerAdminSimulator, self).delete(username_or_id)

    def retrieve(self, username_or_id):
        return super(ConsumerAdminSimulator, self).retrieve(username_or_id)

    def update(self, username_or_id, username=None, custom_id=None):
        return super(ConsumerAdminSimulator, self).update(username_or_id, username, custom_id)


class PluginConfigurationAdminSimulator(PluginConfigurationAdminContract):
    def create(self, api_name_or_id, name, value, consumer_id=None):
        return super(PluginConfigurationAdminSimulator, self).create(api_name_or_id, name, value, consumer_id)

    def list(self, id=None, name=None, api_id=None, consumer_id=None, size=100, offset=None):
        return super(PluginConfigurationAdminSimulator, self).list(id, name, api_id, consumer_id, size, offset)

    def delete(self, api_name_or_id, plugin_configuration_name_or_id):
        super(PluginConfigurationAdminSimulator, self).delete(api_name_or_id, plugin_configuration_name_or_id)

    def update(self, api_name_or_id, plugin_configuration_name_or_id, name, value, consumer_id=None):
        return super(PluginConfigurationAdminSimulator, self).update(api_name_or_id, plugin_configuration_name_or_id,
                                                                     name, value, consumer_id)


class KongAdminSimulator(KongAdminContract):
    apis = APIAdminSimulator()
    consumers = ConsumerAdminSimulator()
    plugin_configurations = PluginConfigurationAdminSimulator()
