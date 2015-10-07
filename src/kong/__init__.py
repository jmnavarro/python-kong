# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

try:  # pragma: no cover
    # https://urllib3.readthedocs.org/en/latest/security.html#pyopenssl
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass

__version__ = '0.3.2'
