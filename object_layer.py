import cocos as c


class ObjectLayer(c.layer.ScrollableLayer):
    def __init__(self):
        super(ObjectLayer, self).__init__()
        self.batch = c.batch.BatchNode()
        self.add(self.batch)