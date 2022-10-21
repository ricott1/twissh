from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from .university import University


@dataclass
class City:
    name: str
    country: str
    population: int
    one_person_yearly_costs: int
    universities: list[University]

    @classmethod
    def from_dict(cls, d: dict[str, any]) -> City:
        city = City(
            name=d["name"],
            country=d["country"],
            population=d["population"],
            one_person_yearly_costs=d["one_person_yearly_costs"],
            universities=[University.from_dict(u) for u in d["universities"]],
        )

        for uni in city.universities:
            uni.city = city
        
        return city