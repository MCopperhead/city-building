import cocos as c


class Highlight(c.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(Highlight, self).__init__()
        self.tile_highlight = c.sprite.Sprite("highlight.png")
        self.add(self.tile_highlight)

        self.roads = []

        self.batch = c.batch.BatchNode()
        self.add(self.batch)