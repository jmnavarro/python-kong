# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from abc import ABCMeta, abstractmethod
import os
import sys
import collections
import requests
import uuid
import json

# To run the standalone test script
if __name__ == '__main__':
    sys.path.append('../src/')

from kong.exceptions import ConflictError
from kong.simulator import KongAdminSimulator
from kong.client import KongAdminClient
from kong.compat import TestCase, skipIf, run_unittests, OrderedDict, urlencode
from kong.utils import uuid_or_string, add_url_params, sorted_ordered_dict

API_URL = os.environ.get('PYKONG_TEST_API_URL', 'http://localhost:8001')

_SESSION = None


def kong_testserver_is_up():
    global _SESSION
    if not _SESSION:
        _SESSION = requests.session()

    try:
        return _SESSION.get(API_URL).status_code == 200
    except IOError:
        return False


class KongAdminTesting(object):
    """
    Important: Do not remove nesting!
    """
    class ClientFactoryMixin(object):
        __metaclass__ = ABCMeta

        @abstractmethod
        def on_create_client(self):
            pass

    class APITestCase(ClientFactoryMixin, TestCase):
        __metaclass__ = ABCMeta

        def setUp(self):
            self.client = self.on_create_client()
            self.assertTrue(self.client.apis.count() == 0)
            self._cleanup = []

        def tearDown(self):
            for name_or_id in set(self._cleanup):
                self.client.apis.delete(name_or_id)
            self.assertEqual(self.client.apis.count(), 0)

        def test_add(self):
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertEqual(self.client.apis.count(), 1)
            self.assertEqual(result['target_url'], 'http://mockbin.com/')
            self.assertEqual(result['name'], 'Mockbin')
            self.assertEqual(result['public_dns'], 'mockbin.com')
            self.assertIsNotNone(result['id'])
            self.assertIsNotNone(result['created_at'])
            self.assertFalse('path' in result)

        def test_add_conflict(self):
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertIsNotNone(result)
            self.assertEqual(self.client.apis.count(), 1)

            result2 = None
            error_thrown = False
            try:
                result2 = self.client.apis.add(
                    target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            except ConflictError:
                error_thrown = True
            self.assertTrue(error_thrown)
            self.assertIsNone(result2)

            self.assertEqual(self.client.apis.count(), 1)

        def test_update(self):
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')

            # Update by name
            result2 = self.client.apis.update('Mockbin', 'http://mockbin.com', path='/someservice', strip_path=True)
            self.assertEqual(result2['id'], result['id'])
            self.assertEqual(result2['path'], '/someservice')
            self.assertEqual(result2['public_dns'], 'mockbin.com')
            self.assertTrue(result2['strip_path'])

            # Update by id
            result3 = self.client.apis.update(
                result['id'], 'http://mockbin2.com', path='/someotherservice', public_dns='example.com')
            self.assertEqual(result3['id'], result['id'])
            self.assertEqual(result3['target_url'], 'http://mockbin2.com/')
            self.assertEqual(result3['path'], '/someotherservice')
            self.assertEqual(result3['public_dns'], 'example.com')
            self.assertTrue(result3['strip_path'])

            # retrieve to check
            result4 = self.client.apis.retrieve(result['id'])
            self.assertIsNotNone(result4)
            self.assertEqual(result4['id'], result['id'])
            self.assertEqual(result4['target_url'], 'http://mockbin2.com/')
            self.assertEqual(result4['path'], '/someotherservice')
            self.assertEqual(result4['public_dns'], 'example.com')
            self.assertTrue(result4['strip_path'])

        def test_retrieve(self):
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertEqual(result['target_url'], 'http://mockbin.com/')
            self.assertEqual(result['name'], 'Mockbin')
            self.assertEqual(result['public_dns'], 'mockbin.com')

            # Retrieve by name
            result2 = self.client.apis.retrieve('Mockbin')
            self.assertEqual(result2, result)

            # Retrieve by id
            result3 = self.client.apis.retrieve(result['id'])
            self.assertEqual(result3, result)
            self.assertEqual(result3, result2)

        def test_list(self):
            amount = 10

            for i in range(amount):
                self.client.apis.add(
                    target_url='http://mockbin%s.com' % i,
                    name=self._cleanup_afterwards('Mockbin%s' % i),
                    public_dns='mockbin%s.com' % i)

            self.assertEqual(self.client.apis.count(), amount)

            result = self.client.apis.list()
            self.assertTrue('data' in result)
            data = result['data']

            self.assertEqual(len(data), amount)

            result = self.client.apis.list(public_dns='mockbin3.com')
            self.assertTrue('data' in result)
            data = result['data']

            self.assertEqual(len(data), 1)

            result = self.client.apis.list(size=3)
            self.assertIsNotNone(result['next'])
            self.assertEqual(len(result['data']), 3)

        def test_iterate(self):
            amount = 10

            for i in range(amount):
                self.client.apis.add(
                    target_url='http://mockbin%s.com' % i,
                    name=self._cleanup_afterwards('Mockbin%s' % i),
                    public_dns='mockbin%s.com' % i)

            found = []

            for item in self.client.apis.iterate(window_size=3):
                found.append(item)

            self.assertEqual(len(found), amount)
            self.assertEqual(
                sorted([item['id'] for item in found]),
                sorted([item['id'] for item in self.client.apis.list().get('data')]))

        def test_iterate_filtered(self):
            amount = 10

            for i in range(amount):
                self.client.apis.add(
                    target_url='http://mockbin%s.com' % i,
                    name=self._cleanup_afterwards('Mockbin%s' % i),
                    public_dns='mockbin%s.com' % i)

            found = []

            for item in self.client.apis.iterate(window_size=3, name='Mockbin3'):
                found.append(item)

            self.assertEqual(len(found), 1)
            self.assertEqual(
                sorted([item['id'] for item in found]),
                sorted([item['id'] for item in self.client.apis.list(name='Mockbin3').get('data')]))

        def test_delete(self):
            result1 = self.client.apis.add(
                target_url='http://mockbin1.com', name='Mockbin1', public_dns='mockbin1.com')
            result2 = self.client.apis.add(
                target_url='http://mockbin2.com', name='Mockbin2', public_dns='mockbin2.com')
            self.assertEqual(self.client.apis.count(), 2)
            self.assertEqual(result1['target_url'], 'http://mockbin1.com/')
            self.assertEqual(result2['target_url'], 'http://mockbin2.com/')

            # Delete by id
            self.client.apis.delete(result1['id'])
            self.assertEqual(self.client.apis.count(), 1)

            # Delete by name
            self.client.apis.delete(result2['name'])
            self.assertEqual(self.client.apis.count(), 0)

        def test_create_global_plugin_configuration(self):
            # Create test api
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertIsNotNone(result)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 0)

            # Create global plugin configuration for the api
            result2 = self.client.apis.plugins('Mockbin').create('ratelimiting', enabled=False, second=20)
            self.assertIsNotNone(result2)
            self.assertIsNotNone(result2['id'])
            self.assertIsNotNone(result2['api_id'])
            self.assertFalse(result2['enabled'])
            self.assertEqual(result2['value']['second'], 20)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 1)

        def test_create_plugin_configuration_conflict(self):
            # Create test api
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertIsNotNone(result)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 0)

            # Create global plugin configuration for the api
            result2 = self.client.apis.plugins('Mockbin').create('ratelimiting', enabled=False, second=20)
            self.assertIsNotNone(result2)
            self.assertIsNotNone(result2['id'])

            result3 = None
            error_thrown = False
            try:
                result3 = self.client.apis.plugins('Mockbin').create('ratelimiting', enabled=False, second=35)
            except ConflictError as e:
                error_thrown = True
            self.assertTrue(error_thrown)
            self.assertIsNone(result3)

        def test_create_non_existing_plugin_configuration(self):
            # Create test api
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertIsNotNone(result)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 0)

            result2 = None
            error_thrown = False
            try:
                result2 = self.client.apis.plugins('Mockbin').create('unknown_plugin', second=20)
            except ValueError:
                error_thrown = True
            self.assertTrue(error_thrown)
            self.assertIsNone(result2)

        def test_create_incorrect_plugin_configuration(self):
            # Create test api
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertIsNotNone(result)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 0)

            result2 = None
            error_thrown = False
            try:
                result2 = self.client.apis.plugins('Mockbin').create('ratelimiting', unknown_parameter=20)
            except ValueError:
                error_thrown = True
            self.assertTrue(error_thrown)
            self.assertIsNone(result2)

        def test_create_consumer_specific_plugin_configuration(self):
            # Create test api
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertIsNotNone(result)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 0)

            # Create test consumer
            consumer = self.client.consumers.create(username='abc1234')

            try:
                # Create consumer specific plugin configuration for the api
                result2 = self.client.apis.plugins('Mockbin').create(
                    'requestsizelimiting', consumer_id=consumer['id'], allowed_payload_size=512)
                self.assertIsNotNone(result2)
                self.assertIsNotNone(result2['consumer_id'])
                self.assertEqual(result2['consumer_id'], consumer['id'])
                self.assertEqual(self.client.apis.plugins('Mockbin').count(), 1)
            finally:
                # Delete the test consumer
                self.client.consumers.delete(consumer['id'])

        def test_update_global_plugin_configuration(self):
            # Create test api
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertIsNotNone(result)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 0)

            # Create global plugin configuration for the api
            result2 = self.client.apis.plugins('Mockbin').create('ratelimiting', enabled=False, second=20)
            self.assertIsNotNone(result2)
            self.assertEqual(result2['enabled'], False)
            self.assertEqual(result2['value']['second'], 20)

            # Update
            result3 = self.client.apis.plugins('Mockbin').update(result2['name'], enabled=True, second=27)
            self.assertIsNotNone(result3)
            self.assertEqual(result3['enabled'], True)
            self.assertEqual(result3['value']['second'], 27)

            # Make sure we still have only 1 configuration
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 1)

        def test_update_incorrect_plugin_configuration(self):
            # Create test api
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertIsNotNone(result)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 0)

            # Create global plugin configuration for the api
            result2 = self.client.apis.plugins('Mockbin').create('ratelimiting', enabled=False, second=20)
            self.assertIsNotNone(result2)
            self.assertEqual(result2['enabled'], False)
            self.assertEqual(result2['value']['second'], 20)

            # Update
            result3 = None
            error_thrown = False
            try:
                result3 = self.client.apis.plugins('Mockbin').update(
                    result2['name'], enabled=True, unknown_parameter=27)
            except ValueError:
                error_thrown = True
            self.assertTrue(error_thrown)
            self.assertIsNone(result3)

            # Make sure we still have only 1 configuration
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 1)

        def test_update_consumer_specific_plugin_configuration(self):
            # Create test api
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertIsNotNone(result)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 0)

            # Create test consumer
            consumer = self.client.consumers.create(username='abc1234')

            try:
                # Create consumer specific plugin configuration for the api
                result2 = self.client.apis.plugins('Mockbin').create(
                    'requestsizelimiting', consumer_id=consumer['id'], allowed_payload_size=512)
                self.assertIsNotNone(result2)
                self.assertIsNotNone(result2['consumer_id'])
                self.assertEqual(result2['consumer_id'], consumer['id'])
                self.assertEqual(self.client.apis.plugins('Mockbin').count(), 1)

                # Update
                result3 = self.client.apis.plugins('Mockbin').update(
                    'requestsizelimiting', consumer_id=consumer['id'], allowed_payload_size=1024)
                self.assertIsNotNone(result3)
                self.assertEqual(result3['enabled'], True)
                self.assertEqual(result3['value']['allowed_payload_size'], 1024)
                self.assertIsNotNone(result3['consumer_id'])
                self.assertEqual(result3['consumer_id'], consumer['id'])

                # Make sure we still have only 1 configuration
                self.assertEqual(self.client.apis.plugins('Mockbin').count(), 1)
            finally:
                # Delete the test consumer
                self.client.consumers.delete(consumer['id'])

        def test_delete_plugin_configuration(self):
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertIsNotNone(result)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 0)

            result2 = self.client.apis.plugins('Mockbin').create('ratelimiting', enabled=False, second=20)
            self.assertIsNotNone(result2)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 1)

            result3 = self.client.apis.plugins('Mockbin').create('requestsizelimiting', allowed_payload_size=512)
            self.assertIsNotNone(result3)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 2)

            # delete by name
            self.client.apis.plugins('Mockbin').delete('ratelimiting')
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 1)

            # delete by id
            self.client.apis.plugins('Mockbin').delete(result3['id'])
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 0)

        def test_list_plugin_configuration(self):
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertIsNotNone(result)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 0)

            result2 = self.client.apis.plugins('Mockbin').create('ratelimiting', enabled=False, second=20)
            self.assertIsNotNone(result2)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 1)

            result3 = self.client.apis.plugins('Mockbin').create('requestsizelimiting', allowed_payload_size=512)
            self.assertIsNotNone(result3)
            self.assertEqual(self.client.apis.plugins('Mockbin').count(), 2)

            result4 = self.client.apis.plugins('Mockbin').list()
            data = result4['data']

            self.assertEqual(len(data), 2)

            result5 = self.client.apis.plugins('Mockbin').list(name='requestsizelimiting')
            data = result5['data']

            self.assertEqual(len(data), 1)

        def _cleanup_afterwards(self, name_or_id):
            self._cleanup.append(name_or_id)
            return name_or_id

    class ConsumerTestCase(ClientFactoryMixin, TestCase):
        __metaclass__ = ABCMeta

        def setUp(self):
            self.client = self.on_create_client()
            self.assertTrue(self.client.consumers.count() == 0)
            self._cleanup = []

        def tearDown(self):
            for name_or_id in set(self._cleanup):
                self.client.consumers.delete(name_or_id)
            self.assertEqual(self.client.consumers.count(), 0)

        def test_create(self):
            result = self.client.consumers.create(
                username=self._cleanup_afterwards('abc1234'), custom_id='41245871-1s7q-awdd35aw-d8a6s2d12345')
            self.assertIsNotNone(result)
            self.assertEqual(result['username'], 'abc1234')
            self.assertEqual(result['custom_id'], '41245871-1s7q-awdd35aw-d8a6s2d12345')

        def test_create_only_username(self):
            result = self.client.consumers.create(username=self._cleanup_afterwards('abc123'))
            self.assertIsNotNone(result)
            self.assertFalse('custom_id' in result)
            self.assertEqual(result['username'], 'abc123')

        def test_create_only_custom_id(self):
            result = self.client.consumers.create(custom_id='41245871-1s7q-awdd35aw-d8a6s2d4a8q9')
            self.assertIsNotNone(result)
            self._cleanup_afterwards(result['id'])  # We have no username, so we can only delete afterwards with id
            self.assertFalse('username' in result)
            self.assertEqual(result['custom_id'], '41245871-1s7q-awdd35aw-d8a6s2d4a8q9')

        def test_create_conflict(self):
            result1 = self.client.consumers.create(
                username=self._cleanup_afterwards('abc1234'), custom_id='41245871-1s7q-awdd35aw-d8a6s2d12345')
            self.assertIsNotNone(result1)

            result2 = None
            error_thrown = False
            try:
                result2 = self.client.consumers.create(
                    username=self._cleanup_afterwards('abc1234'), custom_id='41245871-1s7q-awdd35aw-d8a6s2d12345')
            except ConflictError:
                error_thrown = True
            self.assertTrue(error_thrown)
            self.assertIsNone(result2)

        def test_create_conflict_only_username(self):
            result1 = self.client.consumers.create(username=self._cleanup_afterwards('abc123'))
            self.assertIsNotNone(result1)

            result2 = None
            error_thrown = False
            try:
                result2 = self.client.consumers.create(username=self._cleanup_afterwards('abc123'))
            except ConflictError:
                error_thrown = True
            self.assertTrue(error_thrown)
            self.assertIsNone(result2)

        def test_create_conflict_only_custom_id(self):
            result1 = self.client.consumers.create(custom_id='41245871-1s7q-awdd35aw-d8a6s2d4a8q9')
            self.assertIsNotNone(result1)
            self._cleanup_afterwards(result1['id'])  # We have no username, so we can only delete afterwards with id

            result2 = None
            error_thrown = False
            try:
                result2 = self.client.consumers.create(custom_id='41245871-1s7q-awdd35aw-d8a6s2d4a8q9')
            except ConflictError:
                error_thrown = True
            self.assertTrue(error_thrown)
            self.assertIsNone(result2)

        def test_update(self):
            result1 = self.client.consumers.create(username='abc123', custom_id='123456789')
            self.assertIsNotNone(result1)
            self._cleanup_afterwards(result1['id'])

            # update by username
            result2 = self.client.consumers.update(result1['username'], username='abc456')
            self.assertIsNotNone(result2)
            self.assertEqual(result2['id'], result1['id'])
            self.assertEqual(result2['username'], 'abc456')

            # update by id
            result3 = self.client.consumers.update(result1['id'], username='abc789', custom_id='987654321')
            self.assertIsNotNone(result3)
            self.assertEqual(result3['id'], result1['id'])
            self.assertEqual(result3['username'], 'abc789')
            self.assertEqual(result3['custom_id'], '987654321')

            # retrieve to check
            result4 = self.client.consumers.retrieve(result1['id'])
            self.assertIsNotNone(result4)
            self.assertEqual(result4['username'], 'abc789')
            self.assertEqual(result4['custom_id'], '987654321')

        def test_retrieve(self):
            result = self.client.consumers.create(
                username=self._cleanup_afterwards('abc1234'), custom_id='41245871-1s7q-awdd35aw-d8a6s2d12345')
            self.assertIsNotNone(result)
            self.assertEqual(result['username'], 'abc1234')
            self.assertEqual(result['custom_id'], '41245871-1s7q-awdd35aw-d8a6s2d12345')

            # Retrieve by username
            result2 = self.client.consumers.retrieve('abc1234')
            self.assertEqual(result2, result)

            # Retrieve by id
            result3 = self.client.consumers.retrieve(result['id'])
            self.assertEqual(result3, result)
            self.assertEqual(result3, result2)

        def test_list(self):
            amount = 10

            for i in range(amount):
                self.client.consumers.create(
                    username=self._cleanup_afterwards('abc1234_%s' % i),
                    custom_id='41245871-1s7q-awdd35aw-d8a6s2d12345_%s' % i)

            self.assertEqual(self.client.consumers.count(), amount)

            result = self.client.consumers.list()
            self.assertTrue('data' in result)
            data = result['data']

            self.assertEqual(len(data), amount)

            result = self.client.consumers.list(custom_id='41245871-1s7q-awdd35aw-d8a6s2d12345_6')
            self.assertTrue('data' in result)
            data = result['data']

            self.assertEqual(len(data), 1)

            result = self.client.consumers.list(size=3)
            self.assertIsNotNone(result['next'])
            self.assertEqual(len(result['data']), 3)

        def test_iterate(self):
            amount = 10

            for i in range(amount):
                self.client.consumers.create(
                    username=self._cleanup_afterwards('abc1234_%s' % i),
                    custom_id='41245871-1s7q-awdd35aw-d8a6s2d12345_%s' % i)

            found = []

            for item in self.client.consumers.iterate(window_size=3):
                found.append(item)

            self.assertEqual(len(found), amount)
            self.assertEqual(
                sorted([item['id'] for item in found]),
                sorted([item['id'] for item in self.client.consumers.list().get('data')]))

        def test_delete(self):
            result1 = self.client.consumers.create(
                username='abc1234', custom_id='41245871-1s7q-awdd35aw-d8a6s2d12345')
            result2 = self.client.consumers.create(
                username='abc12345', custom_id='51245871-1s7q-awdd35aw-d8a6s2d12346')
            self.assertEqual(self.client.consumers.count(), 2)
            self.assertEqual(result1['username'], 'abc1234')
            self.assertEqual(result2['username'], 'abc12345')

            # Delete by id
            self.client.consumers.delete(result1['id'])
            self.assertEqual(self.client.consumers.count(), 1)

            # Delete by username
            self.client.consumers.delete(result2['username'])
            self.assertEqual(self.client.consumers.count(), 0)

        def _cleanup_afterwards(self, username_or_id):
            self._cleanup.append(username_or_id)
            return username_or_id

    class PluginTestCase(ClientFactoryMixin, TestCase):
        __metaclass__ = ABCMeta

        def setUp(self):
            self.client = self.on_create_client()

        def test_list(self):
            result = self.client.plugins.list()
            self.assertIsNotNone(result)
            self.assertTrue('enabled_plugins' in result)
            self.assertTrue(isinstance(result['enabled_plugins'], collections.Iterable))

        def test_retrieve_schema(self):
            result = self.client.plugins.list()
            self.assertIsNotNone(result)

            # sanity check
            self.assertTrue(len(result['enabled_plugins']) >= 1)

            for plugin_name in result['enabled_plugins']:
                schema = self.client.plugins.retrieve_schema(plugin_name)
                self.assertIsNotNone(schema)
                self.assertTrue(isinstance(schema, dict))


