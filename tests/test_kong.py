# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from six import with_metaclass
from abc import ABCMeta, abstractmethod
import os
from unittest import TestCase

from kong.simulator import KongAdminSimulator
from kong.client import KongAdminClient

API_URL = os.environ.get('PYKONG_TEST_API_URL', 'http://localhost:8001')


class KongAdminTesting(object):
    """
    Important: Do not remove nesting!
    """
    class KongAdminTestCase(with_metaclass(ABCMeta, TestCase)):
        @abstractmethod
        def on_create_client(self):
            pass

        def setUp(self):
            self.client = self.on_create_client()
            self.assertTrue(self.client.apis.count() == 0)
            self._api_cleanup = []

        def tearDown(self):
            for name_or_id in self._api_cleanup:
                self.client.apis.delete(name_or_id)
            self.assertEqual(self.client.apis.count(), 0)

        def test_apis_add(self):
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_api('Mockbin'), public_dns='mockbin.com')
            self.assertEqual(self.client.apis.count(), 1)
            self.assertEqual(result['target_url'], 'http://mockbin.com/')
            self.assertEqual(result['name'], 'Mockbin')
            self.assertEqual(result['public_dns'], 'mockbin.com')
            self.assertIsNotNone(result['id'])
            self.assertIsNotNone(result['created_at'])
            self.assertFalse('path' in result)

        def test_apis_update(self):
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_api('Mockbin'), public_dns='mockbin.com')

            # Update by name
            result2 = self.client.apis.update('Mockbin', 'http://mockbin.com', path='/someservice', strip_path=True)
            self.assertEqual(result2['path'], '/someservice')
            self.assertEqual(result2['public_dns'], 'mockbin.com')
            self.assertTrue(result2['strip_path'])

            # Update by id
            result3 = self.client.apis.update(
                result['id'], 'http://mockbin2.com', path='/someotherservice', public_dns='example.com')
            self.assertEqual(result3['target_url'], 'http://mockbin2.com/')
            self.assertEqual(result3['path'], '/someotherservice')
            self.assertEqual(result3['public_dns'], 'example.com')
            self.assertTrue(result3['strip_path'])

        def test_apis_retrieve(self):
            result = self.client.apis.add(
                target_url='http://mockbin.com', name=self._cleanup_api('Mockbin'), public_dns='mockbin.com')

            # Retrieve by name
            result2 = self.client.apis.retrieve('Mockbin')
            self.assertEqual(result2, result)

            # Retrieve by id
            result3 = self.client.apis.retrieve(result['id'])
            self.assertEqual(result3, result)
            self.assertEqual(result3, result2)

        def _cleanup_api(self, name_or_id):
            self._api_cleanup.append(name_or_id)
            return name_or_id


class SimulatorTestCase(KongAdminTesting.KongAdminTestCase):
    def on_create_client(self):
        return KongAdminSimulator()


class ClientTestCase(KongAdminTesting.KongAdminTestCase):
    def on_create_client(self):
        return KongAdminClient(API_URL)