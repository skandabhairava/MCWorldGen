import amulet, shutil
from amulet.api.block import Block
from amulet.api.block_entity import BlockEntity
from typing import Callable
import math

class WorldGenerator:
    def __init__(self, world_name: str, x_limits: tuple[int, int], y_limits: tuple[int, int], z_limits: tuple[int, int]) -> None:
        try:
            shutil.rmtree(world_name)
        except FileNotFoundError:
            ...
        try:
            shutil.copytree("template/EMPTY", world_name)
        except Exception:
            raise Exception("Error while copying \"EMPTY\" world from dir 'template' ")
        
        self.world = amulet.load_level(world_name)
        self.x_limits, self.y_limits, self.z_limits = sorted(x_limits), sorted(y_limits), sorted((z_limits))

    def place_block(self, x: int, y: int, z: int, block: str, properties:dict|None=None, block_entity: BlockEntity|None=None, namespace="minecraft", dimension="minecraft:overworld"):
        self.world.set_version_block(x, y, z, dimension, ("java", (1, 19)), Block(namespace, block, properties), block_entity) # type: ignore

    def get_block(self, x: int, y: int, z: int, dimension: str="minecraft:overworld") -> str:
        return self.world.get_block(x, y, z, "minecraft:overworld")._base_name.lower()

    def generate_terrain(self, func: Callable[[int, int, int, dict|tuple|list], int|float], debug: bool=False):
        for x in range(self.x_limits[0], self.x_limits[1]):
            for z in range(self.z_limits[0], self.z_limits[1]):
                for y in range(self.y_limits[0], self.y_limits[1]):
                    y_level = func(x, y, z, {})
                    if y < math.floor(y_level):
                        self.place_block(x, y, z, "stone")

            if debug: print("done x:", x)

    def save_and_close(self):
        print("Saving World...")
        if self.world.changed:
            self.world.pre_save_operation()
            self.world.save()
        self.world.close()
