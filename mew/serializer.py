# -*- coding: utf-8 -*-
import datetime as dt
import enum
import json
import re
import uuid
from collections.abc import Collection, Mapping
from typing import Any, Callable, Union

from dataclasses import asdict, is_dataclass

UTC = dt.timezone.utc


def serialize(
    obj: Any,
    convert_case: Callable = lambda x: x,
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
            convert_case(k): serialize(v, convert_case)
            for k, v in obj.items()
        }

    # Convert dataclass instance as dict
    if is_dataclass(obj) and not isinstance(obj, type):
        return serialize(asdict(obj), convert_case)

    # Recursively serialise stuff that looks like a list or set.
    if isinstance(obj, Collection) and not isinstance(obj, str):
        return [serialize(i, convert_case) for i in obj]

    return obj


def deserialize(value, annotation):
    if annotation in [str, int, float, bool, type(None)]:
        return value

    if annotation == uuid.UUID:
        return uuid.UUID(value)

    if annotation == dt.datetime:
        return dt.datetime.fromisoformat(value)

    if is_dataclass(annotation):
        return annotation(
            **{
                from_pascal_case(k): deserialize(
                    v,
                    annotation.__dataclass_fields__[from_pascal_case(k)].type,
                )
                for k, v in value.items()
            }
        )

    if isinstance(annotation, type):
        if issubclass(annotation, enum.Enum):
            for item in annotation:
                if item.value == value:
                    return item
            raise Exception(
                f"cannot find an item in Enum {annotation} with value {value}"
            )
        if issubclass(annotation, tuple):
            return annotation(*value)

    if hasattr(annotation, "__origin__") and hasattr(annotation, "__args__"):
        origin = annotation.__origin__
        args = annotation.__args__
        if origin == list:
            return [deserialize(item, args[0]) for item in value]
        if origin == Union:
            for arg in args:
                try:
                    return deserialize(value, arg)
                except TypeError:
                    pass
            raise Exception(
                f"cannot convert type {annotation} for value {value}"
            )
        # TODO more...
    raise Exception(f"unsupported type {annotation} for value {value}")


def dumps(o, *args, **kwargs):
    convert_case = kwargs.pop('convert_case', lambda x: x)
    serialized = serialize(o, convert_case=convert_case)
    return json.dumps(serialized, *args, **kwargs)


def loads(data, annotation):
    data_asdict = json.loads(data)
    return deserialize(data_asdict, annotation)


def to_pascal_case(name):
    """
    Turn a Pythonic attribute name into PascalCase.
    """
    return name.title().replace("_", "")


def from_pascal_case(name):
    """
    Turn a PascalCase attribute name into Pythonic name.
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
