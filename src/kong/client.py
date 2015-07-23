# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import requests
from urlparse import urljoin
from httplib import OK, CREATED, CONFLICT, NO_CONTENT

from .contract import KongAdminContract, APIAdminContract, ConsumerAdminContract, PluginConfigurationAdminContract
from .utils import add_url_params, assert_dict_keys_in, ensure_trailing_slash
from .exceptions import ConflictError


class RestClient(object):
    def __init__(self, api_url):
        self.api_url = api_url
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = requests.session()
        return self._session

    def get_url(self, *path, **query_params):
        url = ensure_trailing_slash(urljoin(self.api_url, '/'.join(path)))
        return add_url_params(url, query_params)


class APIAdminClient(APIAdminContract, RestClient):
    def __init__(self, api_url):
        super(APIAdminClient, self).__init__(api_url)

    def count(self):
        response = self.session.get(self.get_url('apis'))
        result = response.json()
        amount = result.get('total', len(result.get('data')))
        return amount

    def add(self, target_url, name=None, public_dns=None, path=None, strip_path=False):
        response = self.session.post(self.get_url('apis'), data={
            'name': name,
            'public_dns': public_dns,
            'path': path,
            'strip_path': strip_path,
            'target_url': target_url
        })
        result = response.json()
        if response.status_code == CONFLICT:
            raise ConflictError(', '.join(result.values()))

        assert response.status_code == CREATED

        return result

    def update(self, name_or_id, target_url, **fields):
        assert_dict_keys_in(fields, ['name', 'public_dns', 'path', 'strip_path'])
        response = self.session.patch(self.get_url('apis', name_or_id), data=dict({
            'target_url': target_url
        }, **fields))
        result = response.json()

        assert response.status_code == OK

        return result

    def delete(self, name_or_id):
        response = self.session.delete(self.get_url('apis', name_or_id))

        assert response.status_code == NO_CONTENT

    def retrieve(self, name_or_id):
        response = self.session.get(self.get_url('apis', name_or_id))

        assert response.status_code == OK

        return response.json()

    def list(self, size=100, offset=None, **filter_fields):
        assert_dict_keys_in(filter_fields, ['id', 'name', 'public_dns', 'target_url'])

        query_params = filter_fields
        query_params['size'] = size

        if offset:
            query_params['offset'] = offset

        url = self.get_url('apis', **query_params)
        response = self.session.get(url)

        assert response.status_code == OK

        return response.json()


class ConsumerAdminClient(ConsumerAdminContract, RestClient):
    def __init__(self, api_url):
        super(ConsumerAdminClient, self).__init__(api_url)

    def count(self):
        response = self.session.get(self.get_url('consumers', size=1))
        result = response.json()
        amount = result.get('total', len(result.get('data')))
        return amount

    def create(self, username=None, custom_id=None):
        return super(ConsumerAdminClient, self).create(username, custom_id)

    def list(self, size=100, offset=None, **filter_fields):
        return super(ConsumerAdminClient, self).list(size, offset, **filter_fields)

    def delete(self, username_or_id):
        super(ConsumerAdminClient, self).delete(username_or_id)

    def retrieve(self, username_or_id):
        return super(ConsumerAdminClient, self).retrieve(username_or_id)

    def update(self, username_or_id, **fields):
        return super(ConsumerAdminClient, self).update(username_or_id, **fields)


class PluginConfigurationAdminClient(PluginConfigurationAdminContract, RestClient):
    def __init__(self, api_url):
        super(PluginConfigurationAdminClient, self).__init__(api_url)

    def create(self, api_name_or_id, name, value, consumer_id=None):
        return super(PluginConfigurationAdminClient, self).create(api_name_or_id, name, value, consumer_id)

    def list(self, size=100, offset=None, **filter_fields):
        return super(PluginConfigurationAdminClient, self).list(size, offset, **filter_fields)

    def delete(self, api_name_or_id, plugin_configuration_name_or_id):
        super(PluginConfigurationAdminClient, self).delete(api_name_or_id, plugin_configuration_name_or_id)

    def update(self, api_name_or_id, plugin_configuration_name_or_id, name, value, **fields):
        return super(PluginConfigurationAdminClient, self).update(api_name_or_id, plugin_configuration_name_or_id, name,
                                                                  value, **fields)


class KongAdminClient(KongAdminContract):
    def __init__(self, api_url):
        super(KongAdminClient, self).__init__(
            apis=APIAdminClient(api_url),
            consumers=ConsumerAdminClient(api_url),
            plugin_configurations=PluginConfigurationAdminClient(api_url))
