import pygame as pg
from sshattrick.game import Game, Side


class SSHattrick(object):
    FPS = 60
    UPDATE_STEP = 1 / FPS

    def __init__(self) -> None:
        self.players_id = {}
        self.minds = {}
        self.games = {}
        self.clock = pg.time.Clock()

    def register_new_game(self, mind, name: str) -> None:
        if name in self.games:
            self.games[name].join(mind)
            mind.process_event("game_joined", self.games[name], Side.BLUE)

        else:
            self.games[name] = Game(name, mind)
            mind.process_event("game_joined", self.games[name], Side.RED)
    
    def dispatch_event(self, event_name: str, *args, **kwargs) -> None:
        for mind in self.minds:
            mind.process_event(event_name, *args, **kwargs)

    def disconnect(self, avatar_id):
        print("disconnect", avatar_id)
        if avatar_id in self.players_id:
            print("deleting", avatar_id)
            ent_id = self.players_id[avatar_id]
            # comment next line to keep disconnected bodies in (maybe set them dead)
            # self.world.delete_entity(self.players_id[avatar_id])
            # del self.players_id[avatar_id]

    def on_update(self, _deltatime: float) -> None:
        for game in self.games.values():
            game.update(_deltatime)
        self.clock.tick(self.FPS)
