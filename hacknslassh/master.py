import esper
import uuid
import pygame as pg

from hacknslassh import components
from hacknslassh.gui.scenes import GUI
from hacknslassh.utils import random_stats, random_name
from hacknslassh.constants import GAME_SPEED


class HackNSlash(object):
    FPS = 10
    UPDATE_STEP = 1 / FPS

    def __init__(self):
        self.players = {}
        self.chat_log = []
        self.world = esper.World()  # world.World()
        self.gui = GUI
        self.clock = pg.time.Clock()

    def on_start(self, _id):
        pass

    def register_new_player(
        self, _id: uuid.UUID, race: components.RaceType, gender: components.GenderType
    ) -> components.Actor:
        _components = [
            components.Position(),
            components.ImageCollection.CHARACTERS[gender][race],
            components.RenderableWithDirection("white"),
            components.Directionable(),
            components.Characteristics(),
            components.Health(),
            components.Mana(),
            components.Race(race),
            components.Gender(gender),
            components.Description(random_name(), "description"),
        ]
        player = components.Entity(self.world, _components)
        self.players[_id] = player
        print("Player", player)
        return player

    def disconnect(self, _id):
        print("disconnect", _id)
        if _id in self.players:
            print("deleting", _id)
            # comment next line to keep disconnected bodies in (maybe set them dead)
            # self.world.delete_entity(player_id)#need to get player_id here
            # del self.players[_id]

    def on_update(self, _deltatime):

        self.world.process(GAME_SPEED * _deltatime)  # on_update(GAME_SPEED * _deltatime)
        # world.process()

        self.clock.tick(self.FPS)

        # sending = [l  for _id, p in self.players.items() for l in p.chat_sent_log]
        # self.redraw = self.redraw or len(sending) > 0
        # for _id, p in self.players.items():
        #     p_sending = [m for m in sending if m['sender_id'] != p.id]
        #     p.chat_sent_log = []
        #     p.chat_received_log += p_sending
