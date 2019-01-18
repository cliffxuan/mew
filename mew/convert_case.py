#!/usr/bin/env python
import re


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
