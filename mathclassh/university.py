from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import uuid

from mathclassh.research_group import ResearchGroup

@dataclass
class University:
    id: bytes
    name: str
    city: bytes
    unallocated_funds: int
    research_groups: list[bytes]
    number_of_students: int
    students_level: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> University:
        return University(
            id = uuid.uuid4().bytes,
            name=d["name"],
            city=None,
            unallocated_funds=d["unallocated_funds"],
            research_groups=[],
            number_of_students=d["number_of_students"],
            students_level=d["students_level"],
        )

    def total_funds(self) -> int:
        return sum([g.funds for g in self.research_groups.values()]) + self.unallocated_funds
    
    def add_research_group(self, research_group: ResearchGroup) -> None:
        if research_group.id not in self.research_groups:
            research_group.university = self.id
            self.research_groups.append(research_group.id)
    
    def remove_group(self, research_group: ResearchGroup) -> None:
        if research_group.id in self.research_groups:
            research_group.university = None
            self.research_groups.remove(research_group.id)