import cocos as c
import textures
from pyglet.graphics import OrderedGroup
from random import choice
from shared_data import MAP_SIZE


class OrderedSprite(c.sprite.Sprite):
    """
    Sprite with fixed "set_batch" method.
    In the original method, batches doesn't respect the Z level, when sprite is added.
    Patch is found here:
    https://groups.google.com/forum/#!topic/cocos-discuss/baOYgFpmvVk
    """
    def set_batch(self, batch, groups=None, z=0):
        self.batch = batch
        if batch is None:
            self.group = None
        else:
            group = groups.get(z)
            if group is None:
                group = OrderedGroup(z)
                groups[z] = group
            self.group = group
        for childZ, child in self.children:
            child.set_batch(self.batch, groups, z + childZ)


class Tree(OrderedSprite):
    def __init__(self, **kwargs):
        super(Tree, self).__init__(choice(textures.TREES), anchor=(29, 15), **kwargs)


class Pillar(OrderedSprite):
    def __init__(self, **kwargs):
        super(Pillar, self).__init__(textures.BUILDINGS["pillar.png"], anchor=(29, 15), **kwargs)


class Building(OrderedSprite):
    # All building must be connected by roads with central pillar.
    # If building is not connected - it is disabled.
    def __init__(self, image, z, **kwargs):
        super(Building, self).__init__(image, **kwargs)
        self.connected = False
        self.cell = None
        self.z = z


class House(Building):
    def __init__(self, z, **kwargs):
        super(House, self).__init__(textures.BUILDINGS["house.png"], z, anchor=(29, 15), **kwargs)
        self.population = 0
        self.max_population = 4

    def is_full(self):
        return self.population == self.max_population


class TestCube(OrderedSprite):
    def __init__(self, **kwargs):
        super(TestCube, self).__init__(textures.TEST_CUBE_ANIM, anchor=(29, 15), **kwargs)

    def move(self, path):
        action = c.actions.Delay(0)
        prev_cell = path[0]
        for cell in path[1:]:
            duration = max(abs(cell.i - prev_cell.i), abs(cell.j - prev_cell.j))
            action += c.actions.MoveTo(cell.position, duration)
            z = 2*MAP_SIZE - cell.i - cell.j
            action += c.actions.CallFunc(self.parent.change_z, self, z)
            prev_cell = cell
        action += c.actions.CallFunc(self.kill)
        self.do(action)


class Wall(OrderedSprite):
    def __init__(self, index, **kwargs):
        super(Wall, self).__init__(textures.WALLS["wall{}.png".format(index)], anchor=(29, 15), **kwargs)


class Stairs(OrderedSprite):
    def __init__(self, **kwargs):
        super(Stairs, self).__init__(textures.WALLS["stairs.png"], anchor=(29, 15), **kwargs)