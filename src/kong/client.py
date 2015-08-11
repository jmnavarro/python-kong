# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os
import time
import logging
import requests
import backoff

from requests.adapters import HTTPAdapter

from .contract import KongAdminContract, APIAdminContract, ConsumerAdminContract, PluginAdminContract, \
    APIPluginConfigurationAdminContract, BasicAuthAdminContract
from .utils import add_url_params, assert_dict_keys_in, ensure_trailing_slash
from .compat import OK, CREATED, NO_CONTENT, NOT_FOUND, CONFLICT, urljoin
from .exceptions import ConflictError

logger = logging.getLogger(__name__)

KONG_MINIMUM_REQUEST_INTERVAL = float(os.getenv('KONG_MINIMUM_REQUEST_INTERVAL', 0))

if KONG_MINIMUM_REQUEST_INTERVAL > 0:
    logger.warn('Requests will be throttled: KONG_MINIMUM_REQUEST_INTERVAL = %s' % KONG_MINIMUM_REQUEST_INTERVAL)


def raise_response_error(response, exception_class=None, is_json=True):
    exception_class = exception_class or ValueError
    assert issubclass(exception_class, BaseException)
    if is_json:
        raise exception_class(', '.join(['%s: %s' % (key, value) for (key, value) in response.json().items()]))
    raise exception_class(str(response))


class ThrottlingHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        super(ThrottlingHTTPAdapter, self).__init__(*args, **kwargs)
        self._last_request = None

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        if self._last_request is not None and KONG_MINIMUM_REQUEST_INTERVAL > 0:
            diff = time.time() - self._last_request
            if 0 < diff < KONG_MINIMUM_REQUEST_INTERVAL:
                logger.warn('Waiting %s seconds before sending request' % diff)
                time.sleep(diff)
        result = super(ThrottlingHTTPAdapter, self).send(request, stream, timeout, verify, cert, proxies)
        self._last_request = time.time()
        return result


class RestClient(object):
    def __init__(self, api_url):
        self.api_url = api_url
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = requests.session()
            self._session.mount(self.api_url, ThrottlingHTTPAdapter())
        return self._session

    def get_url(self, *path, **query_params):
        url = ensure_trailing_slash(urljoin(self.api_url, '/'.join(path)))
        return add_url_params(url, query_params)


