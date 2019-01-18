# -*- coding: utf-8 -*-
import datetime as dt
import enum
import json
import uuid
from collections.abc import Collection, Mapping
from typing import Any, Callable, Union

from dataclasses import asdict, is_dataclass

UTC = dt.timezone.utc


def serialize(
    obj: Any,
    convert_key: Callable = lambda x: x,
) -> Any:
    """
    Takes an object and returns a representation of that object
    that can be json encoded. If no special behaviour is known
    for the object then the object itself will be returned unless
    a default conversion function has been provided.
    """
    # Format as "10fb6968-6b54-44c8-9365-e0b3934ae156".
    if isinstance(obj, uuid.UUID):
        return str(obj)

    # Format datetimes as ISO-8601 w/ timezone.
    if isinstance(obj, dt.datetime):
        return obj.isoformat()

    # Serialise enums to their value.
    if isinstance(obj, enum.Enum):
        return obj.value

    # Recursively serialise dictionaries.
    if isinstance(obj, Mapping):
        # TODO this is assuming k is a string
        return {
            convert_key(k): serialize(v, convert_key)
            for k, v in obj.items()
        }

    # Convert dataclass instance as dict
    if is_dataclass(obj) and not isinstance(obj, type):
        return serialize(asdict(obj), convert_key)

    # Recursively serialise stuff that looks like a list or set.
    if isinstance(obj, Collection) and not isinstance(obj, str):
        return [serialize(i, convert_key) for i in obj]

    return obj


# TODO type annotate t
# TODO code example to use
def deserialize(t, value, convert_key: Callable = lambda x: x):
    if t in [str, int, float, bool, type(None)]:
        return value

    if t == uuid.UUID:
        return uuid.UUID(value)

    if t == dt.datetime:
        return dt.datetime.fromisoformat(value)

    if is_dataclass(t):
        return t(
            **{
                # TODO parameterize from_pascal_case
                convert_key(k): deserialize(
                    t.__dataclass_fields__[convert_key(k)].type,
                    v,
                    convert_key
                )
                for k, v in value.items()
            }
        )

    if isinstance(t, type):
        if issubclass(t, enum.Enum):
            for item in t:
                if item.value == value:
                    return item
            raise Exception(
                f"cannot find an item in Enum {t} with value {value}"
            )
        if issubclass(t, tuple):
            return t(*value)

    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        origin = t.__origin__
        args = t.__args__
        if origin == list:
            return [deserialize(args[0], item, convert_key) for item in value]
        if origin == Union:
            for arg in args:
                try:
                    return deserialize(arg, value, convert_key)
                except TypeError:
                    pass
            raise Exception(
                f"cannot convert type {t} for value {value}"
            )
        # TODO convert more of type.XXX
    raise Exception(f"unsupported type {t} for value {value}")


def dumps(o, *args, **kwargs):
    convert_key = kwargs.pop('convert_key', lambda x: x)
    serialized = serialize(o, convert_key=convert_key)
    return json.dumps(serialized, *args, **kwargs)


def loads(t, data, convert_key: Callable = lambda x: x):
    data_asdict = json.loads(data)
    return deserialize(t, data_asdict, convert_key)