class UtilTestCase(TestCase):
    def test_uuid_or_string_uuid(self):
        input = uuid.uuid4()
        result = uuid_or_string(input)
        self.assertEqual(result, str(input))

    def test_uuid_or_string_incorrect_value(self):
        result = None
        error_thrown = False
        try:
            result = uuid_or_string(1234)
        except ValueError:
            error_thrown = True
        self.assertTrue(error_thrown)
        self.assertIsNone(result)

    def test_add_url_params(self):
        params = OrderedDict({
            'bla1': 1,
            'bla2': 'hello',
            'bla3': True,
            'bla4': sorted_ordered_dict({'a': 1, 'b': ['a', 2, False]})
        })
        result = add_url_params('http://localhost/?x=0', params)
        expected_result = \
            'http://localhost/?bla1=1&bla2=hello&bla3=%s&%s&x=0' % (
                json.dumps(True),
                urlencode({
                    'bla4': json.dumps(params['bla4'])
                }))
        self.assertEqual(result, expected_result)


class SimulatorAPITestCase(KongAdminTesting.APITestCase):
    def on_create_client(self):
        return KongAdminSimulator()


class SimulatorConsumerTestCase(KongAdminTesting.ConsumerTestCase):
    def on_create_client(self):
        return KongAdminSimulator()


class SimulatorPluginTestCase(KongAdminTesting.PluginTestCase):
    def on_create_client(self):
        return KongAdminSimulator()


@skipIf(kong_testserver_is_up() is False, 'Kong testserver is down')
class ClientAPITestCase(KongAdminTesting.APITestCase):
    def on_create_client(self):
        return KongAdminClient(API_URL)


@skipIf(kong_testserver_is_up() is False, 'Kong testserver is down')
class ClientConsumerTestCase(KongAdminTesting.ConsumerTestCase):
    def on_create_client(self):
        return KongAdminClient(API_URL)


@skipIf(kong_testserver_is_up() is False, 'Kong testserver is down')
class ClientPluginTestCase(KongAdminTesting.PluginTestCase):
    def on_create_client(self):
        return KongAdminClient(API_URL)


if __name__ == '__main__':
    run_unittests()
