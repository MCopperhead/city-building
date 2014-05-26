import cocos as c
from cell import Cell
from shared_data import MAP_SIZE


class ObjectLayer(c.layer.ScrollableLayer):
    def __init__(self):
        super(ObjectLayer, self).__init__()
        self.batch = c.batch.BatchNode()
        self.add(self.batch)
        self.buildings = set()

    def add_object(self, cell, object_class, building=False):
        if cell.passable and cell.type != Cell.ROAD:
            obj = object_class(position=cell.position)
            z = 2*MAP_SIZE - cell.i - cell.j
            self.batch.add(obj, z=z)
            cell.child = obj
            cell.passable = False
            if building:
                self.buildings.add(cell)
            return True
        return False