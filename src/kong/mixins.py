# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from abc import ABCMeta, abstractmethod

from six import with_metaclass

from .utils import parse_query_parameters


class CollectionMixin(with_metaclass(ABCMeta, object)):
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
        :return: Dictionary containing dictionaries
        """

    def iterate(self, window_size=10, **filter_fields):
        current_offset = None
        while True:
            response = self.list(size=window_size, offset=current_offset, **filter_fields)
            for item in response['data']:
                yield item
            next_url = response.get('next', None)
            if next_url is None:
                return
            current_offset = parse_query_parameters(next_url).get('offset')[0]
