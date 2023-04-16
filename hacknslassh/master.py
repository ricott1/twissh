import time
import esper
from hacknslassh.factories.cat_factory import load_cat, generate_cats
from hacknslassh.factories.player_factory import create_player, load_player
from hacknslassh.factories.potion_factory import PotionColor, PotionSize, create_potion
from hacknslassh.processors import processor
from .db_connector import get_all_cats, delete_all_cats, get_player, get_all_players

from hacknslassh.constants import GAME_SPEED
from web.server import UrwidMaster, UrwidMind
from .components import *
from .dungeon import Dungeon
from .gui.gui import GUI


class HackNSlassh(UrwidMaster):
    FPS = 60
    UPDATE_STEP = 1 / FPS

    def __init__(self) -> None:
        all_players = get_all_players()
        self.player_ids: dict[bytes, int] = {}
        for p in all_players:
            self.player_ids[bytes.fromhex(p[0])] = None
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
        self.world.add_processor(processor.SightProcessor(), priority=1)
        self.world.add_processor(processor.UpdateTargetProcessor())
        self.base_dungeon = Dungeon(self.world)
        # self.clock = pg.time.Clock()
        self.toplevel = GUI
        self.time = time.time()
        # delete_all_cats()
        self.initialize_cats()

    def initialize_cats(self) -> None:
        cats = get_all_cats()
        if len(cats) == 0:
            cats_data = generate_cats(self.base_dungeon)
        else:
            cats_data = [load_cat(self.base_dungeon, cat) for cat in cats]
        for cat_components in cats_data:
            cat_id = self.world.create_entity(*cat_components)
            self.base_dungeon.set_renderable_entity(cat_id)

    def register_new_player(self, mind: UrwidMind, game_class: GameClassName | None = None, gender: GenderType | None = None) -> int:
        all_matches = get_player(mind.avatar.uuid.hex)

        if len(all_matches) == 0:
            player_components = create_player(mind, self.base_dungeon, gender, game_class)
        elif len(all_matches) == 1:
            player_data = all_matches[0]
            player_components = load_player(mind, self.base_dungeon, player_data)
        else:
            print("Error while loading", mind.avatar.uuid.hex)
            return self.disconnect(mind)

        player_id = self.world.create_entity(*player_components)
        self.base_dungeon.set_renderable_entity(player_id)
        self.player_ids[mind.avatar.uuid.bytes] = player_id

        potion_components = create_potion(self.base_dungeon, PotionColor.RED, PotionSize.SMALL)
        potion_id = self.world.create_entity(*potion_components)
        x, y, z = self.world.component_for_entity(player_id, InLocation).position
        self.world.component_for_entity(potion_id, InLocation).position = (x, y, 0)
        self.base_dungeon.set_renderable_entity(potion_id)
        return player_id

    def disconnect(self, mind: UrwidMind) -> None:
        if mind.avatar.uuid.bytes in self.player_ids:
            ent_id = self.player_ids[mind.avatar.uuid.bytes]
            self.world.component_for_entity(ent_id, RGB).kill()
            print("disconnect", mind.avatar.uuid.hex, "from", self.minds)

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
