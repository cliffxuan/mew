# -*- coding: utf-8 -*-
from dataclasses import dataclass
from enum import Enum
from typing import List

import mew


class Type(Enum):
    normal = "normal"
    electric = "electric"
    fire = "fire"
    fighting = "fighting"
    water = "water"
    psychic = "psychic"


@mew.serializable
@dataclass
class Pokemon:
    name: str
    pokedex: int
    type: Type
    abilities: List[str]


pikachu = Pokemon(
    name="Pikachu",
    pokedex=25,
    type=Type.electric,
    abilities=["static", "lightning rod"],
)

blob = pikachu.dumps()
pikachu_from_blob = Pokemon.loads(blob)
assert pikachu == pikachu_from_blob
