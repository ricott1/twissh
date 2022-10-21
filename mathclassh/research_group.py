from __future__ import annotations
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from mathclassh.city import City
    from mathclassh.mathematician import Mathematician
    from mathclassh.university import University

from dataclasses import dataclass


@dataclass
class ResearchGroup:
    id: uuid.UUID
    university: University
    members: dict[uuid.UUID, Mathematician]
    funds: int
    head: Mathematician

    def __post_init__(self) -> None:
        for member in self.members.values():
            member.research_group = self

    @property
    def city(self) -> City:
        return self.university.city
    
    @property
    def members_list(self) -> list[Mathematician]:
        return list(self.members.values())
    
    @property
    def size(self) -> int:
        return len(self.members)
    
    def add_member(self, member: Mathematician) -> None:
        self.members[member.id] = member
        member.research_group = self
    
    def remove_member(self, member: Mathematician) -> None:
        if member.id in self.members:
            member.research_group = None
            del self.members[member.id]