# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

try:
    from http.client import OK, CREATED, CONFLICT, NO_CONTENT
except ImportError:
    from httplib import OK, CREATED, CONFLICT, NO_CONTENT

try:
    from urllib.parse import urlparse, urljoin, urlencode, unquote, parse_qsl, ParseResult
except ImportError:
    from urlparse import urlparse, urljoin, parse_qsl, ParseResult
    from urllib import urlencode, unquote

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

try:
    from unittest import TestCase, skipIf, main as run_unittests
except ImportError:
    from unittest2 import TestCase, skipIf, main as run_unittests
