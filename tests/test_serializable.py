# -*- coding: utf-8 -*-
import datetime as dt
import typing
import uuid
from dataclasses import dataclass, field
from enum import Enum

import pytest
from hypothesis import given, note, settings
from hypothesis import strategies as st
from hypothesis.extra.dateutil import timezones

from mew import NotSupported, serializable, to_pascal_case, from_pascal_case


def test_not_supported():

    with pytest.raises(NotSupported):

        @serializable
        class Foo:
            name: typing.Callable


# TODO generate types?
class GeoPosition(typing.NamedTuple):
    latitude: float
    longitude: float


class Subject(Enum):
    mathmatics = 0
    english = 1
    computing = 2


@serializable
@dataclass
class Address:
    id: uuid.UUID
    door_number: int
    house_name: typing.Optional[str]
    street_name: str
    geo_position: GeoPosition


@serializable
@dataclass
class Teacher:
    id: uuid.UUID
    name: str
    address: Address


@serializable
@dataclass
class Lecture:
    id: uuid.UUID
    name: int
    timestamp: dt.datetime
    teacher: Teacher
    subject: Subject


@serializable
@dataclass
class Student:
    id: uuid.UUID
    name: str
    address: Address
    lectures: typing.List[Lecture] = field(default_factory=list)


@st.composite
def geo_positions(
    draw,
    latitude=st.floats(min_value=-90, max_value=90),
    longitude=st.floats(min_value=0, max_value=180),
) -> GeoPosition:
    return GeoPosition(draw(latitude), draw(longitude))


@st.composite
def address(
    draw,
    id=st.uuids(),
    door_number=st.integers(),
    house_name=st.one_of(st.text() | st.none()),
    street_name=st.text(),
    geo_position=geo_positions(),
) -> Address:
    return Address(
        draw(id),
        draw(door_number),
        draw(house_name),
        draw(street_name),
        draw(geo_position),
    )


@st.composite
def timestamps(
    draw, timestamp=st.datetimes(timezones=timezones())
) -> dt.datetime:
    return draw(timestamp)


@st.composite
def teacher(draw, id=st.uuids(), name=st.text(), address=address()) -> Teacher:
    return Teacher(draw(id), draw(name), draw(address))


@st.composite
def lecture(
    draw,
    id=st.uuids(),
    name=st.text(),
    timestamp=timestamps(),
    teacher=teacher(),
    subject=st.sampled_from(Subject),
) -> Lecture:
    return Lecture(
        draw(id),
        draw(name),
        draw(timestamp),
        draw(teacher),
        draw(subject),
    )


@st.composite
def student(
    draw, id=st.uuids(), name=st.text(), address=address(), lecture=lecture()
) -> Student:
    lectures = draw(st.lists(lecture, max_size=5))
    return Student(draw(id), draw(name), draw(address), lectures)


@given(address())
def test_address(address):
    blob = address.dumps(convert_key=to_pascal_case)
    # make sure all keys are included and with the correct case
    assert "DoorNumber" in blob
    assert "HouseName" in blob
    assert "StreetName" in blob
    assert address == Address.loads(blob, convert_key=from_pascal_case)


@given(teacher())
def test_teacher(teacher):
    blob = teacher.dumps(convert_key=to_pascal_case)
    # parent keys
    assert "Id" in blob
    assert "Name" in blob
    assert "Address" in blob
    # child keys
    assert "DoorNumber" in blob
    assert "HouseName" in blob
    assert "StreetName" in blob
    assert teacher == Teacher.loads(
        teacher.dumps(),
        convert_key=from_pascal_case
    )


@given(lecture())
def test_lecture(lecture):
    blob = lecture.dumps(convert_key=to_pascal_case)
    # parent keys
    assert "Id" in blob
    assert "Name" in blob
    assert "Address" in blob
    # child keys
    assert "DoorNumber" in blob
    assert "HouseName" in blob
    assert "StreetName" in blob
    assert lecture == Lecture.loads(blob, convert_key=from_pascal_case)


@given(student())
@settings(max_examples=16)
def test_student(student):
    blob = student.dumps()
    note(f"student: {student}")
    assert student == Student.loads(blob, convert_key=from_pascal_case)
