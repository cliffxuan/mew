#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
from dataclasses import is_dataclass
import datetime as dt
import enum
import typing
import uuid

from mew.serializer import dumps, loads


class NotSupported(Exception):
    """not supported"""

    def __init__(self, types, message):
        self.types = types
        self.message = message


scalar_types = [str, int, float, bool, type(None)]
directly_supported_types = [
    uuid.UUID,
    dt.datetime,
    *scalar_types,
]


def is_namedtuple(t):
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple:
        return False
    f = getattr(t, "_fields", None)
    if not isinstance(f, tuple):
        return False
    return all(type(n) == str for n in f)


def find_unsupported(t) -> typing.List[typing.Any]:
    if t in directly_supported_types:
        return []
    if isinstance(t, type):  # if it's a class
        if issubclass(t, enum.Enum):
            return []
        if is_dataclass(t):
            unsupported = [
                v.type
                for v in t.__dataclass_fields__.values()
                if find_unsupported(v.type)
            ]
            return unsupported
        if is_namedtuple(t):
            unsupported = [
                v
                for v in t._field_types.values()
                if find_unsupported(v)
            ]
            return unsupported
    if hasattr(t, "__origin__"):  # if it's a type in typing module
        origin = t.__origin__
        if origin == typing.Union:
            unsupported = [
                arg
                for arg in t.__args__
                if find_unsupported(arg)
            ]
            return unsupported
        if origin == list:
            return find_unsupported(t.__args__[0])
        # TODO covert more of typing.XXX
        return [t]
    return [t]


def serializable(t):
    """adds dumps() and loads() to the class"""
    unsupported_types = find_unsupported(t)
    if unsupported_types:
        # TODO specified which types are not supported
        raise NotSupported(
            unsupported_types, f"unsupported type {unsupported_types}"
        )
    t.dumps = dumps
    t.loads = classmethod(loads)
    return t
