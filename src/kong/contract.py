# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from abc import ABCMeta, abstractmethod

from six import with_metaclass

from .mixins import CollectionMixin


class APIPluginConfigurationAdminContract(CollectionMixin):
    """
    Because we are already mixing with CollectionMixin, we cannot use 'with_metaclass(ABCMeta, ...)'. The solution is
      to explicitly define the __metaclass__ property on the class like below.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def destroy(self):
        """
        Releases all references, closes open connections, ...
        """

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
        :type plugin_name: six.text_type
        :param enabled: Whether or not the pluginconfiguration is enabled
        :type enabled: bool
        :param consumer_id: The unique identifier of the consumer that overrides the existing settings for this
            specific consumer on incoming requests.
        :type consumer_id: six.text_type | uuid.UUID
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
    def create_or_update(self, plugin_name, plugin_configuration_id=None, enabled=None, consumer_id=None, **fields):
        """
        :param plugin_name: The name of the Plugin that's going to be added. Currently the Plugin must be installed in
            every Kong instance separately.
        :type plugin_name: six.text_type
        :param plugin_configuration_id: The unique identifier of the plugin configuration to update
        :type plugin_configuration_id: six.text_type | uuid.UUID
        :param enabled: Whether or not the pluginconfiguration is enabled
        :type enabled: bool
        :param consumer_id: The unique identifier of the consumer that overrides the existing settings for this
            specific consumer on incoming requests.
        :type consumer_id: six.text_type | uuid.UUID
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
                    "next": \
                     "http://localhost:8001/plugins_configurations/?size=10&offset=4d924084-1adb-40a5-c042-63b19db421d1"
                }
        """

    @abstractmethod
    def update(self, plugin_name, enabled=None, consumer_id=None, **fields):
        """
        :param plugin_name: The name of the Plugin that's going to be updated. Currently the Plugin must be installed in
            every Kong instance separately.
        :type plugin_name: six.text_type
        :param enabled: Whether or not the pluginconfiguration is enabled
        :type enabled: bool
        :param consumer_id: The unique identifier of the consumer that overrides the existing settings for this specific
            consumer on incoming requests.
        :type consumer_id: six.text_type | uuid.UUID
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
    def retrieve(self, plugin_id):
        """
        :param plugin_id: The unique identifier of the plugin for which to retrieve the configuration on this API
        :type plugin_id: six.text_type | uuid.UUID
        """

    @abstractmethod
    def delete(self, plugin_id):
        """
        :param plugin_id: The unique identifier of the plugin for which to delete the configuration on this API
        :type plugin_id: six.text_type | uuid.UUID
        """


