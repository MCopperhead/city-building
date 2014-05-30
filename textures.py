import os
from pyglet import image

_texture_bin = image.atlas.TextureBin(1024, 1024)

GRASS_IMAGE = _texture_bin.add(image.load("tiles.png"))

ROAD_IMAGES = {file: _texture_bin.add(image.load("images/roads/"+file)) for file in os.listdir("images/roads")}

TREES = [_texture_bin.add(image.load("images/trees/"+file)) for file in os.listdir("images/trees")]

HAMMER = _texture_bin.add(image.load("images/hammer.png"))

HIGHLIGHT = _texture_bin.add(image.load("images/highlight.png"))

BUTTON_IMAGES = {file: _texture_bin.add(image.load("images/buttons/"+file)) for file in os.listdir("images/buttons/")}

BUILDINGS = {file: _texture_bin.add(image.load("images/buildings/"+file)) for file in os.listdir("images/buildings/")}

WALLS = {file: _texture_bin.add(image.load("images/walls/"+file)) for file in os.listdir("images/walls/")}

CELL_LEVEL_ADD = _texture_bin.add(image.load("images/cell_level_add.png"))
CELL_LEVEL_SUB = _texture_bin.add(image.load("images/cell_level_sub.png"))

CUBE_IMAGES = [image.load("images/animation/cubes/"+file) for file in os.listdir("images/animation/cubes/")]
TEST_CUBE_ANIM = image.Animation.from_image_sequence(CUBE_IMAGES, 0.1)
TEST_CUBE_ANIM.add_to_texture_bin(_texture_bin)

INFOCARD = _texture_bin.add(image.load("images/infocard.png"))