# -*- coding: utf-8 -*-
import typing

from hypothesis import given
from hypothesis import strategies as st

from mew.serializer import dumps, loads, StringSerializer, IntSerializer


@given(st.text())
def test_string_serializer(text):
    assert StringSerializer.serialize(text) == text
    assert StringSerializer.deserialize(text) == text


@given(st.integers())
def test_int_serializer(integer):
    assert IntSerializer.serialize(integer) == integer
    assert IntSerializer.deserialize(integer) == integer


def test_dumps_yaml():
    origin = ['foo', 'bar']
    result = dumps(origin, format='yaml', default_flow_style=False)
    assert result == '- foo\n- bar\n'
    assert loads(typing.List[str], result, format='yaml') == origin
