from __future__ import annotations
from email.policy import default
from enum import auto
from .constants import *

import pygame as pg
import os


"""COORDINATES:
    |    y
   - ---->
    |
    |
    |
    v x
"""

fileDir = os.path.dirname(os.path.realpath(__file__))
DEFAULT_SIZE = (80, 48)
GOAL_TOP = 18
GOAL_BOTTOM = 26
SHOOTING_TIME = 0.75
DRAG = 0.0005

class Direction(int, Enum):
    UP = 0
    UP_RIGHT = 1
    RIGHT = 2
    DOWN_RIGHT = 3
    DOWN = 4
    DOWN_LEFT = 5
    LEFT = 6
    UP_LEFT = 7


class Input(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    SHOOT = " "


class RedPlayer(object):
    RIGHT = pg.image.load(f"{fileDir}/assets/red_player01.png")
    DOWN = pg.image.load(f"{fileDir}/assets/red_player02.png")
    LEFT = pg.image.load(f"{fileDir}/assets/red_player03.png")
    UP = pg.image.load(f"{fileDir}/assets/red_player04.png")
    UP_RIGHT = pg.image.load(f"{fileDir}/assets/red_player05.png")
    DOWN_RIGHT = pg.image.load(f"{fileDir}/assets/red_player06.png")
    DOWN_LEFT = pg.image.load(f"{fileDir}/assets/red_player07.png")
    UP_LEFT = pg.image.load(f"{fileDir}/assets/red_player08.png")
    RIGHT_SHOOT = pg.image.load(f"{fileDir}/assets/red_player_shoot01.png")
    DOWN_SHOOT = pg.image.load(f"{fileDir}/assets/red_player_shoot02.png")
    LEFT_SHOOT = pg.image.load(f"{fileDir}/assets/red_player_shoot03.png")
    UP_SHOOT = pg.image.load(f"{fileDir}/assets/red_player_shoot04.png")
    UP_RIGHT_SHOOT = pg.image.load(f"{fileDir}/assets/red_player_shoot05.png")
    DOWN_RIGHT_SHOOT = pg.image.load(f"{fileDir}/assets/red_player_shoot06.png")
    DOWN_LEFT_SHOOT = pg.image.load(f"{fileDir}/assets/red_player_shoot07.png")
    UP_LEFT_SHOOT = pg.image.load(f"{fileDir}/assets/red_player_shoot08.png")
    GOALIE = pg.image.load(f"{fileDir}/assets/red_goalie.png")

class BluePlayer(object):
    RIGHT = pg.image.load(f"{fileDir}/assets/blue_player01.png")
    DOWN = pg.image.load(f"{fileDir}/assets/blue_player02.png")
    LEFT = pg.image.load(f"{fileDir}/assets/blue_player03.png")
    UP = pg.image.load(f"{fileDir}/assets/blue_player04.png")
    UP_RIGHT = pg.image.load(f"{fileDir}/assets/blue_player05.png")
    DOWN_RIGHT = pg.image.load(f"{fileDir}/assets/blue_player06.png")
    DOWN_LEFT = pg.image.load(f"{fileDir}/assets/blue_player07.png")
    UP_LEFT = pg.image.load(f"{fileDir}/assets/blue_player08.png")
    RIGHT_SHOOT = pg.image.load(f"{fileDir}/assets/blue_player_shoot01.png")
    DOWN_SHOOT = pg.image.load(f"{fileDir}/assets/blue_player_shoot02.png")
    LEFT_SHOOT = pg.image.load(f"{fileDir}/assets/blue_player_shoot03.png")
    UP_SHOOT = pg.image.load(f"{fileDir}/assets/blue_player_shoot04.png")
    UP_RIGHT_SHOOT = pg.image.load(f"{fileDir}/assets/blue_player_shoot05.png")
    DOWN_RIGHT_SHOOT = pg.image.load(f"{fileDir}/assets/blue_player_shoot06.png")
    DOWN_LEFT_SHOOT = pg.image.load(f"{fileDir}/assets/blue_player_shoot07.png")
    UP_LEFT_SHOOT = pg.image.load(f"{fileDir}/assets/blue_player_shoot08.png")
    GOALIE = pg.image.load(f"{fileDir}/assets/blue_goalie.png")

class Mask(object):
    RIGHT = pg.mask.from_surface(RedPlayer.RIGHT)
    DOWN = pg.mask.from_surface(RedPlayer.DOWN)
    LEFT = pg.mask.from_surface(RedPlayer.LEFT)
    UP = pg.mask.from_surface(RedPlayer.UP)
    UP_RIGHT = pg.mask.from_surface(RedPlayer.UP_RIGHT)
    DOWN_RIGHT = pg.mask.from_surface(RedPlayer.DOWN_RIGHT)
    DOWN_LEFT = pg.mask.from_surface(RedPlayer.DOWN_LEFT)
    UP_LEFT = pg.mask.from_surface(RedPlayer.UP_LEFT)
    RIGHT_SHOOT = pg.mask.from_surface(RedPlayer.RIGHT_SHOOT)
    DOWN_SHOOT = pg.mask.from_surface(RedPlayer.DOWN_SHOOT)
    LEFT_SHOOT = pg.mask.from_surface(RedPlayer.LEFT_SHOOT)
    UP_SHOOT = pg.mask.from_surface(RedPlayer.UP_SHOOT)
    UP_RIGHT_SHOOT = pg.mask.from_surface(RedPlayer.UP_RIGHT_SHOOT)
    DOWN_RIGHT_SHOOT = pg.mask.from_surface(RedPlayer.DOWN_RIGHT_SHOOT)
    DOWN_LEFT_SHOOT = pg.mask.from_surface(RedPlayer.DOWN_LEFT_SHOOT)
    UP_LEFT_SHOOT = pg.mask.from_surface(RedPlayer.UP_LEFT_SHOOT)
    GOALIE = pg.mask.from_surface(RedPlayer.GOALIE)


class Side(Enum):
    RED = auto()
    BLUE = auto()



class Player(pg.sprite.Sprite):
    def __init__(self, side: Side, game: Game) -> None:
        self.game = game
        _x = DEFAULT_SIZE[0]//2 - 4 if side == Side.RED else DEFAULT_SIZE[0]//2 + 4
        _y = DEFAULT_SIZE[1]//2
        self.position = pg.math.Vector2(_x, _y)
        self.velocity = pg.math.Vector2(0, 0)
        self.acceleration = pg.math.Vector2(0, 0)
        self.side = side
        self.direction = Direction.RIGHT if self.side == Side.RED else Direction.LEFT
        self.goalie = Goalie(self.side)
        self.goalie.position = pg.math.Vector2(1, _y) if self.side == Side.RED else pg.math.Vector2(DEFAULT_SIZE[0] - 4, _y)
        self.shooting = 0
        super().__init__()
       
    @property
    def x(self) -> int:
        return int(self.position.x)
    
    @property
    def y(self) -> int:
        return int(self.position.y)
        
    @property
    def rect(self):
        return self.image.get_rect(topleft=pg.math.Vector2(self.x, self.y))
    
    @property
    def image(self) -> pg.Surface:
        name = self.direction.name + "_SHOOT" if self.shooting else self.direction.name
        if self.side == Side.RED:
            return RedPlayer.__dict__[name]
        else:
            return BluePlayer.__dict__[name]
    
    @property
    def mask(self):
        return Mask.__dict__[self.direction.name]

    @property
    def opponent(self):
        return self.game.blue_player if self.side == Side.RED else self.game.red_player
    
    def handle_input(self, _input: str) -> None:
        max_acc = 250
        acc = 0
        if _input == Input.UP:
            acc = max_acc
        elif _input == Input.DOWN and self.velocity.magnitude_squared() > 0:
            acc = -max_acc
        # turn left
        elif _input == Input.LEFT:
            self.turn(-1)
        # turn right
        elif _input == Input.RIGHT:
            self.turn(1)
        elif _input == Input.SHOOT:
            self.shoot()

        if self.direction == Direction.RIGHT:
            self.acceleration = acc * pg.math.Vector2(1, 0)
        elif self.direction == Direction.UP:
            self.acceleration = acc * pg.math.Vector2(0, -1)
        elif self.direction == Direction.LEFT:
            self.acceleration = acc * pg.math.Vector2(-1, 0)
        elif self.direction == Direction.DOWN:
            self.acceleration = acc * pg.math.Vector2(0, 1)
        elif self.direction == Direction.UP_RIGHT:
            self.acceleration = acc * pg.math.Vector2(1, -1).normalize()
        elif self.direction == Direction.DOWN_RIGHT:
            self.acceleration = acc * pg.math.Vector2(1, 1).normalize()
        elif self.direction == Direction.DOWN_LEFT:
            self.acceleration = acc * pg.math.Vector2(-1, 1).normalize()
        elif self.direction == Direction.UP_LEFT:
            self.acceleration = acc * pg.math.Vector2(-1, -1).normalize()  
    
    def turn(self, direction: int) -> None:
        self.direction = Direction((self.direction + direction)%8)
    
    def shoot(self) -> None:
        self.shooting = SHOOTING_TIME
    
    def check_collitions(self) -> list[str, str]:
        collided = []
        if pg.sprite.collide_mask(self, self.game.bottom_wall):
            print("collided at bottom", self.position)
            collided.append("bottom")
        elif pg.sprite.collide_mask(self, self.game.top_wall):
            print("collided at top", self.position)
            collided.append("top")

        if pg.sprite.collide_mask(self, self.game.left_wall):
            print("collided at left", self.position)
            collided.append("left")
        elif pg.sprite.collide_mask(self, self.game.right_wall):
            print("collided at right", self.position)
            collided.append("right")
        
        if pg.sprite.collide_mask(self, self.goalie):
            print("collided with goalie", self.position)
            collided.append("own_goalie")

        elif pg.sprite.collide_mask(self, self.opponent.goalie):
            print("collided with goalie", self.position)
            collided.append("opponent_goalie")
        
        return collided
    
    def update(self, deltatime: float) -> tuple[pg.math.Vector2, bool]:
        new_velocity = self.velocity + self.acceleration * deltatime
        v = new_velocity.magnitude()
        if v > 0:
            new_velocity = v/(1+DRAG*v**2) * new_velocity.normalize()
        self.position += new_velocity * deltatime
        
        # Check collisions with walls
        if self.position.y > self.game.size[1] - self.rect.height - 1:
            self.position.y = self.game.size[1] - self.rect.height - 1
            new_velocity.y = 0
        elif self.position.y < 1:
            self.position.y = 1
            new_velocity.y = 0
        if self.position.x > self.game.size[0] - self.rect.width - 1:
            self.position.x = self.game.size[0] - self.rect.width - 1
            new_velocity.x = 0
        elif self.position.x < 1:
            self.position.x = 1
            new_velocity.x = 0
        
        old_position = pg.math.Vector2(self.position)
        # Check collisions with red goalie
        # if pg.sprite.collide_mask(self, self.game.red_player.goalie):
        #     if self.rect.left < self.game.red_player.goalie.rect.right:
        #         new_velocity.x = 0
        #     if self.rect.bottom > self.game.red_player.goalie.rect.top:
        #         new_velocity.y = 0
        #     elif self.rect.top < self.game.red_player.goalie.rect.bottom:
        #         new_velocity.y = 0
        #     self.position = old_position
        # # Check collisions with blue goalie
        # elif pg.sprite.collide_mask(self, self.game.blue_player.goalie):
        #     if self.rect.right > self.game.blue_player.goalie.rect.left:
        #         new_velocity.x = 0
        #     if self.rect.bottom > self.game.blue_player.goalie.rect.top:
        #         new_velocity.y = 0
        #     elif self.rect.top < self.game.blue_player.goalie.rect.bottom:
        #         new_velocity.y = 0
        #     self.position = old_position
        
        self.velocity = new_velocity
        self.acceleration = pg.math.Vector2(0, 0)
        self.goalie.position.y = max(GOAL_TOP, min(GOAL_BOTTOM, self.y))
        self.shooting = max(0, self.shooting - deltatime)
        

class Goalie(pg.sprite.Sprite):
    def __init__(self, side: Side) -> None:
        _x = DEFAULT_SIZE[0]//2 - 4 if side == Side.RED else DEFAULT_SIZE[0]//2 + 4
        _y = DEFAULT_SIZE[1]//2
        self.position = pg.math.Vector2(_x, _y)
        self.side = side
        super().__init__()
        self.mask = Mask.GOALIE

    @property
    def x(self) -> int:
        return int(self.position.x)
    
    @property
    def y(self) -> int:
        return int(self.position.y)
        
    @property
    def rect(self):
        return self.image.get_rect(topleft=pg.math.Vector2(self.x, self.y))
    
    @property
    def image(self) -> pg.Surface:
        if self.side == Side.RED:
            return RedPlayer.GOALIE
        else:
            return BluePlayer.GOALIE

class Wall(pg.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.rect = pg.Rect(x, y, width, height)
        self.image = pg.Surface((width, height))
        self.image.fill(pg.Color("purple"))
        self.mask = pg.mask.from_surface(self.image)
        super().__init__()


class Game(object):
    def __init__(self, name: str, red_mind = None, blue_mind = None) -> None:
        self.red_mind = red_mind
        self.blue_mind = blue_mind
        self.name = name

        self.size = DEFAULT_SIZE
        self.center = (self.size[0] // 2, self.size[1] // 2)
        self.red_player = Player(Side.RED, self)
        self.blue_player = Player(Side.BLUE, self)

        self.bottom_wall = Wall(0, self.size[1] - 1, self.size[0], 1)
        self.top_wall = Wall(0, 0, self.size[0], 1)
        self.left_wall = Wall(0, 0, 1, self.size[1])
        self.right_wall = Wall(self.size[0] - 1, 0, 1, self.size[1])

        self.field = pg.image.load(f"{fileDir}/assets/field.png")
        self.field.blit(self.bottom_wall.image, self.bottom_wall.rect)
        self.field.blit(self.top_wall.image, self.top_wall.rect)
        self.field.blit(self.left_wall.image, self.left_wall.rect)
        self.field.blit(self.right_wall.image, self.right_wall.rect)

        self.sprites = pg.sprite.Group(self.red_player, self.blue_player, self.red_player.goalie, self.blue_player.goalie)
    
    def image(self) -> pg.Surface:
        image = self.field.copy()
        image.blit(self.red_player.image, (self.red_player.x, self.red_player.y))
        image.blit(self.blue_player.image, (self.blue_player.x, self.blue_player.y))
        image.blit(self.red_player.goalie.image, (self.red_player.goalie.x, self.red_player.goalie.y))
        image.blit(self.blue_player.goalie.image, (self.blue_player.goalie.x, self.blue_player.goalie.y))

        debug = True
        if debug:
            pg.draw.rect(image, pg.Color("red"), self.red_player.rect, 1)
            pg.draw.rect(image, pg.Color("blue"), self.blue_player.rect, 1)
            # pg.draw.rect(image, pg.Color("red"), self.red_player.goalie.rect, 1)
            # pg.draw.rect(image, pg.Color("blue"), self.blue_player.goalie.rect, 1)
            # draw red line on goalie top
            pg.draw.line(image, pg.Color("red"), (self.red_player.goalie.rect.left, self.red_player.goalie.rect.top), (self.red_player.goalie.rect.right, self.red_player.goalie.rect.top))
            # draw blue line on goalie top
            pg.draw.line(image, pg.Color("blue"), (self.blue_player.goalie.rect.left, self.blue_player.goalie.rect.top), (self.blue_player.goalie.rect.right, self.blue_player.goalie.rect.top))
        return image

    def join(self, mind) -> None:
        self.blue_mind = mind
        self.start()
    
    def start(self) -> None:
        pass

    def update(self, deltatime: float) -> None:
        self.red_player.update(deltatime)
        self.blue_player.update(deltatime)

        for player in [self.red_player, self.blue_player]:
            player.update(deltatime)

        if self.red_mind:
            self.red_mind.process_event("redraw_local_ui_next_cycle")
        if self.blue_mind:
            self.blue_mind.process_event("redraw_local_ui_next_cycle")

    


    