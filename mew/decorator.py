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


def is_serializable(t):
    if t in directly_supported_types:
        return True
    if is_dataclass(t):
        return all(
            is_serializable(v.type)
            for v in t.__dataclass_fields__.values()
        )
    if isinstance(t, type):  # if it's a class
        if issubclass(t, enum.Enum):
            return True
        if is_namedtuple(t):
            return all(is_serializable(v) for v in t._field_types.values())
    if hasattr(t, "__origin__"):  # if it's a type in typing module
        origin = t.__origin__
        if origin == typing.Union:
            return all(is_serializable(arg) for arg in t.__args__)
        if origin == list:
            return is_serializable(t.__args__[0])
        # TODO more
        return False
    return False


def serializable(t):
    if not is_serializable(t):
        # TODO specified which types are not supported
        raise NotSupported(f"unsupported types")
    t.dumps = dumps
    t.loads = classmethod(loads)
    return t
