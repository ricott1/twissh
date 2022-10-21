from enum import Enum
import json
from typing import Any
import uuid
import random
import datetime
import os
import pygame as pg

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

def roll(num, dice):
    tot = 0
    for i in range(num):
        tot += random.randint(1, dice)
    return tot


def mod(value):
    # return (value-10)//2
    if value <= 3:
        return -3
    elif value <= 5:
        return -2
    elif value <= 8:
        return -1
    elif value >= 18:
        return 3
    elif value >= 16:
        return 2
    elif value >= 13:
        return 1
    return 0


def get_time():
    return datetime.datetime.now().strftime("%H:%M:%S")


def new_id():
    return uuid.uuid4()

def load_data(filename) -> Any:
    return json.load(open(f"{FILE_DIR}/data/{filename}"))

class ImageCollection:
    FRAME = pg.image.load(f"{FILE_DIR}/assets/frame.png")
    RED_FRAME = pg.image.load(f"{FILE_DIR}/assets/red_frame.png")
    BLUE_FRAME = pg.image.load(f"{FILE_DIR}/assets/blue_frame.png")

class MALE_PORTRAITS(Enum):
    PORTRAIT_01 = pg.image.load(f"{FILE_DIR}/assets/male01.png")
    PORTRAIT_02 = pg.image.load(f"{FILE_DIR}/assets/male02.png")
    PORTRAIT_03 = pg.image.load(f"{FILE_DIR}/assets/male03.png")
    PORTRAIT_04 = pg.image.load(f"{FILE_DIR}/assets/male04.png")
    PORTRAIT_05 = pg.image.load(f"{FILE_DIR}/assets/male05.png")

    @classmethod
    def random(cls) -> pg.Surface:
        return pg.image.load(f"{FILE_DIR}/assets/male{random.randint(1, 5):02d}.png")

class FEMALE_PORTRAITS:
    PORTRAIT_01 = pg.image.load(f"{FILE_DIR}/assets/female01.png")
    PORTRAIT_02 = pg.image.load(f"{FILE_DIR}/assets/female02.png")
    PORTRAIT_03 = pg.image.load(f"{FILE_DIR}/assets/female03.png")
    PORTRAIT_04 = pg.image.load(f"{FILE_DIR}/assets/female04.png")

    @classmethod
    def random(cls) -> pg.Surface:
        return pg.image.load(f"{FILE_DIR}/assets/female{random.randint(1, 4):02d}.png")

