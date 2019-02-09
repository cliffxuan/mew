#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
from dataclasses import is_dataclass
import enum
import typing

from mew.serializer import dumps, loads, SCALAR_TYPES


class NotSupported(Exception):
    """not supported"""

    def __init__(self, types, message):
        self.types = types
        self.message = message


def is_namedtuple(t):
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple:
        return False
    f = getattr(t, "_fields", None)
    if not isinstance(f, tuple):
        return False
    return all(type(n) == str for n in f)


def find_unsupported(t: typing.Any) -> typing.List[typing.Any]:
    if t in SCALAR_TYPES:
        return []
    if isinstance(t, type):  # if it's a class
        if issubclass(t, enum.Enum):
            return []
        if is_dataclass(t):
            return [
                v.type
                for v in t.__dataclass_fields__.values()
                if find_unsupported(v.type)
            ]
        if is_namedtuple(t) and hasattr(t, "_field_types"):
            # yes: class Point(typing.NamedTuple):
            #          x: int
            #          y: int
            # no: Point = namedtuple('Point', ['x', 'y'])
            return [v for v in t._field_types.values() if find_unsupported(v)]
    if hasattr(t, "__origin__"):  # if it's a type in typing module
        origin = t.__origin__
        if origin == typing.Union:
            return [arg for arg in t.__args__ if find_unsupported(arg)]
        if origin in (list, typing.List):  # typing.List for python3.6
            return find_unsupported(t.__args__[0])
        # TODO covert more of typing.XXX
    return [t]


def serializable(t):
    """adds dumps() and loads() to the class"""
    unsupported_types = find_unsupported(t)
    if unsupported_types:
        raise NotSupported(unsupported_types, f"unsupported type {unsupported_types}")
    t.dumps = dumps
    t.loads = classmethod(loads)
    return t
