# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from abc import ABCMeta, abstractmethod
import os
import sys
import unittest
from unittest import TestCase

# To run the standalone test script
if __name__ == '__main__':
    sys.path.append('../src/')

from kong.exceptions import ConflictError
from kong.simulator import APIAdminSimulator, ConsumerAdminSimulator
from kong.client import APIAdminClient, ConsumerAdminClient

API_URL = os.environ.get('PYKONG_TEST_API_URL', 'http://localhost:8001')


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
            self.assertTrue(self.client.count() == 0)
            self._cleanup = []

        def tearDown(self):
            for name_or_id in set(self._cleanup):
                self.client.delete(name_or_id)
            self.assertEqual(self.client.count(), 0)

        def test_add(self):
            result = self.client.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertEqual(self.client.count(), 1)
            self.assertEqual(result['target_url'], 'http://mockbin.com/')
            self.assertEqual(result['name'], 'Mockbin')
            self.assertEqual(result['public_dns'], 'mockbin.com')
            self.assertIsNotNone(result['id'])
            self.assertIsNotNone(result['created_at'])
            self.assertFalse('path' in result)

        def test_add_conflict(self):
            result = self.client.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            self.assertIsNotNone(result)
            self.assertEqual(self.client.count(), 1)

            result2 = None
            error_thrown = False
            try:
                result2 = self.client.add(
                    target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')
            except ConflictError:
                error_thrown = True
            self.assertTrue(error_thrown)
            self.assertIsNone(result2)

            self.assertEqual(self.client.count(), 1)

        def test_update(self):
            result = self.client.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')

            # Update by name
            result2 = self.client.update('Mockbin', 'http://mockbin.com', path='/someservice', strip_path=True)
            self.assertEqual(result2['path'], '/someservice')
            self.assertEqual(result2['public_dns'], 'mockbin.com')
            self.assertTrue(result2['strip_path'])

            # Update by id
            result3 = self.client.update(
                result['id'], 'http://mockbin2.com', path='/someotherservice', public_dns='example.com')
            self.assertEqual(result3['target_url'], 'http://mockbin2.com/')
            self.assertEqual(result3['path'], '/someotherservice')
            self.assertEqual(result3['public_dns'], 'example.com')
            self.assertTrue(result3['strip_path'])

        def test_retrieve(self):
            result = self.client.add(
                target_url='http://mockbin.com', name=self._cleanup_afterwards('Mockbin'), public_dns='mockbin.com')

            # Retrieve by name
            result2 = self.client.retrieve('Mockbin')
            self.assertEqual(result2, result)

            # Retrieve by id
            result3 = self.client.retrieve(result['id'])
            self.assertEqual(result3, result)
            self.assertEqual(result3, result2)

        def test_list(self):
            amount = 10

            for i in xrange(amount):
                self.client.add(
                    target_url='http://mockbin%s.com' % i,
                    name=self._cleanup_afterwards('Mockbin%s' % i),
                    public_dns='mockbin%s.com' % i)

            self.assertEqual(self.client.count(), amount)

            result = self.client.list()
            self.assertTrue('data' in result)

            data = result['data']

            self.assertEqual(len(data), amount)

        def test_delete(self):
            result1 = self.client.add(
                target_url='http://mockbin1.com', name='Mockbin1', public_dns='mockbin1.com')
            result2 = self.client.add(
                target_url='http://mockbin2.com', name='Mockbin2', public_dns='mockbin2.com')
            self.assertEqual(self.client.count(), 2)
            self.assertEqual(result1['target_url'], 'http://mockbin1.com/')
            self.assertEqual(result2['target_url'], 'http://mockbin2.com/')

            # Delete by id
            self.client.delete(result1['id'])
            self.assertEqual(self.client.count(), 1)

            # Delete by id
            self.client.delete(result2['name'])
            self.assertEqual(self.client.count(), 0)

        def _cleanup_afterwards(self, name_or_id):
            self._cleanup.append(name_or_id)
            return name_or_id

    class ConsumerTestCase(ClientFactoryMixin, TestCase):
        __metaclass__ = ABCMeta

        def setUp(self):
            self.client = self.on_create_client()
            self.assertTrue(self.client.count() == 0)
            self._cleanup = []

        def tearDown(self):
            for name_or_id in set(self._cleanup):
                self.client.delete(name_or_id)
            self.assertEqual(self.client.count(), 0)

        def test_create(self):
            result = self.client.create(
                username=self._cleanup_afterwards('i5009821'), custom_id='41245871-1s7q-awdd35aw-d8a6s2d12345')
            self.assertIsNotNone(result)
            self.assertEqual(result['username'], 'i5009821')
            self.assertEqual(result['custom_id'], '41245871-1s7q-awdd35aw-d8a6s2d12345')

        def test_create_only_username(self):
            result = self.client.create(username=self._cleanup_afterwards('i5009820'))
            self.assertIsNotNone(result)
            self.assertFalse('custom_id' in result)
            self.assertEqual(result['username'], 'i5009820')

        def test_create_only_custom_id(self):
            result = self.client.create(custom_id='41245871-1s7q-awdd35aw-d8a6s2d4a8q9')
            self.assertIsNotNone(result)
            self._cleanup_afterwards(result['id'])  # We have no username, so we can only delete afterwards with id
            self.assertFalse('username' in result)
            self.assertEqual(result['custom_id'], '41245871-1s7q-awdd35aw-d8a6s2d4a8q9')

        def test_create_conflict(self):
            result1 = self.client.create(
                username=self._cleanup_afterwards('i5009821'), custom_id='41245871-1s7q-awdd35aw-d8a6s2d12345')
            self.assertIsNotNone(result1)

            result2 = None
            error_thrown = False
            try:
                result2 = self.client.create(
                    username=self._cleanup_afterwards('i5009821'), custom_id='41245871-1s7q-awdd35aw-d8a6s2d12345')
            except ConflictError:
                error_thrown = True
            self.assertTrue(error_thrown)
            self.assertIsNone(result2)

        def test_create_conflict_only_username(self):
            result1 = self.client.create(username=self._cleanup_afterwards('i5009820'))
            self.assertIsNotNone(result1)

            result2 = None
            error_thrown = False
            try:
                result2 = self.client.create(username=self._cleanup_afterwards('i5009820'))
            except ConflictError:
                error_thrown = True
            self.assertTrue(error_thrown)
            self.assertIsNone(result2)

        def test_create_conflict_only_custom_id(self):
            result1 = self.client.create(custom_id='41245871-1s7q-awdd35aw-d8a6s2d4a8q9')
            self.assertIsNotNone(result1)
            self._cleanup_afterwards(result1['id'])  # We have no username, so we can only delete afterwards with id

            result2 = None
            error_thrown = False
            try:
                result2 = self.client.create(custom_id='41245871-1s7q-awdd35aw-d8a6s2d4a8q9')
            except ConflictError:
                error_thrown = True
            self.assertTrue(error_thrown)
            self.assertIsNone(result2)

        def _cleanup_afterwards(self, username_or_id):
            self._cleanup.append(username_or_id)
            return username_or_id


class SimulatorAPITestCase(KongAdminTesting.APITestCase):
    def on_create_client(self):
        return APIAdminSimulator()


class SimulatorConsumerTestCase(KongAdminTesting.ConsumerTestCase):
    def on_create_client(self):
        return ConsumerAdminSimulator()


class ClientAPITestCase(KongAdminTesting.APITestCase):
    def on_create_client(self):
        return APIAdminClient(API_URL)


class ClientConsumerTestCase(KongAdminTesting.ConsumerTestCase):
    def on_create_client(self):
        return ConsumerAdminClient(API_URL)


if __name__ == '__main__':
    unittest.main()
