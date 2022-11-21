from __future__ import annotations
from dataclasses import dataclass
import uuid


@dataclass
class City:
    id: bytes
    name: str
    country: str
    population: int
    one_person_yearly_costs: int
    universities: list[bytes]

    @classmethod
    def from_dict(cls, d: dict[str, any]) -> City:
        city = City(
            id = uuid.uuid4().bytes,
            name=d["name"],
            country=d["country"],
            population=d["population"],
            one_person_yearly_costs=d["one_person_yearly_costs"],
            universities=[],
        )

        for uni in city.universities:
            uni.city = city
        
        return city