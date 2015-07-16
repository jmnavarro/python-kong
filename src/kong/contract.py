# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from abc import ABCMeta, abstractproperty, abstractmethod

from six import with_metaclass


class APIAdminContract(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def add(self, target_url, name=None, public_dns=None, path=None, strip_path=False):
        """
        :param target_url: The base target URL that points to your API server, this URL will be used for proxying
            requests. For example, https://mockbin.com.
        :type target_url: basestring
        :param name:
        :type name: basestring
        :param public_dns:
        :type public_dns: basestring
        :param path:
        :type path: basestring
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
        :type name_or_id: basestring | uuid.UUID
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
    def list(self, id=None, name=None, public_dns=None, target_url=None, size=100, offset=None):
        """
        :param id: A filter on the list based on the apis id field.
        :type id: uuid.UUID
        :param name: A filter on the list based on the apis name field.
        :type name: basestring
        :param public_dns: A filter on the list based on the apis public_dns field.
        :type public_dns: basestring
        :param target_url: A filter on the list based on the apis target_url field.
        :type target_url: basestring
        :param size: A limit on the number of objects to be returned.
        :type size: int
        :param offset: A cursor used for pagination. offset is an object identifier that defines a place in the list.
        :type offset: uuid.UUID
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
    def update(self, name_or_id, target_url, name=None, public_dns=None, path=None, strip_path=False):
        """
        :param name_or_id: The unique identifier or the name of the API to update
        :type name_or_id: basestring | uuid.UUID
        :param target_url: The base target URL that points to your API server, this URL will be used for proxying
            requests. For example, https://mockbin.com.
        :type target_url: basestring
        :param name:
        :type name: basestring
        :param public_dns:
        :type public_dns: basestring
        :param path:
        :type path: basestring
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
    def delete(self, name_or_id):
        """
        :param name_or_id: The unique identifier or the name of the API to delete
        :type name_or_id: basestring | uuid.UUID
        """


class ConsumerAdminContract(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def create(self, username=None, custom_id=None):
        """
        :param username: The username of the consumer. You must send either this field or custom_id with the request.
        :type username: basestring
        :param custom_id: Field for storing an existing ID for the consumer, useful for mapping Kong with users in your
            existing database. You must send either this field or username with the request.
        :type custom_id: basestring
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
        :type username_or_id: basestring | uuid.UUID
        :rtype: dict
        :return: Dictionary containing the Consumer description. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "custom_id": "abc123",
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def list(self, id=None, custom_id=None, username=None, size=100, offset=None):
        """
        :param id: A filter on the list based on the consumer id field.
        :type id: uuid.UUID
        :param custom_id: A filter on the list based on the consumer custom_id field.
        :type custom_id: basestring
        :param username: A filter on the list based on the consumer username field.
        :type username: basestring
        :param size: A limit on the number of objects to be returned.
        :type size: int
        :param offset: A cursor used for pagination. offset is an object identifier that defines a place in the list.
        :type offset: uuid.UUID
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
    def update(self, username_or_id, username=None, custom_id=None):
        """
        :param username_or_id: The unique identifier or the username of the consumer to update
        :type username_or_id: basestring | uuid.UUID
        :param username: The username of the consumer. You must send either this field or custom_id with the request.
        :type username: basestring
        :param custom_id: Field for storing an existing ID for the consumer, useful for mapping Kong with users in your
            existing database. You must send either this field or username with the request.
        :type custom_id: basestring
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
        :type username_or_id: basestring | uuid.UUID
        """


class PluginConfigurationAdminContract(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def create(self, api_name_or_id, name, value, consumer_id=None):
        """
        :param api_name_or_id: The unique identifier or the name of the API on which to add a plugin configuration
        :type api_name_or_id: basestring | uuid.UUID
        :param name: The name of the Plugin that's going to be added. Currently the Plugin must be installed in every
            Kong instance separately.
        :type name: basestring
        :param value: The configuration properties for the Plugin which can be found on the plugins documentation page
            in the Plugin Gallery.
        :type value: dict
        :param consumer_id: The unique identifier of the consumer that overrides the existing settings for this specific
            consumer on incoming requests.
        :type consumer_id: uuid.UUID
        :rtype: dict
        :return: Dictionary containing the PluginConfiguration description. Example:
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
    def list(self, id=None, name=None, api_id=None, consumer_id=None, size=100, offset=None):
        """
        :param id: A filter on the list based on the id field.
        :type id: uuid.UUID
        :param name: A filter on the list based on the name field.
        :type name: basestring
        :param api_id: A filter on the list based on the api_id field.
        :type api_id: uuid.UUID
        :param consumer_id: A filter on the list based on the consumer_id field.
        :type consumer_id: uuid.UUID
        :param size: A limit on the number of objects to be returned.
        :type size: int
        :param offset: A cursor used for pagination. offset is an object identifier that defines a place in the list.
        :type offset: uuid.UUID
        :rtype: dict
        :return: Dictionary containing dictionaries containing PluginConfiguration descriptions. Example:
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
                    "next": "http://localhost:8001/plugins_configurations/?size=10&offset=4d924084-1adb-40a5-c042-1s..."
                }
        """

    @abstractmethod
    def update(self, api_name_or_id, plugin_configuration_name_or_id, name, value, consumer_id=None):
        """
        :param api_name_or_id: The unique identifier or the name of the API for which to update the plugin configuration
        :type api_name_or_id: basestring | uuid.UUID
        :param plugin_configuration_name_or_id: The unique identifier or the name of the plugin for which to update the
            configuration on this API
        :type plugin_configuration_name_or_id: basestring | uuid.UUID
        :param name: The name of the Plugin that's going to be added. Currently the Plugin must be installed in every
            Kong instance separately.
        :type name: basestring
        :param value: The configuration properties for the Plugin which can be found on the plugins documentation page
            in the Plugin Gallery.
        :type value: dict
        :param consumer_id: The unique identifier of the consumer that overrides the existing settings for this specific
            consumer on incoming requests.
        :type consumer_id: uuid.UUID
        :rtype: dict
        :return: Dictionary containing the PluginConfiguration description. Example:
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
    def delete(self, api_name_or_id, plugin_configuration_name_or_id):
        """
        :param api_name_or_id: The unique identifier or the name of the API for which to delete the plugin configuration
        :type api_name_or_id: basestring | uuid.UUID
        :param plugin_configuration_name_or_id: The unique identifier or the name of the plugin for which to delete the
            configuration on this API
        :type plugin_configuration_name_or_id: basestring | uuid.UUID
        """


class KongAdminContract(with_metaclass(ABCMeta, object)):
    @abstractproperty
    def apis(self):
        """
        :rtype: APIAdminContract
        :return:
        """

    @abstractproperty
    def consumers(self):
        """
        :rtype: ConsumerAdminContract
        :return:
        """

    @abstractproperty
    def plugin_configurations(self):
        """
        :rtype: PluginConfigurationAdminContract
        :return:
        """
