# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from .contract import KongAdminContract, APIAdminContract, ConsumerAdminContract, PluginConfigurationAdminContract


class APIAdminClient(APIAdminContract):
    pass


class ConsumerAdminClient(ConsumerAdminContract):
    pass


class PluginConfigurationAdminClient(PluginConfigurationAdminContract):
    pass


class KongAdminClient(KongAdminContract):
    apis = APIAdminClient()
    consumers = ConsumerAdminClient()
    plugin_configurations = PluginConfigurationAdminClient()
