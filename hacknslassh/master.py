import esper
import uuid
import pygame as pg

from hacknslassh import components
from hacknslassh.gui.scenes import GUI
from hacknslassh.utils import random_name
from hacknslassh.constants import GAME_SPEED


class HackNSlash(object):
    FPS = 20
    UPDATE_STEP = 1 / FPS

    def __init__(self) -> None:
        self.players = {}
        self.chat_log = []
        self.world = esper.World()  # world.World()
        self.gui = GUI
        self.clock = pg.time.Clock()

    def register_new_player(
        self, mind, race: components.RaceType, gender: components.GenderType
    ) -> components.Actor:
        player = components.Player(self.world, mind, random_name(), "", race, gender)
        self.players[mind.avatar.uuid] = player
        print("Player", player)
        return player

    def disconnect(self, avatar_id):
        print("disconnect", avatar_id)
        if avatar_id in self.players:
            print("deleting", avatar_id)
            # comment next line to keep disconnected bodies in (maybe set them dead)
            self.world.delete_entity(self.players[avatar_id].id)
            del self.players[avatar_id]

    def on_update(self, _deltatime: float) -> None:
        self.world.process(GAME_SPEED * _deltatime)  # on_update(GAME_SPEED * _deltatime)
        # world.process()
        self.clock.tick(self.FPS)
