# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from .contract import KongAdminContract, APIAdminContract, ConsumerAdminContract, PluginConfigurationAdminContract


class APIAdminSimulator(APIAdminContract):
    pass


class ConsumerAdminSimulator(ConsumerAdminContract):
    pass


class PluginConfigurationAdminSimulator(PluginConfigurationAdminContract):
    pass


class KongAdminSimulator(KongAdminContract):
    apis = APIAdminSimulator()
    consumers = ConsumerAdminSimulator()
    plugin_configurations = PluginConfigurationAdminSimulator()
