import cocos as c
import textures
from random import choice


class Tree(c.sprite.Sprite):
    def __init__(self):
        super(Tree, self).__init__(choice(textures.TREES), anchor=(29, 15))
