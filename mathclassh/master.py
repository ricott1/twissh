from __future__ import annotations

import random
import time
import uuid

from mathclassh import utils
from mathclassh.city import City
from mathclassh.math_skills import Field
from mathclassh.mathematician import ROLE, Mathematician
    
from mathclassh.research_group import ResearchGroup

from twissh.server import UrwidMind

from mathclassh.gui.gui import GUI


class MathClassH(object):
    FPS = 1
    UPDATE_STEP = 1 / FPS

    def __init__(self) -> None:
        self.minds: dict[uuid.UUID, UrwidMind] = {}
        self.toplevel = GUI
        # self.clock = pg.time.Clock()
        self.time = time.time()
        self.current_date = 0
        self.cities = [City.from_dict(d) for d in utils.load_data("cities.json")]
        # self.fields = [Field.from_dict(d) for d in utils.load_data("fields.json")]
        self.mathematicians = {}

    def get_random_mathematician(self) -> Mathematician:
        return random.choice(list(self.mathematicians.values()))

    def generate_mathematician(self) -> Mathematician:
        mathematician = Mathematician.generate(random.choice(self.cities), ROLE.HEAD)

    def generate_research_group(self) -> ResearchGroup:
        members = [
            Mathematician.generate(random.choice(self.cities), ROLE.HEAD),
            Mathematician.generate(random.choice(self.cities), ROLE.PHD),
            Mathematician.generate(random.choice(self.cities), ROLE.PHD),
        ]
        self.mathematicians.update({m.id: m for m in members})
        
        city = random.choice(self.cities)
        uni = random.choice(city.universities)
        return ResearchGroup(None, uni, {m.id: m for m in members}, 1000, members[0])

    def tick(self) -> None:
        ...

    def register_new_game(self, mind: UrwidMind) -> ResearchGroup:
        self.minds[mind.avatar.uuid] = mind
        research_group = self.generate_research_group()
        research_group.id = mind.avatar.uuid
        return research_group
        

    def dispatch_event(self, event_name: str, *args, **kwargs) -> None:
        for mind in self.minds:
            mind.process_event(event_name, *args, **kwargs)

    def disconnect(self, avatar_id: bytes) -> None:
        print("disconnect", avatar_id)

    def update(self) -> None:
        self.tick()
        # self.clock.tick(self.FPS)
