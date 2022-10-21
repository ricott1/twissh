import time
import esper
from hacknslassh.processors import processor
import pygame as pg

from hacknslassh.utils import random_name
from hacknslassh.constants import GAME_SPEED
from .components import *
from .location import Location
from .gui.gui import GUI


class HackNSlash(object):
    FPS = 60
    UPDATE_STEP = 1 / FPS

    def __init__(self) -> None:
        self.players_id = {}
        self.minds = {}
        self.world = esper.World()
        self.world.add_processor(processor.ActionProcessor())
        self.world.add_processor(processor.UserInputProcessor(), priority=2)
        self.world.add_processor(processor.DeathProcessor(), priority=3)
        self.world.add_processor(processor.ImageTransitionProcessor())
        self.base_loc = Location()
        self.starting_pos = self.base_loc.generate_random_map(self.world)[0].center
        # self.clock = pg.time.Clock()
        self.toplevel = GUI
        self.time = time.time()

    def register_new_player(
        self, mind, race: RaceType, gender: GenderType
    ) -> int:
        x, y, z = self.starting_pos
        in_location = InLocation(self.base_loc, (x, y, 1))
        _components = [
            ImageCollection.CHARACTERS[gender][race],
            Characteristics(),
            Health(),
            Mana(),
            Description(random_name(), "description", race, gender),
            in_location,
            Acting(),
            User(mind)
        ]
        
        player_id = self.world.create_entity(*_components)
        self.base_loc.set_at(in_location.position, player_id)
        self.base_loc.set_renderable_entity(self.world, player_id)

        self.players_id[mind.avatar.uuid] = player_id
        print("Player", player_id)
        return player_id
    
    def dispatch_event(self, event_name: str, *args, **kwargs) -> None:
        for mind in self.minds:
            mind.process_event(event_name, *args, **kwargs)

    def disconnect(self, mind_id):
        print("disconnect", mind_id, "from", self.minds)
        if mind_id in self.players_id:
            print("deleting", mind_id)
            ent_id = self.players_id[mind_id]
            self.world.component_for_entity(ent_id, Health).value = 0
            # comment next line to keep disconnected bodies in (maybe set them dead)
            # self.world.delete_entity(self.players_id[avatar_id])
            # del self.players_id[avatar_id]
        if mind_id in self.minds:
            del self.minds[mind_id]

    def update(self) -> None:
        deltatime = time.time() - self.time
        self.world.process(GAME_SPEED * deltatime)
        # world.process()
        # self.clock.tick(self.FPS)
        self.time = time.time()
