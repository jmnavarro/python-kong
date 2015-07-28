# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from abc import ABCMeta, abstractmethod

from six import with_metaclass

from .mixins import CollectionMixin


class APIPluginConfigurationAdminContract(CollectionMixin):
    __metaclass__ = ABCMeta

    @abstractmethod
    def count(self):
        """
        :rtype: int
        :return: Amount of records
        """

    @abstractmethod
    def create(self, plugin_name, enabled=None, consumer_id=None, **fields):
        """
        :param plugin_name: The name of the Plugin that's going to be added. Currently the Plugin must be installed in
            every Kong instance separately.
        :type plugin_name: str
        :param enabled: Whether or not the pluginconfiguration is enabled
        :type enabled: bool
        :param consumer_id: The unique identifier of the consumer that overrides the existing settings for this
            specific consumer on incoming requests.
        :type consumer_id: str | uuid.UUID
        :param fields: The configuration properties for the Plugin which can be found on the plugins documentation page
            in the Plugin Gallery.
        :type fields: dict
        :rtype: dict
        :return: Dictionary containing the API plugin configuration. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "api_id": "5fd1z584-1adb-40a5-c042-63b19db49x21",
                    "consumer_id": "a3dX2dh2-1adb-40a5-c042-63b19dbx83hF4",
                    "name": "ratelimiting",
                    "value": {
                        "limit": 20,
                        "period": "minute"
                    },
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def list(self, size=100, offset=None, **filter_fields):
        """
        :param size: A limit on the number of objects to be returned.
        :type size: int
        :param offset: A cursor used for pagination. offset is an object identifier that defines a place in the list.
        :type offset: uuid.UUID
        :param filter_fields: Dictionary containing values to filter for
        :type filter_fields: dict
        :rtype: dict
        :return: Dictionary containing dictionaries containing the API description. Example:
                {
                    "total": 2,
                    "data": [
                      {
                          "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                          "api_id": "5fd1z584-1adb-40a5-c042-63b19db49x21",
                          "name": "ratelimiting",
                          "value": {
                              "limit": 20,
                              "period": "minute"
                          },
                          "created_at": 1422386534
                      },
                      {
                          "id": "3f924084-1adb-40a5-c042-63b19db421a2",
                          "api_id": "5fd1z584-1adb-40a5-c042-63b19db49x21",
                          "consumer_id": "a3dX2dh2-1adb-40a5-c042-63b19dbx83hF4",
                          "name": "ratelimiting",
                          "value": {
                              "limit": 300,
                              "period": "hour"
                          },
                          "created_at": 1422386585
                      }
                    ],
                    "next": "http://localhost:8001/plugins_configurations/?size=10&offset=4d924084-1adb-40a5-c042-63b19db421d1"
                }
        """

    @abstractmethod
    def update(self, plugin_name, enabled=None, consumer_id=None, **fields):
        """
        :param plugin_name: The name of the Plugin that's going to be updated. Currently the Plugin must be installed in
            every Kong instance separately.
        :type plugin_name: str
        :param enabled: Whether or not the pluginconfiguration is enabled
        :type enabled: bool
        :param consumer_id: The unique identifier of the consumer that overrides the existing settings for this specific
            consumer on incoming requests.
        :type consumer_id: str | uuid.UUID
        :param fields: Optional dictionary which values will be used to overwrite the existing values
        :type fields: dict
        :rtype: dict
        :return: Dictionary containing the API plugin configuration. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "api_id": "5fd1z584-1adb-40a5-c042-63b19db49x21",
                    "consumer_id": "a3dX2dh2-1adb-40a5-c042-63b19dbx83hF4",
                    "name": "ratelimiting",
                    "value": {
                        "limit": 50,
                        "period": "second"
                    },
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def delete(self, plugin_name_or_id):
        """
        :param plugin_name_or_id: The unique identifier or the name of the plugin for which to delete the configuration
            on this API
        :type plugin_name_or_id: str | uuid.UUID
        """


