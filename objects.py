import cocos as c
import textures
from pyglet.graphics import OrderedGroup
from random import choice


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


class House(OrderedSprite):
    def __init__(self, **kwargs):
        super(House, self).__init__(textures.BUILDINGS["house.png"], anchor=(29, 15), **kwargs)
