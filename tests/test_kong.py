# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from unittest import TestCase

from kong.simulator import KongAdminSimulator


class SimulatorTestCase(TestCase):
    def setUp(self):
        self.sim = KongAdminSimulator()

    def test_apis_crud(self):
        result = self.sim.apis.add(target_url='http://mockbin.com', name='Mockbin', public_dns='mockbin.com')
        self.assertEqual(result['target_url'], 'http://mockbin.com')
        self.assertEqual(result['name'], 'Mockbin')
        self.assertEqual(result['public_dns'], 'mockbin.com')
        self.assertIsNotNone(result['id'])
        self.assertIsNotNone(result['created_at'])