class APIAdminContract(CollectionMixin):
    __metaclass__ = ABCMeta

    @abstractmethod
    def count(self):
        """
        :rtype: int
        :return: Amount of records
        """

    @abstractmethod
    def add(self, target_url, name=None, public_dns=None, path=None, strip_path=False):
        """
        :param target_url: The base target URL that points to your API server, this URL will be used for proxying
            requests. For example, https://mockbin.com.
        :type target_url: str
        :param name:
        :type name: str
        :param public_dns:
        :type public_dns: str
        :param path:
        :type path: str
        :param strip_path:
        :type strip_path: bool
        :rtype: dict
        :return: Dictionary containing the API description. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "name": "Mockbin",
                    "public_dns": "mockbin.com",
                    "target_url": "http://mockbin.com",
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def retrieve(self, name_or_id):
        """
        :param name_or_id: The unique identifier or the name of the API to retrieve
        :type name_or_id: str | uuid.UUID
        :rtype: dict
        :return: Dictionary containing the API description. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "name": "Mockbin",
                    "public_dns": "mockbin.com",
                    "target_url": "https://mockbin.com",
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def list(self, size=100, offset=None, **filter_fields):
        """
        :param size: A limit on the number of objects to be returned.
        :type size: int
        :param offset: A cursor used for pagination. offset is an object identifier that defines a place in the list.
        :type offset: uuid.UUID
        :param filter_fields: Dictionary containing values to filter for
        :type filter_fields: dict
        :rtype: dict
        :return: Dictionary containing dictionaries containing the API description. Example:
                {
                    "total": 2,
                    "data": [
                        {
                            "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                            "name": "Mockbin",
                            "public_dns": "mockbin.com",
                            "target_url": "https://mockbin.com",
                            "created_at": 1422386534
                        },
                        {
                            "id": "3f924084-1adb-40a5-c042-63b19db421a2",
                            "name": "PrivateAPI",
                            "public_dns": "internal.api.com",
                            "target_url": "http://private.api.com",
                            "created_at": 1422386585
                        }
                    ],
                    "next": "http://localhost:8001/apis/?size=10&offset=4d924084-1adb-40a5-c042-63b19db421d1"
                }
        """



    @abstractmethod
    def update(self, name_or_id, target_url, **fields):
        """
        :param name_or_id: The unique identifier or the name of the API to update
        :type name_or_id: str | uuid.UUID
        :param target_url: The base target URL that points to your API server, this URL will be used for proxying
            requests. For example, https://mockbin.com.
        :type target_url: str
        :param fields: Optional dictionary which values will be used to overwrite the existing values
        :type fields: dict
        :rtype: dict
        :return: Dictionary containing the API description. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "name": "Mockbin",
                    "public_dns": "mockbin.com",
                    "target_url": "http://mockbin.com",
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def delete(self, name_or_id):
        """
        :param name_or_id: The unique identifier or the name of the API to delete
        :type name_or_id: str | uuid.UUID
        """

    @abstractmethod
    def plugins(self, name_or_id):
        """
        :param name_or_id: The unique identifier or the name of the API to get the APIPluginAdminContract for
        :rtype: APIPluginConfigurationAdminContract
        :return:
        """


class ConsumerAdminContract(CollectionMixin):
    __metaclass__ = ABCMeta

    @abstractmethod
    def count(self):
        """
        :rtype: int
        :return: Amount of records
        """

    @abstractmethod
    def create(self, username=None, custom_id=None):
        """
        :param username: The username of the consumer. You must send either this field or custom_id with the request.
        :type username: str
        :param custom_id: Field for storing an existing ID for the consumer, useful for mapping Kong with users in your
            existing database. You must send either this field or username with the request.
        :type custom_id: str
        :rtype: dict
        :return: Dictionary containing the Consumer description. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "custom_id": "abc123",
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def retrieve(self, username_or_id):
        """
        :param username_or_id: The unique identifier or the username of the consumer to retrieve
        :type username_or_id: str | uuid.UUID
        :rtype: dict
        :return: Dictionary containing the Consumer description. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "custom_id": "abc123",
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def list(self, size=100, offset=None, **filter_fields):
        """
        :param size: A limit on the number of objects to be returned.
        :type size: int
        :param offset: A cursor used for pagination. offset is an object identifier that defines a place in the list.
        :type offset: uuid.UUID
        :param filter_fields: Dictionary containing values to filter for
        :type filter_fields: dict
        :rtype: dict
        :return: Dictionary containing dictionaries containing the Consumer description. Example:
                {
                    "total": 2,
                    "data": [
                        {
                            "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                            "custom_id": "abc123",
                            "created_at": 1422386534
                        },
                        {
                            "id": "3f924084-1adb-40a5-c042-63b19db421a2",
                            "custom_id": "def345",
                            "created_at": 1422386585
                        }
                    ],
                    "next": "http://localhost:8001/consumers/?size=10&offset=4d924084-1adb-40a5-c042-63b19db421d1"
                }
        """

    @abstractmethod
    def update(self, username_or_id, **fields):
        """
        :param username_or_id: The unique identifier or the username of the consumer to update
        :type username_or_id: str | uuid.UUID
        :param fields: Optional dictionary which values will be used to overwrite the existing values
        :type fields: dict
        :rtype: dict
        :return: Dictionary containing the Consumer description. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "custom_id": "abc123",
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def delete(self, username_or_id):
        """
        :param username_or_id: The unique identifier or the name of the consumer to delete
        :type username_or_id: str | uuid.UUID
        """


class PluginAdminContract(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def list(self):
        """
        :rtype: dict
        :return: Returns a list of all installed plugins on the node.
        """

    @abstractmethod
    def retrieve_schema(self, plugin_name):
        """
        :param plugin_name:
        :type plugin_name: str
        :rtype: dict
        :return: Returns the schema of a plugin's configuration.
        """


class KongAdminContract(object):
    def __init__(self, apis, consumers, plugins):
        self._apis = apis
        self._consumers = consumers
        self._plugins = plugins

    @property
    def apis(self):
        """
        :rtype: APIAdminContract
        :return:
        """
        return self._apis

    @property
    def consumers(self):
        """
        :rtype: ConsumerAdminContract
        :return:
        """
        return self._consumers

    @property
    def plugins(self):
        """
        :rtype: PluginAdminContract
        :return:
        """
        return self._plugins
