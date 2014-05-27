import cocos as c
import textures
from pyglet.graphics import OrderedGroup
from random import choice
from shared_data import MAP_SIZE


class OrderedSprite(c.sprite.Sprite):
    """
    Спрайт с исправленным методом set_batch.
    В оригинальном методе батчи не учитывают индекс z при добавлении спрайта.
    Причём, в более ранних версиях cocos2d было нормально. Непонятно зачем изменили.
    Патч нашел здесь:
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
    # Все здания должны соединяться дорогами с центральной Колонной.
    # Если здание не соединено - оно не работает.
    def __init__(self, *args, **kwargs):
        super(Building, self).__init__(*args, **kwargs)
        self.connected = False
        self.cell = None


class House(Building):
    def __init__(self, **kwargs):
        # TODO: дома должны развиваться не сами, как в цезаре, а вручную.
        # захотелось дом побольше - старые сносятся, новые строятся.
        # Для постройки больших домов должны выполняться определенные требования.
        super(House, self).__init__(textures.BUILDINGS["house.png"], anchor=(29, 15), **kwargs)
        self.population = 0
        self.max_population = 4

    def is_full(self):
        return self.population == self.max_population


class TestCube(OrderedSprite):
    def __init__(self, **kwargs):
        super(TestCube, self).__init__(textures.TEST_CUBE_ANIM, anchor=(29, 15), **kwargs)

    def move(self, path):
        action = c.actions.Delay(0)
        for cell in path[1:]:
            action += c.actions.MoveTo(cell.position, 1)
            z = 2*MAP_SIZE - cell.i - cell.j
            action += c.actions.CallFunc(self.parent.change_z, self, z)
        action += c.actions.CallFunc(self.kill)
        self.do(action)
