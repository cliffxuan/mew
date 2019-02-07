Mew: python dataclass serializer/deserializer
=============================================
[![Build Status](https://travis-ci.org/cliffxuan/mew.svg?branch=master)](https://travis-ci.org/cliffxuan/mew)
[![Python Version Support](https://img.shields.io/pypi/pyversions/mew.svg)](https://img.shields.io/pypi/pyversions/mew.svg)
[![PyPI Version](https://badge.fury.io/py/mew.svg)](https://badge.fury.io/py/mew)
[![Coverage](https://img.shields.io/codeclimate/coverage/cliffxuan/mew.svg?style=flat)](https://codeclimate.com/github/cliffxuan/mew)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
![image](https://raw.githubusercontent.com/cliffxuan/mew/master/mew.jpg)

``` {.sourceCode .python}
from dataclasses import dataclass
from enum import Enum
from typing import List

import mew


class Type(Enum):
    normal = 'normal'
    electric = 'electric'
    fire = 'fire'
    fighting = 'fighting'
    water = 'water'
    psychic = 'psychic'


@mew.serializable
@dataclass
class Pokemon:
    name: str
    pokedex: int
    type: Type
    abilities: List[str]


>>> pikachu = Pokemon('Pikachu', 25, Type.electric, ['static', 'lightning rod'])

>>> pikachu
Pokemon(name='Pikachu', pokedex=25, type=<Type.electric: 'electric'>, abilities=['static', 'lightning rod'])

>>> pikachu.dumps()
'{"name": "Pikachu", "pokedex": 25, "type": "electric", "abilities": ["static", "lightning rod"]}'

>>> assert pikachu == Pokemon.loads(pikachu.dumps())
```
