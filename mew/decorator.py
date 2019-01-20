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

    def __init__(self, _type, message):
        self.type = _type
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


# TODO make return type a custom class
def is_serializable(t) -> typing.Tuple[bool, typing.Optional[typing.Any]]:
    if t in directly_supported_types:
        return True, None
    if is_dataclass(t):
        unsupported = [
            v
            for v in t.__dataclass_fields__.values()
            if not is_serializable(v.type)[0]
        ]
        if unsupported:
            return False, unsupported[0].type
        else:
            return True, None
    if isinstance(t, type):  # if it's a class
        if issubclass(t, enum.Enum):
            return True, None
        if is_namedtuple(t):
            unsupported = [
                v
                for v in t._field_types.values()
                if not is_serializable(v)[0]
            ]
            if unsupported:
                return False, unsupported[0]
            else:
                return True, None
    if hasattr(t, "__origin__"):  # if it's a type in typing module
        origin = t.__origin__
        if origin == typing.Union:
            unsupported = [
                arg
                for arg in t.__args__
                if not is_serializable(arg)[0]
            ]
            if unsupported:
                return False, unsupported[0]
            else:
                return True, None
        if origin == list:
            return is_serializable(t.__args__[0])
        # TODO covert more of typing.XXX
        return False, t
    return False, t


def serializable(t):
    """adds dumps() and loads() to the class"""
    is_ok, unsupported = is_serializable(t)
    if not is_ok:
        # TODO specified which types are not supported
        raise NotSupported(unsupported, f"unsupported type {unsupported}")
    t.dumps = dumps
    t.loads = classmethod(loads)
    return t
