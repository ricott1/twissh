from __future__ import annotations

import random
import time
import uuid

from mathclassh import utils
from mathclassh.city import City
from mathclassh.math_skills import FieldDescription, FieldSkill
from mathclassh.mathematician import ROLE, Mathematician
    
from mathclassh.research_group import ResearchGroup
from mathclassh.university import University

from twissh.server import UrwidMaster, UrwidMind

from mathclassh.gui.gui import GUI


class MathClassH(UrwidMaster):
    FPS = 1
    UPDATE_STEP = 1 / FPS

    def __init__(self) -> None:
        self.minds: dict[bytes, UrwidMind] = {}
        self.toplevel = GUI
        # self.clock = pg.time.Clock()
        self.time = time.time()
        self.current_date = 0
        self.cities: dict[bytes, City] = {}
        self.universities: dict[bytes, University] = {}
        self.research_groups: dict[bytes, ResearchGroup] = {}
        for d in utils.load_data("cities.json"):
            city = City.from_dict(d)
            for u in d["universities"]:
                uni = University.from_dict(u)
                uni.city = city.id
                city.universities.append(uni.id)
                self.universities[uni.id] = uni

            self.cities[city.id] = city
            
        self.fields = [FieldDescription.from_dict(d) for d in utils.load_data("fields.json")]
        self.mathematicians = {}

    def get_random_mathematician(self) -> Mathematician:
        return random.choice(list(self.mathematicians.values()))

    def generate_mathematician(self) -> Mathematician:
        mathematician = Mathematician.generate(random.choice(self.cities), ROLE.HEAD)
        # for field in self.fields:
        #     subfields = {f.short_name: utils.roll(1, 20) for f in field.subfields}
        #     setattr(mathematician, field.short_name, FieldSkill(field, subfields)) 
        
        self.mathematicians[mathematician.id] = mathematician

    def generate_research_group(self, research_group_id: bytes) -> ResearchGroup:
        members = [
            Mathematician.generate(random.choice(list(self.cities.keys())), ROLE.HEAD),
            Mathematician.generate(random.choice(list(self.cities.keys())), ROLE.PHD),
            Mathematician.generate(random.choice(list(self.cities.keys())), ROLE.PHD),
        ]
        self.mathematicians.update({m.id: m for m in members})
        
        city = random.choice(list(self.cities.values()))
        uni = random.choice(city.universities)

        r = ResearchGroup(research_group_id, uni, [], 1000, members[0].id)
        for m in members:
            r.add_member(m)
            
        self.research_groups[r.id] = r
        self.universities[uni].add_research_group(r)
        return r 

    def tick(self) -> None:
        ...

    def register_new_game(self, mind: UrwidMind) -> ResearchGroup:
        self.minds[mind.avatar.uuid.bytes] = mind
        research_group = self.generate_research_group(mind.avatar.uuid.bytes)
        return research_group

    def disconnect(self, mind: UrwidMind) -> None:
        print("disconnect", mind.avatar.uuid.bytes, "from", self.minds)
        if mind.avatar.uuid.bytes in self.minds:
            del self.minds[mind.avatar.uuid.bytes]

    def update(self) -> None:
        self.tick()
        # self.clock.tick(self.FPS)
