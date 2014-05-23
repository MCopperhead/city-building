import os
from pyglet import image

texture_bin = image.atlas.TextureBin()

GRASS_IMAGE = texture_bin.add(image.load("tiles.png"))

ROAD_IMAGES = {}
for file in os.listdir("images/roads"):
    ROAD_IMAGES[file] = texture_bin.add(image.load("images/roads/"+file))

TREES = []
for file in os.listdir("images/trees"):
    TREES.append(texture_bin.add(image.load("images/trees/"+file)))