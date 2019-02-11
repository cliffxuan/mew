# -*- coding: utf-8 -*-
import datetime as dt
import enum
import json
import sys
import uuid
from abc import ABC, abstractmethod
from collections.abc import Collection, Mapping
from typing import Any, Callable, Dict, List, Tuple, Union
from dataclasses import asdict, is_dataclass

import yaml

if sys.version_info < (3, 7):
    # fromisoformat() is for python version >= 3.7
    from backports.datetime_fromisoformat import MonkeyPatch

    MonkeyPatch.patch_fromisoformat()


NoneType = type(None)
SUPPORTED_FORMATS = ("json", "yaml")

PRIMITIVE_TYPES = (str, int, float, bool, type(None))
SCALAR_TYPES = (uuid.UUID, dt.date, dt.datetime, dt.time, *PRIMITIVE_TYPES)


class ScalarTypeSerializer(ABC):
    @property
    @classmethod
    @abstractmethod
    def type(cls):
        ...

    @abstractmethod
    def serialize(obj: "ScalarTypeSerializer.type"):
        ...

    @staticmethod
    @abstractmethod
    def deserialize(value) -> "ScalarTypeSerializer.type":
        ...


class StringSerializer(ScalarTypeSerializer):

    type = str

    @staticmethod
    def serialize(obj: str) -> str:
        return obj

    @staticmethod
    def deserialize(value: str) -> str:
        return value


class IntSerializer(ScalarTypeSerializer):

    type = int

    @staticmethod
    def serialize(obj: int) -> int:
        return obj

    @staticmethod
    def deserialize(value: int) -> int:
        return value


class FloatSerializer(ScalarTypeSerializer):

    type = float

    @staticmethod
    def serialize(obj: float) -> float:
        return obj

    @staticmethod
    def deserialize(value: float) -> float:
        return value


class BooleanSerializer(ScalarTypeSerializer):

    type = bool

    @staticmethod
    def serialize(obj: bool) -> bool:
        return obj

    @staticmethod
    def deserialize(value: bool) -> bool:
        return value


class NoneTypeSerializer:

    type = NoneType

    @staticmethod
    def serialize(obj: NoneType) -> NoneType:
        return obj

    @staticmethod
    def deserialize(value: NoneType) -> NoneType:
        return value


class UUIDSerializer(ScalarTypeSerializer):
    type = uuid.UUID

    @staticmethod
    def serialize(obj: uuid.UUID) -> str:
        # Format as "10fb6968-6b54-44c8-9365-e0b3934ae156".
        return str(obj)

    @staticmethod
    def deserialize(value: str) -> dt.datetime:
        return uuid.UUID(value)


class DateTimeSerializer(ScalarTypeSerializer):
    type = dt.datetime

    @staticmethod
    def serialize(obj: dt.datetime) -> str:
        # Format datetimes as ISO-8601 w/ timezone.
        return obj.isoformat()

    @staticmethod
    def deserialize(value: str) -> dt.datetime:
        return dt.datetime.fromisoformat(value)


class DateSerializer(ScalarTypeSerializer):

    type = dt.date

    @staticmethod
    def serialize(obj: dt.date) -> str:
        # Format date as YYYY-MM-DD
        return obj.isoformat()

    @staticmethod
    def deserialize(value: str) -> dt.date:
        return dt.date.fromisoformat(value)


class TimeSerializer(ScalarTypeSerializer):

    type = dt.time

    @staticmethod
    def serialize(obj: dt.time) -> str:
        # Format date as HH:MM:SS
        return obj.isoformat()

    @staticmethod
    def deserialize(value: str) -> dt.date:
        return dt.time.fromisoformat(value)


#  class EnumSerializer(ScalarTypeSerializer):
#      type: enum.Enum

#      @staticmethod
#      def serialize(obj: enum.Enum) -> Any:
#          # Serialise enums to their value.
#          # TODO value may not be serializable
#          return obj.value

#      @staticmethod
#      def deserialize(value: Any) -> enum.Enum:


class MultiTypeSerializer:

    default_serializers: Tuple[ScalarTypeSerializer] = (
        StringSerializer,
        IntSerializer,
        FloatSerializer,
        BooleanSerializer,
        NoneTypeSerializer,
        UUIDSerializer,
        DateTimeSerializer,
        DateSerializer,
        TimeSerializer,
    )

    def __init__(self):
        self.serializers: Dict[type, ScalarTypeSerializer] = {
            serializer.type: serializer for serializer in self.default_serializers
        }

    def serialize(self, obj: Any, convert_key: Callable = lambda x: x) -> Any:
        for t in self.serializers:
            if isinstance(obj, t):
                return self.serializers[t].serialize(obj)

        # Serialise enums to their value.
        if isinstance(obj, enum.Enum):
            return obj.value

        # Recursively serialise dictionaries.
        if isinstance(obj, Mapping):
            # TODO this is assuming k is a string
            return {
                convert_key(k): self.serialize(v, convert_key) for k, v in obj.items()
            }

        # Convert dataclass instance as dict
        if is_dataclass(obj) and not isinstance(obj, type):
            return self.serialize(asdict(obj), convert_key)

        # Recursively serialise stuff that looks like a list or set.
        if isinstance(obj, Collection) and not isinstance(obj, str):
            return [self.serialize(i, convert_key) for i in obj]

        # TODO raise exception instead?
        return obj

    def deserialize(
        self, t: Any, value: Any, convert_key: Callable = lambda x: x
    ) -> Any:
        if t in self.serializers:
            return self.serializers[t].deserialize(value)
        if is_dataclass(t):
            return t(
                **{
                    convert_key(k): self.deserialize(
                        t.__dataclass_fields__[convert_key(k)].type, v, convert_key
                    )
                    for k, v in value.items()
                }
            )

        if isinstance(t, type):
            if issubclass(t, enum.Enum):
                for item in t:
                    if item.value == value:
                        return item
                raise Exception(f"cannot find an item in Enum {t} with value {value}")
            if issubclass(t, tuple):
                return t(*value)

        if hasattr(t, "__origin__") and hasattr(t, "__args__"):
            origin = t.__origin__
            args = t.__args__
            if origin in (list, List):
                return [self.deserialize(args[0], item, convert_key) for item in value]
            if origin == Union:
                for arg in args:
                    try:
                        return self.deserialize(arg, value, convert_key)
                    except TypeError:
                        pass
                raise Exception(f"cannot convert type {t} for value {value}")
            # TODO convert more of type.XXX
        raise Exception(f"unsupported type {t} for value {value}")


# TODO validate
# types may not match
def dumps(o, *, format: str = "json", convert_key: Callable = lambda x: x, **kwargs):
    #  serialized = serialize(o, convert_key=convert_key)
    serialized = MultiTypeSerializer().serialize(o, convert_key=convert_key)
    if format == "json":
        return json.dumps(serialized, **kwargs)
    if format == "yaml":
        return yaml.dump(serialized, **kwargs)
    raise ValueError(
        f'supported formats are {",".join(SUPPORTED_FORMATS)}.' f" found {format}"
    )


def loads(t, data, format: str = "json", convert_key: Callable = lambda x: x):
    if format == "json":
        data_asdict = json.loads(data)
    elif format == "yaml":
        data_asdict = yaml.load(data)
    else:
        raise ValueError(
            f'supported formats are {",".join(SUPPORTED_FORMATS)}.' f" found {format}"
        )
    #  return deserialize(t, data_asdict, convert_key)
    return MultiTypeSerializer().deserialize(t, data_asdict, convert_key)
