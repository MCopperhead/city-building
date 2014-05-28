import os
from pyglet import image

texture_bin = image.atlas.TextureBin(1024, 1024)

GRASS_IMAGE = texture_bin.add(image.load("tiles.png"))

ROAD_IMAGES = {file: texture_bin.add(image.load("images/roads/"+file)) for file in os.listdir("images/roads")}

TREES = [texture_bin.add(image.load("images/trees/"+file)) for file in os.listdir("images/trees")]

HAMMER = texture_bin.add(image.load("images/hammer.png"))

HIGHLIGHT = texture_bin.add(image.load("images/highlight.png"))

BUTTON_IMAGES = {file: texture_bin.add(image.load("images/buttons/"+file)) for file in os.listdir("images/buttons/")}

BUILDINGS = {file: texture_bin.add(image.load("images/buildings/"+file)) for file in os.listdir("images/buildings/")}

WALLS = {file: texture_bin.add(image.load("images/walls/"+file)) for file in os.listdir("images/walls/")}

CUBE_IMAGES = [image.load("images/animation/cubes/"+file) for file in os.listdir("images/animation/cubes/")]
TEST_CUBE_ANIM = image.Animation.from_image_sequence(CUBE_IMAGES, 0.1)
TEST_CUBE_ANIM.add_to_texture_bin(texture_bin)