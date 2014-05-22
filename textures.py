import os
from pyglet import image

texture_bin = image.atlas.TextureBin()
ROAD_IMAGES = {}
for file in os.listdir("images/roads"):
    ROAD_IMAGES[file] = texture_bin.add(image.load("images/roads/"+file))
GRASS_IMAGE = texture_bin.add(image.load("tiles.png"))