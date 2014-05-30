import cocos as c
import shared_data
import textures
from shared_data import Modes
from objects import Tree, House, Pillar, Wall, Stairs


class Highlight(c.layer.Layer):
    is_event_handler = True
    instance = None

    def __init__(self):
        super(Highlight, self).__init__()
        self.tile_highlight = c.sprite.Sprite(textures.HIGHLIGHT)
        self.tile_highlight.opacity = 0
        self.add(self.tile_highlight)

        self.roads = []

        self.batch = c.batch.BatchNode()
        self.add(self.batch)

        self.highlight_children = {
            Modes.TREE: Tree(),
            Modes.DELETE: c.sprite.Sprite(textures.HAMMER),
            Modes.HOUSING: House(z=0),
            Modes.PILLAR: Pillar(),
            Modes.STAIRS: Stairs(),
            Modes.LEVEL[0]: c.sprite.Sprite(textures.CELL_LEVEL_ADD),
            Modes.LEVEL[1]: c.sprite.Sprite(textures.CELL_LEVEL_SUB),
        }

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Highlight, cls).__new__(cls)
        return cls.instance

    def show(self):
        self.clear_highlight()
        if shared_data.mode in Modes.WALL:
            self.tile_highlight.add(Wall(int(shared_data.mode[-1])))
        elif shared_data.mode != Modes.ROAD:
            self.tile_highlight.add(self.highlight_children[shared_data.mode])
        self.tile_highlight.opacity = 255

    def hide(self):
        self.clear_highlight()
        self.tile_highlight.opacity = 0

    def clear_highlight(self):
        for child in self.tile_highlight.get_children():
            child.kill()