
Changelog
=========

0.4.0 (2015-10-09)
------------------

* Changed 'add' to 'create' and 'add_or_update' to 'create_or_update' (WARNING: Not backwards compatible!)
* Code cleanup

0.3.2 (2015-10-07)
------------------

* Updated contract docstrings to explicitly support 'six.text_type' instead of 'str'

0.3.1 (2015-09-23)
------------------

* Now supporting 'preserve_host' and 'strip_request_path' options

0.3.0 (2015-09-22)
------------------

* Updated library again to be compatible with Kong 0.5.x (WARNING: Not backwards compatible!)

0.2.0 (2015-09-09)
------------------

* Updated library to be compatible with Kong 0.5.x (WARNING: Not backwards compatible!)

0.1.14 (2015-08-26)
-------------------

* Added some error checks

0.1.13 (2015-08-26)
-------------------

* Small bugfix

0.1.12 (2015-08-20)
-------------------

* Implemented retrieve api for APIPluginConfigurationAdminContract

0.1.11 (2015-08-19)
-------------------

* Implemented close method for KongAdminContract

0.1.10 (2015-08-18)
-------------------

* Implemented Basic Auth credentials API's
* Implemented Key authentication API's
* Implemented OAuth2 API's

0.1.9 (2015-08-06)
------------------

* Improved error handling in client

0.1.8 (2015-08-06)
------------------

* Bugfixes

0.1.7 (2015-07-30)
------------------

* Implemented APIAdminContract.add_or_update API
* Implemented APIPluginConfigurationAdminContract.create_or_update API
* Implemented ConsumerAdminContract.create_or_update API

0.1.6 (2015-07-28)
------------------

* Updated KongAdminSimulator constructor to accept api_url

0.1.5 (2015-07-28)
------------------

* Added CollectionMixin to contract (abstract base classes)

0.1.4 (2015-07-28)
------------------

* Bugfix related to checking for API conflicts

0.1.3 (2015-07-28)
------------------

* Added more tests and 'CollectionMixin' that exposes an 'iterate' api

0.1.2 (2015-07-27)
------------------

* Implemented 'plugin configuration' update API

0.1.1 (2015-07-24)
------------------

* Package structure updated

0.1.0 (2015-07-23)
------------------

* First release on PyPI.