class APIAdminContract(CollectionMixin):
    __metaclass__ = ABCMeta

    @abstractmethod
    def destroy(self):
        """
        Releases all references, closes open connections, ...
        """

    @abstractmethod
    def count(self):
        """
        :rtype: int
        :return: Amount of records
        """

    @abstractmethod
    def create(self, upstream_url, name=None, request_host=None, request_path=None, strip_request_path=False,
               preserve_host=False):
        """
        :param upstream_url: The base target URL that points to your API server, this URL will be used for proxying
            requests. For example, https://mockbin.com.
        :type upstream_url: six.text_type
        :param name:
        :type name: six.text_type
        :param request_host:
        :type request_host: six.text_type
        :param request_path:
        :type request_path: six.text_type
        :param strip_request_path:
        :type strip_request_path: bool
        :param preserve_host:
        :type preserve_host: bool
        :rtype: dict
        :return: Dictionary containing the API description. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "name": "Mockbin",
                    "request_host": "mockbin.com",
                    "upstream_url": "http://mockbin.com",
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def create_or_update(self, upstream_url, api_id=None, name=None, request_host=None, request_path=None,
                         strip_request_path=False, preserve_host=False):
        """
        :param upstream_url: The base target URL that points to your API server, this URL will be used for proxying
            requests. For example, https://mockbin.com.
        :type upstream_url: six.text_type
        :param api_id: The unique identifier of the API to update
        :type api_id: six.text_type | uuid.UUID
        :param name:
        :type name: six.text_type
        :param request_host:
        :type request_host: six.text_type
        :param request_path:
        :type request_path: six.text_type
        :param strip_request_path:
        :type strip_request_path: bool
        :param preserve_host:
        :type preserve_host: bool
        :rtype: dict
        :return: Dictionary containing the API description. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "name": "Mockbin",
                    "request_host": "mockbin.com",
                    "upstream_url": "http://mockbin.com",
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def retrieve(self, name_or_id):
        """
        :param name_or_id: The unique identifier or the name of the API to retrieve
        :type name_or_id: six.text_type | uuid.UUID
        :rtype: dict
        :return: Dictionary containing the API description. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "name": "Mockbin",
                    "request_host": "mockbin.com",
                    "upstream_url": "https://mockbin.com",
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
                            "request_host": "mockbin.com",
                            "upstream_url": "https://mockbin.com",
                            "created_at": 1422386534
                        },
                        {
                            "id": "3f924084-1adb-40a5-c042-63b19db421a2",
                            "name": "PrivateAPI",
                            "request_host": "internal.api.com",
                            "upstream_url": "http://private.api.com",
                            "created_at": 1422386585
                        }
                    ],
                    "next": "http://localhost:8001/apis/?size=10&offset=4d924084-1adb-40a5-c042-63b19db421d1"
                }
        """

    @abstractmethod
    def update(self, name_or_id, upstream_url, **fields):
        """
        :param name_or_id: The unique identifier or the name of the API to update
        :type name_or_id: six.text_type | uuid.UUID
        :param upstream_url: The base target URL that points to your API server, this URL will be used for proxying
            requests. For example, https://mockbin.com.
        :type upstream_url: six.text_type
        :param fields: Optional dictionary which values will be used to overwrite the existing values
        :type fields: dict
        :rtype: dict
        :return: Dictionary containing the API description. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "name": "Mockbin",
                    "request_host": "mockbin.com",
                    "upstream_url": "http://mockbin.com",
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def delete(self, name_or_id):
        """
        :param name_or_id: The unique identifier or the name of the API to delete
        :type name_or_id: six.text_type | uuid.UUID
        """

    @abstractmethod
    def plugins(self, name_or_id):
        """
        :param name_or_id: The unique identifier or the name of the API to get the APIPluginAdminContract for
        :rtype: APIPluginConfigurationAdminContract
        :return:
        """


class BasicAuthAdminContract(CollectionMixin):
    __metaclass__ = ABCMeta

    @abstractmethod
    def destroy(self):
        """
        Releases all references, closes open connections, ...
        """

    @abstractmethod
    def count(self):
        """
        :rtype: int
        :return: Amount of records
        """

    @abstractmethod
    def create(self, username, password):
        """
        :param username: The username
        :type username: six.text_type
        :param password: The password
        :type password: six.text_type
        :rtype: dict
        :return: Dictionary containing the BasicAuth description. Example:
                {
                    password: "test2"
                    consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                    id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                    username: "dirk2"
                    created_at: 1438872669000
                }
        """

    @abstractmethod
    def create_or_update(self, basic_auth_id=None, username=None, password=None):
        """
        :param basic_auth_id: The unique identifier of the basic_auth info to update
        :type basic_auth_id: six.text_type | uuid.UUID
        :param username: The username
        :type username: six.text_type
        :param password: The password
        :type password: six.text_type
        :rtype: dict
        :return: Dictionary containing the BasicAuth description. Example:
                {
                    password: "test2"
                    consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                    id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                    username: "dirk2"
                    created_at: 1438872669000
                }
        """

    @abstractmethod
    def update(self, basic_auth_id, **fields):
        """
        :param basic_auth_id: The unique identifier of the basic_auth info to update
        :type basic_auth_id: six.text_type | uuid.UUID
        :param fields: Optional dictionary which values will be used to overwrite the existing values
        :type fields: dict
        :rtype: dict
        :return: Dictionary containing the BasicAuth description. Example:
                {
                    password: "test2"
                    consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                    id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                    username: "dirk2"
                    created_at: 1438872669000
                }
        """

    @abstractmethod
    def retrieve(self, basic_auth_id):
        """
        :param basic_auth_id: The unique identifier of the basic_auth info to retrieve
        :type basic_auth_id: six.text_type | uuid.UUID
        :rtype: dict
        :return: Dictionary containing the BasicAuth description. Example:
                {
                    password: "test2"
                    consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                    id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                    username: "dirk2"
                    created_at: 1438872669000
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
        :return: Dictionary containing dictionaries containing the BasicAuth description. Example:
                {
                   "data":[
                      {
                         "password":"test2",
                         "consumer_id":"abf8f0e5-753b-4eaa-ceff-a7c5187df4ff",
                         "id":"fe575378-162c-4c88-cc35-be456ad8d8a5",
                         "username":"dirk2",
                         "created_at":1438872669000
                      },
                      {
                         "password":"test",
                         "consumer_id":"abf8f0e5-753b-4eaa-ceff-a7c5187df4ff",
                         "id":"da982f37-1d15-4850-c89c-8e238adcb010",
                         "username":"dirk",
                         "created_at":1438872620000
                      }
                   ]
                }
        """

    @abstractmethod
    def delete(self, basic_auth_id):
        """
        :param basic_auth_id: The unique identifier of the basic_auth info to delete
        :type basic_auth_id: six.text_type | uuid.UUID
        """


class KeyAuthAdminContract(CollectionMixin):
    __metaclass__ = ABCMeta

    @abstractmethod
    def destroy(self):
        """
        Releases all references, closes open connections, ...
        """

    @abstractmethod
    def count(self):
        """
        :rtype: int
        :return: Amount of records
        """

    @abstractmethod
    def create(self, key=None):
        """
        :param key: You can optionally set your own unique key to authenticate the client. If missing, the plugin will
            generate one.
        :type key: six.text_type
        :rtype: dict
        :return: Dictionary containing the KeyAuth description. Example:
                {
                    consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                    id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                    key: "ahaiwdiaodyauodawyuiwoa7dwuaoadwhidwa"
                    created_at: 1438872669000
                }
        """

    @abstractmethod
    def create_or_update(self, key_auth_id=None, key=None):
        """
        :param key_auth_id: The unique identifier of the key_auth info to update
        :type key_auth_id: six.text_type | uuid.UUID
        :param key: You can optionally set your own unique key to authenticate the client. If missing, the plugin will
            generate one.
        :rtype: dict
        :return: Dictionary containing the KeyAuth description. Example:
                {
                    consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                    id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                    key: "ahaiwdiaodyauodawyuiwoa7dwuaoadwhidwa"
                    created_at: 1438872669000
                }
        """

    @abstractmethod
    def update(self, key_auth_id, **fields):
        """
        :param key_auth_id: The unique identifier of the key_auth info to update
        :type key_auth_id: six.text_type | uuid.UUID
        :param fields: Optional dictionary which values will be used to overwrite the existing values
        :type fields: dict
        :rtype: dict
        :return: Dictionary containing the KeyAuth description. Example:
                {
                    consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                    id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                    key: "ahaiwdiaodyauodawyuiwoa7dwuaoadwhidwa"
                    created_at: 1438872669000
                }
        """

    @abstractmethod
    def retrieve(self, key_auth_id):
        """
        :param key_auth_id: The unique identifier of the key_auth info to retrieve
        :type key_auth_id: six.text_type | uuid.UUID
        :rtype: dict
        :return: Dictionary containing the KeyAuth description. Example:
                {
                    consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                    id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                    key: "ahaiwdiaodyauodawyuiwoa7dwuaoadwhidwa"
                    created_at: 1438872669000
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
        :return: Dictionary containing dictionaries containing the KeyAuth description. Example:
                {
                   "data":[
                      {
                         consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                         id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                         key: "ahaiwdiaodyauodawyuiwoa7dwuaoadwhidwa"
                         created_at: 1438872669000
                      },
                      {
                         consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                         id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                         key: "ahaiwdiaodyauodawyuiwoa7dwuaoadwhidwa"
                         created_at: 1438872669000
                      }
                   ]
                }
        """

    @abstractmethod
    def delete(self, key_auth_id):
        """
        :param key_auth_id: The unique identifier of the key_auth info to delete
        :type key_auth_id: six.text_type | uuid.UUID
        """


class OAuth2AdminContract(CollectionMixin):
    __metaclass__ = ABCMeta

    @abstractmethod
    def destroy(self):
        """
        Releases all references, closes open connections, ...
        """

    @abstractmethod
    def count(self):
        """
        :rtype: int
        :return: Amount of records
        """

    @abstractmethod
    def create(self, name, redirect_uri, client_id=None, client_secret=None):
        """
        :param name: The name to associate to the credential. In OAuth 2.0 this would be the application name.
        :type name: six.text_type
        :param redirect_uri: The URL in your app where users will be sent after authorization (RFC 6742 Section 3.1.2)
        :type redirect_uri: six.text_type
        :param client_id: You can optionally set your own unique client_id. If missing, the plugin will generate one.
        :type client_id: six.text_type
        :param client_secret: You can optionally set your own unique client_secret. If missing, the plugin will
            generate one.
        :type client_secret: six.text_type
        :rtype: dict
        :return: Dictionary containing the OAuthAuth description. Example:
                {
                    consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                    id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                    name: "Test%20Application",
                    redirect_uri: "http://some-domain/endpoint/",
                    client_id: "SOME_CLIENT_ID",
                    client_secret: "SOME_CLIENT_SECRET",
                    created_at: 1438872669000
                }
        """

    @abstractmethod
    def create_or_update(self, oauth2_id=None, name=None, redirect_uri=None, client_id=None, client_secret=None):
        """
        :param oauth2_id: The unique identifier of the oauth2 info to update
        :type oauth2_id: six.text_type | uuid.UUID
        :param name: The name to associate to the credential. In OAuth 2.0 this would be the application name.
        :type name: six.text_type
        :param redirect_uri: The URL in your app where users will be sent after authorization (RFC 6742 Section 3.1.2)
        :type redirect_uri: six.text_type
        :param client_id: You can optionally set your own unique client_id. If missing, the plugin will generate one.
        :type client_id: six.text_type
        :param client_secret: You can optionally set your own unique client_secret. If missing, the plugin will
            generate one.
        :type client_secret: six.text_type
        :rtype: dict
        :return: Dictionary containing the OAuthAuth description. Example:
                {
                    consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                    id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                    name: "Test%20Application",
                    redirect_uri: "http://some-domain/endpoint/",
                    client_id: "SOME_CLIENT_ID",
                    client_secret: "SOME_CLIENT_SECRET",
                    created_at: 1438872669000
                }
        """

    @abstractmethod
    def update(self, oauth2_id, **fields):
        """
        :param oauth2_id: The unique identifier of the oauth2 info to update
        :type oauth2_id: six.text_type | uuid.UUID
        :param fields: Optional dictionary which values will be used to overwrite the existing values
        :type fields: dict
        :rtype: dict
        :return: Dictionary containing the OAuthAuth description. Example:
                {
                    consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                    id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                    name: "Test%20Application",
                    redirect_uri: "http://some-domain/endpoint/",
                    client_id: "SOME_CLIENT_ID",
                    client_secret: "SOME_CLIENT_SECRET",
                    created_at: 1438872669000
                }
        """

    @abstractmethod
    def retrieve(self, oauth2_id):
        """
        :param oauth2_id: The unique identifier of the oauth2 info to retrieve
        :type oauth2_id: six.text_type | uuid.UUID
        :rtype: dict
        :return: Dictionary containing the OAuthAuth description. Example:
                {
                    consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                    id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                    name: "Test%20Application",
                    redirect_uri: "http://some-domain/endpoint/",
                    client_id: "SOME_CLIENT_ID",
                    client_secret: "SOME_CLIENT_SECRET",
                    created_at: 1438872669000
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
        :return: Dictionary containing dictionaries containing the BasicAuth description. Example:
                {
                   "data":[
                      {
                          consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                          id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                          name: "Test%20Application",
                          redirect_uri: "http://some-domain/endpoint/",
                          client_id: "SOME_CLIENT_ID",
                          client_secret: "SOME_CLIENT_SECRET",
                          created_at: 1438872669000
                      },
                      {
                          consumer_id: "abf8f0e5-753b-4eaa-ceff-a7c5187df4ff"
                          id: "fe575378-162c-4c88-cc35-be456ad8d8a5"
                          name: "Test%20Application",
                          redirect_uri: "http://some-domain/endpoint/",
                          client_id: "SOME_CLIENT_ID",
                          client_secret: "SOME_CLIENT_SECRET",
                          created_at: 1438872669000
                      }
                   ]
                }
        """

    @abstractmethod
    def delete(self, oauth2_id):
        """
        :param oauth2_id: The unique identifier of the oauth2 info to delete
        :type oauth2_id: six.text_type | uuid.UUID
        """


class ConsumerAdminContract(CollectionMixin):
    __metaclass__ = ABCMeta

    @abstractmethod
    def destroy(self):
        """
        Releases all references, closes open connections, ...
        """

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
        :type username: six.text_type
        :param custom_id: Field for storing an existing ID for the consumer, useful for mapping Kong with users in your
            existing database. You must send either this field or username with the request.
        :type custom_id: six.text_type
        :rtype: dict
        :return: Dictionary containing the Consumer description. Example:
                {
                    "id": "4d924084-1adb-40a5-c042-63b19db421d1",
                    "custom_id": "abc123",
                    "created_at": 1422386534
                }
        """

    @abstractmethod
    def create_or_update(self, consumer_id=None, username=None, custom_id=None):
        """
        :param consumer_id: The unique identifier of the consumer to update
        :type consumer_id: six.text_type | uuid.UUID
        :param username: The username of the consumer. You must send either this field or custom_id with the request.
        :type username: six.text_type
        :param custom_id: Field for storing an existing ID for the consumer, useful for mapping Kong with users in your
            existing database. You must send either this field or username with the request.
        :type custom_id: six.text_type
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
        :type username_or_id: six.text_type | uuid.UUID
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
        :type username_or_id: six.text_type | uuid.UUID
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
        :type username_or_id: six.text_type | uuid.UUID
        """

    @abstractmethod
    def basic_auth(self, username_or_id):
        """
        Returns a "Basic Auth" manager for a given consumer

        :param username_or_id: The unique identifier or the name of the consumer
        :rtype BasicAuthAdminContract
        :return:
        """

    @abstractmethod
    def key_auth(self, username_or_id):
        """
        Returns a "Key Auth" manager for a given consumer

        :param username_or_id: The unique identifier or the name of the consumer
        :rtype KeyAuthAdminContract
        :return:
        """

    @abstractmethod
    def oauth2(self, username_or_id):
        """
        Returns a "OAuth2" manager for a given consumer

        :param username_or_id: The unique identifier or the name of the consumer
        :rtype OAuth2AdminContract
        :return:
        """


class PluginAdminContract(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def destroy(self):
        """
        Releases all references, closes open connections, ...
        """

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
        :type plugin_name: six.text_type
        :rtype: dict
        :return: Returns the schema of a plugin's configuration.
        """


class KongAdminContract(with_metaclass(ABCMeta, object)):
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

    @abstractmethod
    def close(self):
        """
        Close all connections if applicable
        :return:
        """
