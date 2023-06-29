import os
import random
import pygame as pg
from hacknslassh.components.description import GameClassName
from hacknslassh.components.image import Image, ImageLayer, ImageComponentOffset, ColorMaps


file_dir = os.path.dirname(os.path.realpath(__file__)) + "/../assets"

def random_image_from_game_class(game_class: GameClassName, random_seed: bytes | None = None) -> Image:
    if not random_seed:
        random_seed = os.urandom(32)

    random.seed(game_class.encode() + random_seed)

    if game_class == GameClassName.CAT:
        W, H = (22, 38)
        components = {
            ImageLayer.BASE: {
                "offset": (0, 0),
                "surface": pg.Surface((W, H), pg.SRCALPHA)
            }
        }
        color_map = random.sample(list(ColorMaps["fur"].values()), 1)[0]
        for layer, part in zip((ImageLayer.TAIL, ImageLayer.BODY, ImageLayer.HEAD), ("tail", "body", "head")):
            candidate_imgs = [f for f in os.listdir(f"{file_dir}/{part}/") if f.startswith(game_class.value.lower())]
            filename = random.sample(candidate_imgs, 1)[0]
            surface = pg.image.load(f"{file_dir}/{part}/{filename}")
            components[layer] = {
                "offset": ImageComponentOffset[game_class][layer],
                "surface": surface,
                "color_map": color_map
            }
        return Image(components)
    
    W, H = (20, 38)
    components = {
        ImageLayer.BASE: {
            "offset": (0, 0),
            "surface": pg.Surface((W, H), pg.SRCALPHA)
        }
    }
    if game_class == GameClassName.HUMAN:
        skin_color_map = random.sample(("light_pink", "dark_pink", "brown"), 1)[0]
    elif game_class == GameClassName.DWARF:
        skin_color_map = random.sample(("light_pink", "dark_pink", "brown"), 1)[0]
    elif game_class == GameClassName.ELF:
        skin_color_map = random.sample(("light_pink", ), 1)[0]
    elif game_class == GameClassName.ORC:
        skin_color_map = random.sample(("light_green", "dark_green"), 1)[0]
    elif game_class == GameClassName.DEVIL:
        skin_color_map = random.sample(("red",), 1)[0]
    elif game_class == GameClassName.CAT:
        skin_color_map = random.sample(list(ColorMaps["fur"].keys()), 1)[0]    

    eyes_color_map = random.sample(list(ColorMaps["eyes"].values()), 1)[0]
    color_map = ColorMaps["skin"][skin_color_map]
    color_map.update(eyes_color_map)

    for layer, part in zip((ImageLayer.FEET, ImageLayer.LEGS, ImageLayer.BODY, ImageLayer.HEAD), ("feet", "legs", "body", "head")):
        candidate_imgs = [f for f in os.listdir(f"{file_dir}/{part}/") if f.startswith(game_class.value.lower())]
        filename = random.sample(candidate_imgs, 1)[0]
        surface = pg.image.load(f"{file_dir}/{part}/{filename}")
        components[layer] = {
            "offset": ImageComponentOffset[game_class][layer],
            "surface": surface,
            "color_map": color_map
        }
    
    hair_color_map = random.sample(list(ColorMaps["hair"].values()), 1)[0]
    if random.random() > 0.2:
        candidate_imgs = [f for f in os.listdir(f"{file_dir}/hair/") if f.startswith("hair")]
        filename = random.sample(candidate_imgs, 1)[0]
        surface = pg.image.load(f"{file_dir}/hair/{filename}")
        components[ImageLayer.HAIR] = {
            "offset": ImageComponentOffset[game_class][ImageLayer.HEAD],
            "surface": pg.image.load(f"{file_dir}/hair/{filename}"),
            "color_map": hair_color_map
        }
    
    if random.random() > 0.5:
        candidate_imgs = [f for f in os.listdir(f"{file_dir}/hair/") if f.startswith("facial_hair")]
        filename = random.sample(candidate_imgs, 1)[0]
        surface = pg.image.load(f"{file_dir}/hair/{filename}")
        components[ImageLayer.FACIAL_HAIR] = {
            "offset": ImageComponentOffset[game_class][ImageLayer.HEAD],
            "surface": surface,
            "color_map": hair_color_map
        }
    
    if game_class == GameClassName.DWARF or random.random() > 0.92:
        candidate_imgs = [f for f in os.listdir(f"{file_dir}/hair/") if f.startswith("full_beard")]
        filename = random.sample(candidate_imgs, 1)[0]
        surface = pg.image.load(f"{file_dir}/hair/{filename}")
        components[ImageLayer.FACIAL_HAIR] = {
            "offset": ImageComponentOffset[game_class][ImageLayer.HEAD],
            "surface": surface,
            "color_map": hair_color_map
        }

    return Image(components)
  
if __name__ == "__main__":
    game_class = random.sample([GameClassName.HUMAN, GameClassName.DWARF, GameClassName.ELF, GameClassName.ORC], 1)[0]
    print(random_image_from_game_class(game_class))