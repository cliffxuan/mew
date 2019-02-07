# -*- coding: utf-8 -*-
import re

CAP_RE = re.compile("(.)([A-Z])")


def to_pascal_case(name):
    """
    Turn a snake_case name into PascalCase.
    """
    return name.title().replace("_", "")


def from_pascal_case(name):
    """
    Turn a PascalCase name into snake_case.
    """
    return CAP_RE.sub(r"\1_\2", name).lower()


def to_camel_case(name):
    """
    Turn a snake_case name into camelCase.
    """
    output = name.title().replace("_", "")
    return output[0].lower() + output[1:]


def from_camel_case(name):
    """
    Turn a camelCase name into snake_case.
    """
    return from_pascal_case(name)
