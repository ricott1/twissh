from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mathclassh.mathematician import Mathematician

from dataclasses import dataclass


@dataclass
class ResearchGroup:
    id: bytes
    university: bytes
    members: list[bytes]
    funds: int
    head: bytes
    
    @property
    def size(self) -> int:
        return len(self.members)
    
    def add_member(self, member: Mathematician) -> None:
        if member.id not in self.members:
            member.research_group = self.id
            self.members.append(member.id)
    
    def remove_member(self, member: Mathematician) -> None:
        if member.id in self.members:
            member.research_group = None
            self.members.remove(member.id)