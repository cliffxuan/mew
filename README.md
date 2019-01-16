Mew: python dataclass serializer/deserializer
=============================================
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

>>> pikachu.to_blob()
'{"name": "Pikachu", "pokedex": 25, "type": "electric", "abilities": ["static", "lightning rod"]}'

>>> assert pikachu == Pokemon.from_blob(pikachu.to_blob())
```
