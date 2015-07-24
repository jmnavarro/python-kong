# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

try:
    from http.client import OK, CREATED, CONFLICT, NO_CONTENT
except ImportError:
    # For python <= 2.6
    from httplib import OK, CREATED, CONFLICT, NO_CONTENT
