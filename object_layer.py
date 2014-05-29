import cocos as c
from cell import Cell
from shared_data import MAP_SIZE
from objects import TestCube, Wall


class DynamicBatch(c.batch.BatchNode):
    """
    Батч, позволяющий менять z дочернего объекта на лету.
    """
    def change_z(self, child, z):
        child.set_batch(None)
        child.set_batch(self.batch, self.groups, z)

        self.children = [(z_, c_) for (z_, c_) in self.children if c_ != child]
        elem = z, child

        lo = 0
        hi = len(self.children)
        a = self.children
        while lo < hi:
            mid = (lo+hi)//2
            if z < a[mid][0]: hi = mid
            else: lo = mid+1
        self.children.insert(lo, elem)


class ObjectLayer(c.layer.ScrollableLayer):
    def __init__(self):
        super(ObjectLayer, self).__init__()
        # self.batch = c.batch.BatchNode()
        self.batch = DynamicBatch()
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
                self.buildings.add(obj)
                obj.cell = cell
            return obj
        return None

    def add_wall(self, cell, index):
        if cell.passable and cell.type != Cell.ROAD:
            z = 2*MAP_SIZE - cell.i - cell.j
            wall = Wall(index, position=cell.position)
            self.batch.add(wall, z=z)
            if index < 6:
                cell.passable = False

    def summon_creature(self, path):
        creature = TestCube(position=self.parent.pillar_cell.position)
        z = 2*MAP_SIZE - path[0].i - path[0].j
        self.batch.add(creature, z=z)
        creature.move(path)
