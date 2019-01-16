# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
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


pikachu = Pokemon('Pikachu', 25, Type.electric, ['static', 'lightning rod'])

blob = pikachu.to_blob()
pikachu_from_blob = Pokemon.from_blob(blob)
assert pikachu == pikachu_from_blob
