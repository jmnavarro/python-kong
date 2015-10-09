# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

"""
By default, we use the standard library’s ssl module. Unfortunately, there are several limitations which are addressed
by PyOpenSSL:

    (Python 2.x) SNI support.
    (Python 2.x-3.2) Disabling compression to mitigate CRIME attack. (https://en.wikipedia.org/wiki/CRIME)

To use the Python OpenSSL bindings instead, you’ll need to install the required packages:

    $ pip install pyopenssl ndg-httpsclient pyasn1

If cryptography fails to install as a dependency, make sure you have libffi available on your system and run pip install
cryptography.

Once the packages are installed, you can tell urllib3 to switch the ssl backend to PyOpenSSL with inject_into_urllib3().

Source: https://urllib3.readthedocs.org/en/latest/security.html#openssl-pyopenssl
"""
try:  # pragma: no cover
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass

__version__ = '0.4.0'
