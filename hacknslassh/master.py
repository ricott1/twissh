import time
import esper
from hacknslassh.processors import processor

from hacknslassh.utils import random_name
from hacknslassh.constants import GAME_SPEED
from twissh.server import UrwidMaster, UrwidMind
from .components import *
from .dungeon import Dungeon
from .gui.gui import GUI


class HackNSlassh(UrwidMaster):
    FPS = 60
    UPDATE_STEP = 1 / FPS

    def __init__(self) -> None:
        self.player_ids: dict[bytes, int] = {}
        self.minds = {}
        self.world = esper.World()
        self.world.add_processor(processor.ActionProcessor())
        self.world.add_processor(processor.UserInputProcessor(), priority=2)
        self.world.add_processor(processor.DeathProcessor(), priority=3)
        self.world.add_processor(processor.ImageTransitionProcessor())
        self.world.add_processor(processor.SightTokenProcessor())
        self.base_loc = Dungeon(self.world)
        # self.clock = pg.time.Clock()
        self.toplevel = GUI
        self.time = time.time()

    def register_new_player(
        self, mind: UrwidMind, game_class: GameClassName, gender: GenderType
    ) -> int:
        x, y = self.base_loc.random_floor_tile()
        in_location = InLocation(self.base_loc, (x, y, 1), fg=(255, 0, 0))
        _components = [
            ImageCollection.CHARACTERS[gender][game_class],
            Characteristics.get_random(),
            Health(),
            Mana(),
            Description(random_name(), "description", game_class, gender),
            in_location,
            Acting(),
            User(mind)
        ]
        
        player_id = self.world.create_entity(*_components)
        print("register_new_player", player_id, "for", mind.avatar.uuid.bytes)
        # self.base_loc.set_at(in_location.position, player_id)
        self.base_loc.set_renderable_entity(player_id)

        self.player_ids[mind.avatar.uuid.bytes] = player_id
        self.minds[mind.avatar.uuid.bytes] = mind
        return player_id

    def disconnect(self, mind: UrwidMind) -> None:
        print("disconnect", mind.avatar.uuid.bytes, "from", self.minds)
        if mind.avatar.uuid.bytes in self.player_ids:
            ent_id = self.player_ids[mind.avatar.uuid.bytes]
            self.world.component_for_entity(ent_id, Health).value = 0
            # comment next line to keep disconnected bodies in (maybe set them dead)
            # self.world.delete_entity(self.player_ids[avatar_id])
            # del self.player_ids[avatar_id]
        if mind.avatar.uuid.bytes in self.minds:
            del self.minds[mind.avatar.uuid.bytes]

    def update(self) -> None:
        deltatime = time.time() - self.time
        self.world.process(GAME_SPEED * deltatime)
        # world.process()
        # self.clock.tick(self.FPS)
        self.time = time.time()
