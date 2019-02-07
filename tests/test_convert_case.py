# -*- coding: utf-8 -*-
import pytest
from mew.convert_case import (
    to_pascal_case,
    from_pascal_case,
    to_camel_case,
    from_camel_case,
)


@pytest.mark.parametrize(
    "pascal, snake",
    [
        ("PascalCase", "pascal_case"),
        ("PascalPascalCase", "pascal_pascal_case"),
        ("Pascal2Pascal2Case", "pascal2_pascal2_case"),
        ("HttpResponseCode", "http_response_code"),
        ("HttpResponseCodeXyz", "http_response_code_xyz")
        # these cannot be converted
        #  ('HTTPResponseCode', 'http_response_code'),
        #  ('HTTPResponseCodeXYZ', 'http_response_code_xyz')
    ],
)
def test_pascal_and_snake_case_conversion(pascal, snake):
    assert pascal == to_pascal_case(snake)
    assert snake == from_pascal_case(pascal)


@pytest.mark.parametrize(
    "camel, snake",
    [
        ("camelCase", "camel_case"),
        ("camelCamelCase", "camel_camel_case"),
        ("camel2Camel2Case", "camel2_camel2_case"),
        ("getHttpResponseCode", "get_http_response_code"),
        ("get2HttpResponseCode", "get2_http_response_code"),
    ],
)
def test_camel_and_snake_case_conversion(camel, snake):
    assert camel == to_camel_case(snake)
    assert snake == from_camel_case(camel)