class APIPluginConfigurationAdminClient(APIPluginConfigurationAdminContract, RestClient):
    def __init__(self, api_admin, api_name_or_id, api_url):
        super(APIPluginConfigurationAdminClient, self).__init__(api_url)

        self.api_admin = api_admin
        self.api_name_or_id = api_name_or_id

    def create(self, plugin_name, enabled=None, consumer_id=None, **fields):
        values = {}
        for key in fields:
            values['value.%s' % key] = fields[key]

        data = dict({
            'name': plugin_name,
            'consumer_id': consumer_id,
        }, **values)

        if enabled is not None and isinstance(enabled, bool):
            data['enabled'] = enabled

        response = self.session.post(self.get_url('apis', self.api_name_or_id, 'plugins'), data=data)
        result = response.json()
        if response.status_code == CONFLICT:
            raise_response_error(response, ConflictError)
        elif response.status_code != CREATED:
            raise_response_error(response, ValueError)

        return result

    def create_or_update(self, plugin_name, plugin_configuration_id=None, enabled=None, consumer_id=None, **fields):
        values = {}
        for key in fields:
            values['value.%s' % key] = fields[key]

        data = dict({
            'name': plugin_name,
            'consumer_id': consumer_id,
        }, **values)

        if enabled is not None and isinstance(enabled, bool):
            data['enabled'] = enabled

        if plugin_configuration_id is not None:
            data['id'] = plugin_configuration_id

        response = self.session.put(self.get_url('apis', self.api_name_or_id, 'plugins'), data=data)
        result = response.json()
        if response.status_code == CONFLICT:
            raise_response_error(response, ConflictError)
        elif response.status_code not in (CREATED, OK):
            raise_response_error(response, ValueError)

        return result

    def update(self, plugin_name, enabled=None, consumer_id=None, **fields):
        values = {}
        for key in fields:
            values['value.%s' % key] = fields[key]

        data_struct_update = dict({
            'name': plugin_name,
        }, **values)

        if consumer_id is not None:
            data_struct_update['consumer_id'] = consumer_id

        if enabled is not None and isinstance(enabled, bool):
            data_struct_update['enabled'] = enabled

        url = self.get_url('apis', self.api_name_or_id, 'plugins', plugin_name)

        response = self.session.patch(url, data=data_struct_update)
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result

    def list(self, size=100, offset=None, **filter_fields):
        assert_dict_keys_in(filter_fields, ['id', 'name', 'api_id', 'consumer_id'])

        query_params = filter_fields
        query_params['size'] = size

        if offset is not None:
            query_params['offset'] = offset

        url = self.get_url('apis', self.api_name_or_id, 'plugins', **query_params)
        response = self.session.get(url)
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result

    @backoff.on_exception(backoff.expo, ValueError, max_tries=3)
    def delete(self, plugin_name_or_id):
        response = self.session.delete(self.get_url('apis', self.api_name_or_id, 'plugins', plugin_name_or_id))

        if response.status_code not in (NO_CONTENT, NOT_FOUND):
            raise ValueError('Could not delete Plugin Configuration (status: %s): %s' % (
                response.status_code, plugin_name_or_id))

    def count(self):
        response = self.session.get(self.get_url('apis', self.api_name_or_id, 'plugins'))
        result = response.json()
        amount = result.get('total', len(result.get('data')))
        return amount


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
            'public_dns': public_dns or None,  # Empty strings are not allowed
            'path': path or None,  # Empty strings are not allowed
            'strip_path': strip_path,
            'target_url': target_url
        })
        result = response.json()
        if response.status_code == CONFLICT:
            raise_response_error(response, ConflictError)
        elif response.status_code != CREATED:
            raise_response_error(response, ValueError)

        return result

    def add_or_update(self, target_url, api_id=None, name=None, public_dns=None, path=None, strip_path=False):
        data = {
            'name': name,
            'public_dns': public_dns or None,  # Empty strings are not allowed
            'path': path or None,  # Empty strings are not allowed
            'strip_path': strip_path,
            'target_url': target_url
        }

        if api_id is not None:
            data['id'] = api_id

        response = self.session.put(self.get_url('apis'), data=data)
        result = response.json()
        if response.status_code == CONFLICT:
            raise_response_error(response, ConflictError)
        elif response.status_code not in (CREATED, OK):
            raise_response_error(response, ValueError)

        return result

    def update(self, name_or_id, target_url, **fields):
        assert_dict_keys_in(fields, ['name', 'public_dns', 'path', 'strip_path'])
        response = self.session.patch(self.get_url('apis', name_or_id), data=dict({
            'target_url': target_url
        }, **fields))
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result

    @backoff.on_exception(backoff.expo, ValueError, max_tries=3)
    def delete(self, name_or_id):
        response = self.session.delete(self.get_url('apis', name_or_id))

        if response.status_code not in (NO_CONTENT, NOT_FOUND):
            raise ValueError('Could not delete API (status: %s): %s' % (response.status_code, name_or_id))

    def retrieve(self, name_or_id):
        response = self.session.get(self.get_url('apis', name_or_id))
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result

    def list(self, size=100, offset=None, **filter_fields):
        assert_dict_keys_in(filter_fields, ['id', 'name', 'public_dns', 'path'])

        query_params = filter_fields
        query_params['size'] = size

        if offset:
            query_params['offset'] = offset

        url = self.get_url('apis', **query_params)
        response = self.session.get(url)
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result

    def plugins(self, name_or_id):
        return APIPluginConfigurationAdminClient(self, name_or_id, self.api_url)


