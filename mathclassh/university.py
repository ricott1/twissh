from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
import uuid

if TYPE_CHECKING:
    from .city import City

from mathclassh.research_group import ResearchGroup

@dataclass
class University:
    name: str
    city: City
    unallocated_funds: int
    research_groups: dict[uuid.UUID, ResearchGroup]
    number_of_students: int
    students_level: int

    def __post_init__(self) -> None:
        for group in self.research_groups.values():
            group.university = self

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> University:
        return University(
            name=d["name"],
            city=d["city"],
            unallocated_funds=d["unallocated_funds"],
            research_groups={},
            number_of_students=d["number_of_students"],
            students_level=d["students_level"],
        )

    def total_funds(self) -> int:
        return sum([g.funds for g in self.research_groups.values()]) + self.unallocated_funds
    
    def add_research_group(self, research_group: ResearchGroup) -> None:
        self.research_groups[research_group.id] = research_group
        research_group.university = self
    
    def remove_group(self, research_group: ResearchGroup) -> None:
        if research_group.id in self.research_groups:
            del self.research_groups[research_group.id]