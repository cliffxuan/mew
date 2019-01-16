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


def to_blob(self, *args, **kwargs) -> str:
    return dumps(self, *args, **kwargs)


def from_blob(cls, data: str):
    return loads(data, cls)


def is_namedtuple(t):
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple:
        return False
    f = getattr(t, "_fields", None)
    if not isinstance(f, tuple):
        return False
    return all(type(n) == str for n in f)


def is_serializable(klass):
    if klass in directly_supported_types:
        return True
    if is_dataclass(klass):
        return all(
            is_serializable(v.type)
            for v in klass.__dataclass_fields__.values()
        )
    if isinstance(klass, type):  # if it's a class
        if issubclass(klass, enum.Enum):
            return True
        if is_namedtuple(klass):
            return all(is_serializable(v) for v in klass._field_types.values())
    if hasattr(klass, "__origin__"):
        origin = klass.__origin__
        if origin == typing.Union:
            return all(is_serializable(arg) for arg in klass.__args__)
        if origin == list:
            return is_serializable(klass.__args__[0])
        # TODO more
        return False
    return False


def serializable(klass):
    if not is_serializable(klass):
        raise NotSupported(f"unsupported types")
    klass.to_blob = to_blob
    klass.from_blob = classmethod(from_blob)
    return klass
