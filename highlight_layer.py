import cocos as c
import shared_data
from shared_data import Modes
from objects import Tree


class Highlight(c.layer.Layer):
    is_event_handler = True
    instance = None

    def __init__(self):
        super(Highlight, self).__init__()
        self.tile_highlight = c.sprite.Sprite("highlight.png")
        self.tile_highlight.opacity = 0
        self.add(self.tile_highlight)

        self.roads = []

        self.batch = c.batch.BatchNode()
        self.add(self.batch)

        self.highlights = {
            Modes.TREE: Tree(),
        }

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Highlight, cls).__new__(cls)
        return cls.instance

    def show(self):
        if shared_data.mode != Modes.ROAD:
            self.tile_highlight.add(self.highlights[shared_data.mode])
        self.tile_highlight.opacity = 255

    def hide(self):
        for child in self.tile_highlight.get_children():
            child.kill()
        self.tile_highlight.opacity = 0