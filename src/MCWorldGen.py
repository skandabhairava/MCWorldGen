#!/usr/bin/env python3

# pip install git+https://github.com/pvigier/perlin-numpy amulet==1.21.0

# make a folder next to ur program called "template" and place an empty void world folder in there named "EMPTY". This program wil make a copy of it everytime it generates a new world 

import helpers, math, random, sys
import numpy as np

from world_generator import WorldGenerator
from amulet.api.block_entity import BlockEntity
from amulet_nbt._string import StringTag
from perlin_numpy import (
    generate_fractal_noise_2d, generate_fractal_noise_3d
)

from typing import Callable

MIN_X, MAX_X = -100, 100
MIN_Y, MAX_Y = -64, 130
MIN_Z, MAX_Z = -100, 100


#from functools import lru_cache
""" @lru_cache
def calc(x: int, y: int, z: int) -> int|float:

    #replace x w/ z, and y w/ x with formulas u find onine

    try:
        return 0
    except Exception:
        print(x, y, z)
        raise """

class CustomTerrainGen(WorldGenerator):
    
    def __init__(self, world_name: str, x_limits: tuple[int, int], y_limits: tuple[int, int], z_limits: tuple[int, int]) -> None:
        super().__init__(world_name, x_limits, y_limits, z_limits)

        self.ore_rarity = 450

    # MAIN GEN ALGORITHM/FUNC

    def generate_sugarcane(self, x, y, z):
        y_level = random.randint(2, 5)

        for dy in range(1, y_level):
            self.place_block(x, y+dy, z, "sugar_cane")

    def generate_normal_tree(self, x, y, z):
        # send y of base of tree / dirt block to place tree
        y_level = random.randint(3, 5)

        #BASE
        for dy in range(1, y_level):
            self.place_block(x, y+dy, z, "oak_log")

        #generate beehive randomly
        
        if random.randint(0, 40) == 0:
            BeeTags = helpers.generate_beehive_tag()
            if (pos:=(random.randint(0, 3))) == 0:
                self.place_block(x+1, y+y_level-1, z, "bee_nest", None, BlockEntity("minecraft", "bee_nest", x+1, y + y_level-1, z, BeeTags))
            elif pos == 1:
                self.place_block(x-1, y + y_level-1, z, "bee_nest", None, BlockEntity("minecraft", "bee_nest", x-1, y + y_level-1, z, BeeTags))
            elif pos == 2:
                self.place_block(x, y + y_level-1, z+1, "bee_nest", None, BlockEntity("minecraft", "bee_nest", x, y + y_level-1, z+1, BeeTags))
            elif pos == 3:
                self.place_block(x, y + y_level-1, z-1, "bee_nest", None, BlockEntity("minecraft", "bee_nest", x, y + y_level-1, z-1, BeeTags))

        #1st set of leaves
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                self.place_block(x+dx, y+y_level, z+dz, "oak_leaves", {"distance": StringTag("1")})

        #2nd set of leaves
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                self.place_block(x+dx, y+y_level+1, z+dz, "oak_leaves", {"distance": StringTag("1")})

        #3rd set of leaves
        for dx in range(-1, 2):
            self.place_block(x+dx, y+y_level, z, "oak_leaves", {"distance": StringTag("1")})
        for dz in range(-1, 2):
            self.place_block(x, y+y_level, z+dz, "oak_leaves", {"distance": StringTag("1")})

    def place_flower(self, x, y, z):
        flower = random.choice(["azure_bluet", "dandelion", "cornflower"])
        self.place_block(x, y+1, z, flower)

    def generate_features(self, x, y, z, noise_features, type_):

        if type_ == "TERRAIN":
            if random.randint(0, 40) == 0 and (noise_features[z][x]*25)>-0.8:
                self.generate_normal_tree(x, y, z)
            elif random.randint(0, 40) == 0:
                self.place_block(x, y+1, z, "tall_grass")
                self.place_block(x, y+2, z, "tall_grass", {"half": StringTag("upper")})
            elif random.randint(0, 5) == 0:
                self.place_block(x, y+1, z, "grass")
            elif random.randint(0, 30) == 0:
                self.place_flower(x, y, z)
        if type_ == "SHORE":
            if random.randint(0, 30) == 0 and (noise_features[z][x]*25)>0:
                self.generate_sugarcane(x, y, z)
            elif random.randint(0, 70) == 0:
                self.place_block(x, y+1, z, "dead_bush")

    def terrain_generation_algorithm(self, x, y, z, args: tuple) -> str|None:

        noise_terrain, noise_features, noise_caves = args

        #shift offsets
        offset_x, offset_z = x-self.x_limits[0], z-self.z_limits[0]

        # Painting constants
        water_level = 25
        lava_y = -58
        dirt_y = 30 + noise_terrain[offset_z][offset_x] * 9
        stone_y = 23 + (noise_terrain[offset_z][offset_x]*7)
        deepslate_y = -20 + (noise_terrain[offset_z][offset_x] * 5)

        # Carving constants
        cave_limits = (-63, 38)
        cave_start_closing = (-60 , 15)

        # Closing off caves near ends
        factor = -0.2
        m_up = (-1 - (factor))/(cave_limits[1] - cave_start_closing[1])
        linear_const_up = -1 - (m_up*cave_limits[1])

        m_down = (-1 - (factor))/(cave_limits[0] - cave_start_closing[0])
        linear_const_down = -1 - (m_down*cave_limits[0])

        block = ""

        if y <= -60:
            block = "bedrock" if random.randint((-60-y)*2, 8) == 8 else "deepslate"
        elif y < deepslate_y:
            block = "deepslate"
        elif y < stone_y:
            block = "stone"
        elif y == math.floor(dirt_y): # on surface
            if y > water_level: # on surface && above water
                self.generate_features(x, y, z, noise_features, "TERRAIN")
                block = "grass_block"
            elif y == water_level: #on surface && at water level
                if (noise_features[offset_z][offset_x]) > 0:
                    self.generate_features(x, y, z, noise_features, "SHORE")
                    block = "sand"
                else:
                    self.generate_features(x, y, z, noise_features, "TERRAIN")
                    block = "grass_block"
            else: #on surface && below water level
                if noise_features[offset_z][offset_x] > 0:
                    block = "sand"
                elif 0 > noise_features[offset_z][offset_x] >= -0.1:
                    block = "clay"
                else:
                    block = "gravel"
        elif y < dirt_y: #below surface
            block = "dirt"
        elif y <= water_level:
            block = "water"

        if (cave_limits[0] < y < cave_limits[1]):
            if y > cave_start_closing[1]:
                factor = round(((m_up*y) + linear_const_up), 4)
            elif y < cave_start_closing[0]:
                factor = round(((m_down*y) + linear_const_down), 4)

            if (noise_caves[offset_z][y-(cave_limits[0])][offset_x] < factor):
                return (None if y > lava_y else "lava")

        return block

    # ORE GEN

    def place_single_blob(self, x: int, y: int, z: int, y_limit: tuple[int, int], rare: int|float, block: str, shape: tuple[int, int, int], size: int):
        if (y_limit[0] < y < y_limit[1]) and random.randint(0, int(rare *self.ore_rarity))==0:
            blob = helpers.gen_blob(shape, size)
            for dx in range(shape[0]):
                for dy in range(shape[1]):
                    for dz in range(shape[2]):
                        x_, y_, z_ = x+dx-1, y+dy-1, z+dz-1
                        if blob[dx][dy][dz] and self.get_block(x_, y_, z_) != "air":
                            self.place_block(x, y, z, block)

    def place_blobs(self, x: int, y: int, z: int):
        # PLACE BLOBS
        coal_y = (-15, 23)
        iron_y = (-18, 20)
        gold_y = (-18, 20)
        copper_y = (-18, 20)
        redstone_y = (-18, 20)
        lapis_y = (-62, -20)
        diamond_y = (-62, -20)

        self.place_single_blob(x, y, z, coal_y, 2, "coal_ore", (3, 3, 3), 3)
        self.place_single_blob(x, y, z, iron_y, 2, "iron_ore", (3, 3, 3), 2)
        self.place_single_blob(x, y, z, gold_y, 2, "gold_ore", (3, 3, 3), 2)
        self.place_single_blob(x, y, z, copper_y, 2.3, "copper_ore", (3, 3, 3), 3)
        self.place_single_blob(x, y, z, redstone_y, 2.8, "redstone_ore", (3, 3, 3), 3)
        self.place_single_blob(x, y, z, lapis_y, 2.5, "deepslate_lapis_ore", (3, 3, 3), 3)
        self.place_single_blob(x, y, z, diamond_y, 2.8, "deepslate_diamond_ore", (3, 3, 3), 3)

    # MAIN GENERATOR

    def generate_terrain(self, func: Callable[[int, int, int, tuple], str|None], debug: bool = False):
        res = int((self.z_limits[1]-self.z_limits[0])/40)
        cave_res = int((self.z_limits[1]-self.z_limits[0])/10)

        print("Designing Terrain...")

        noise_terrain = generate_fractal_noise_2d((self.x_limits[1]-self.x_limits[0], self.z_limits[1]-self.z_limits[0]), (res, res), octaves=2)
        noise_features = generate_fractal_noise_2d((self.x_limits[1]-self.x_limits[0], self.z_limits[1]-self.z_limits[0]), (res, res), octaves=1)
        noise_caves = generate_fractal_noise_3d((self.x_limits[1]-self.x_limits[0], self.x_limits[1]-self.x_limits[0], self.z_limits[1]-self.z_limits[0]), (cave_res, cave_res, cave_res), persistence=3, lacunarity=5).round(1)

        print("Sculpting Terrain...")

        for x in range(self.x_limits[0], self.x_limits[1]):
            for z in range(self.z_limits[0], self.z_limits[1]):
                for y in range(self.y_limits[0], self.y_limits[1]):
                    if result:=func(x, y, z, (noise_terrain, noise_features, noise_caves)):
                        self.place_block(x, y, z, result)

            if debug: helpers.print_percent(x - self.x_limits[0], self.x_limits[1]-1 - self.x_limits[0])

        print("Filling Ores...")
        
        for x in range(self.x_limits[0], self.x_limits[1]):
            for z in range(self.z_limits[0], self.z_limits[1]):
                for y in range(self.y_limits[0], self.y_limits[1]):
                    self.place_blobs(x, y, z)
                    ...

            if debug: helpers.print_percent(x - self.x_limits[0], self.x_limits[1]-1 - self.x_limits[0])


def main():
    np.random.seed(int(random.random()*10000))
    
    world_location = "TEST" if len(sys.argv) != 2 else (sys.argv[1]) + "/TEST"

    world_generator = CustomTerrainGen(world_location, (MIN_X, MAX_X), (MIN_Y, MAX_Y), (MIN_Z, MAX_Z))
    world_generator.generate_terrain(world_generator.terrain_generation_algorithm, True)
    world_generator.save_and_close()

if __name__ == "__main__":
    main()