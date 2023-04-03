import time
import esper
from hacknslassh.factories.cat_factory import load_cat, generate_cats
from hacknslassh.processors import processor
from .db_connector import insert_cat, get_all_cats, delete_all_cats

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
        delete_all_cats()
        cats = get_all_cats()
        if len(cats) == 0:
            self.init_cat()
            cats = get_all_cats()
        for cat_data in cats:
            cat_id = load_cat(self.world, self.base_dungeon, cat_data)
            self.base_dungeon.set_renderable_entity(cat_id)

    def init_cat(self) -> None:
        cats = generate_cats()
        for data in cats:
            info = data["info"]
            rgb = data["rgb"]
            catchable_token = data["catchableToken"]
            color_descriptor = data["ColorDescriptor"]
            body_parts = data["BodyPartsDescriptor"]
            insert_cat(
                info.uuid.hex(),
                info.name,
                info.age,
                info.gender.value,
                info.description,
                rgb.red.value,
                rgb.green.value,
                rgb.blue.value,
                "null",
                catchable_token.rarity,
                color_descriptor.hex(),
                body_parts.hex(),
            )

    def register_new_player(self, mind: UrwidMind, game_class: GameClassName, gender: GenderType) -> int:
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