class BasicAuthAdminClient(BasicAuthAdminContract, RestClient):
    def __init__(self, consumer_admin, consumer_id, api_url):
        super(BasicAuthAdminClient, self).__init__(api_url)

        self.consumer_admin = consumer_admin
        self.consumer_id = consumer_id

    def create_or_update(self, basic_auth_id=None, username=None, password=None):
        data = {
            'username': username,
            'password': password,
        }

        if basic_auth_id is not None:
            data['id'] = basic_auth_id

        response = self.session.put(self.get_url('consumers', self.consumer_id, 'basicauth'), data=data)
        result = response.json()
        if response.status_code == CONFLICT:
            raise_response_error(response, ConflictError)
        elif response.status_code not in (CREATED, OK):
            raise_response_error(response, ValueError)

        return result

    def create(self, username, password):
        response = self.session.post(self.get_url('consumers', self.consumer_id, 'basicauth'), data={
            'username': username,
            'password': password,
        })
        result = response.json()
        if response.status_code == CONFLICT:
            raise_response_error(response, ConflictError)
        elif response.status_code != CREATED:
            raise_response_error(response, ValueError)

        return result

    def list(self, size=100, offset=None, **filter_fields):
        assert_dict_keys_in(filter_fields, ['id', 'username'])

        query_params = filter_fields
        query_params['size'] = size

        if offset:
            query_params['offset'] = offset

        url = self.get_url('consumers', self.consumer_id, 'basicauth', **query_params)
        response = self.session.get(url)
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result

    @backoff.on_exception(backoff.expo, ValueError, max_tries=3)
    def delete(self, basic_auth_id):
        url = self.get_url('consumers', self.consumer_id, 'basicauth', basic_auth_id)
        response = self.session.delete(url)

        if response.status_code not in (NO_CONTENT, NOT_FOUND):
            raise ValueError('Could not delete Basic Auth (status: %s): %s for Consumer: %s' % (
                response.status_code, basic_auth_id, self.consumer_id))

    def retrieve(self, basic_auth_id):
        response = self.session.get(self.get_url('consumers', self.consumer_id, 'basicauth', basic_auth_id))
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result

    def count(self):
        response = self.session.get(self.get_url('consumers', self.consumer_id, 'basicauth'))
        result = response.json()
        amount = result.get('total', len(result.get('data')))
        return amount

    def update(self, basic_auth_id, **fields):
        assert_dict_keys_in(fields, ['username', 'password'])
        response = self.session.patch(
            self.get_url('consumers', self.consumer_id, 'basicauth', basic_auth_id), data=fields)
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result


class ConsumerAdminClient(ConsumerAdminContract, RestClient):
    def __init__(self, api_url):
        super(ConsumerAdminClient, self).__init__(api_url)

    def count(self):
        response = self.session.get(self.get_url('consumers'))
        result = response.json()
        amount = result.get('total', len(result.get('data')))
        return amount

    def create(self, username=None, custom_id=None):
        response = self.session.post(self.get_url('consumers'), data={
            'username': username,
            'custom_id': custom_id,
        })
        result = response.json()
        if response.status_code == CONFLICT:
            raise_response_error(response, ConflictError)
        elif response.status_code != CREATED:
            raise_response_error(response, ValueError)

        return result

    def create_or_update(self, consumer_id=None, username=None, custom_id=None):
        data = {
            'username': username,
            'custom_id': custom_id,
        }

        if consumer_id is not None:
            data['id'] = consumer_id

        response = self.session.put(self.get_url('consumers'), data=data)
        result = response.json()
        if response.status_code == CONFLICT:
            raise_response_error(response, ConflictError)
        elif response.status_code not in (CREATED, OK):
            raise_response_error(response, ValueError)

        return result

    def update(self, username_or_id, **fields):
        assert_dict_keys_in(fields, ['username', 'custom_id'])
        response = self.session.patch(self.get_url('consumers', username_or_id), data=fields)
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result

    def list(self, size=100, offset=None, **filter_fields):
        assert_dict_keys_in(filter_fields, ['id', 'custom_id', 'username'])

        query_params = filter_fields
        query_params['size'] = size

        if offset:
            query_params['offset'] = offset

        url = self.get_url('consumers', **query_params)
        response = self.session.get(url)
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result

    @backoff.on_exception(backoff.expo, ValueError, max_tries=3)
    def delete(self, username_or_id):
        response = self.session.delete(self.get_url('consumers', username_or_id))

        if response.status_code not in (NO_CONTENT, NOT_FOUND):
            raise ValueError('Could not delete Consumer (status: %s): %s' % (response.status_code, username_or_id))

    def retrieve(self, username_or_id):
        response = self.session.get(self.get_url('consumers', username_or_id))
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result

    def basic_auth(self, username_or_id):
        return BasicAuthAdminClient(self, username_or_id, self.api_url)


class PluginAdminClient(PluginAdminContract, RestClient):
    def list(self):
        response = self.session.get(self.get_url('plugins'))
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result

    def retrieve_schema(self, plugin_name):
        response = self.session.get(self.get_url('plugins', plugin_name, 'schema'))
        result = response.json()

        if response.status_code != OK:
            raise_response_error(response, ValueError)

        return result


class KongAdminClient(KongAdminContract):
    def __init__(self, api_url):
        super(KongAdminClient, self).__init__(
            apis=APIAdminClient(api_url),
            consumers=ConsumerAdminClient(api_url),
            plugins=PluginAdminClient(api_url))
