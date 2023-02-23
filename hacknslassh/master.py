import time
import esper
from hacknslassh.factories.cat_factory import create_cat
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
        self.world.add_processor(processor.DelayCallbackProcessor())
        self.world.add_processor(processor.UserInputProcessor(), priority=2)
        self.world.add_processor(processor.AiProcessor(), priority=2)
        self.world.add_processor(processor.DeathProcessor(), priority=4)
        self.world.add_processor(processor.DeathCallbackProcessor(), priority=3)
        self.world.add_processor(processor.ImageTransitionProcessor(), priority=1)
        self.world.add_processor(processor.SightTokenProcessor(), priority=1)
        self.world.add_processor(processor.TransformedTokenProcessor(), priority=1)
        self.world.add_processor(processor.TransformingTokenProcessor(), priority=1)
        self.world.add_processor(processor.SightProcessor())
        self.base_dungeon = Dungeon(self.world)
        # self.clock = pg.time.Clock()
        self.toplevel = GUI
        self.time = time.time()

        for _ in range(15):
            cat_id = create_cat(self.world, self.base_dungeon)
            self.base_dungeon.set_renderable_entity(cat_id)

    def register_new_player(
        self, mind: UrwidMind, game_class: GameClassName, gender: GenderType
    ) -> int:
        _components = get_components_for_game_class(mind, self.base_dungeon, gender, game_class)
        player_id = self.world.create_entity(*_components)
        print("register_new_player", player_id, "for", mind.avatar.uuid.bytes)
        self.base_dungeon.set_renderable_entity(player_id)

        self.player_ids[mind.avatar.uuid.bytes] = player_id
        self.minds[mind.avatar.uuid.bytes] = mind
        return player_id

    def disconnect(self, mind: UrwidMind) -> None:
        print("disconnect", mind.avatar.uuid.bytes, "from", self.minds)
        if mind.avatar.uuid.bytes in self.player_ids:
            ent_id = self.player_ids[mind.avatar.uuid.bytes]
            self.world.component_for_entity(ent_id, RGB).kill()
            print("disconnect", mind.avatar.uuid.bytes, "from", self.minds)
            print("ENT ID", ent_id, "RGB", self.world.component_for_entity(ent_id, RGB))
            
            # comment next line to keep disconnected bodies in (maybe set them dead)
            
            # del self.player_ids[mind.avatar.uuid.bytes]
        if mind.avatar.uuid.bytes in self.minds:
            del self.minds[mind.avatar.uuid.bytes]

    def update(self) -> None:
        deltatime = time.time() - self.time
        self.world.process(GAME_SPEED * deltatime)
        # world.process()
        # self.clock.tick(self.FPS)
        self.time = time.time()
