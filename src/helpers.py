import random
import numpy as np
from scipy.ndimage import binary_dilation

from amulet_nbt._compound import CompoundTag
from amulet_nbt._list import ListTag
from amulet_nbt._named_tag import NamedTag
from amulet_nbt._int import IntTag
from amulet_nbt._float import FloatTag
from amulet_nbt._string import StringTag

def generate_beehive_tag():
    return NamedTag(CompoundTag({'Bees': ListTag(
                    [CompoundTag(
                        {'MinOccupationTicks': IntTag(600),
                        'EntityData': CompoundTag({
                            'Health': FloatTag(10.0),
                            'id': StringTag("minecraft:bee"),
                        })})
                    for _ in range(random.randint(1, 3))]
                )}))

def gen_blob(shape: tuple[int, int, int], size: int):
    blob = np.zeros(shape, dtype=bool)
    center = np.array(shape)//2
    selem = np.random.rand(size, size, size)
    selem = (selem > 0.5).astype(bool)
    blob[center[0], center[1], center[2]] = True
    blob = binary_dilation(blob, selem)
    return blob

def print_percent(done, total):
    percent = int((done/total) * 100)
    if percent % 5 == 0:
        print(f"Done: {percent}%",end="\r")

    if percent == 100:
        print("Done: 100%\nCompleted!")