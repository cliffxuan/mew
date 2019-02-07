# -*- coding: utf-8 -*-
import datetime as dt
import re

from mew import __version__


def test_version():
    # no double digit
    assert re.match(r"\d\.\d\.\d", __version__.__version__)


def test_copyright():
    year = dt.date.today().year
    assert f"Copyright {year} Cliff Xuan" == __version__.__copyright__
