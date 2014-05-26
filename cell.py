import cocos as c
import sys
from ctypes import cdll
import textures
from shared_data import RHOMBUS_SIZE
if sys.platform.startswith("linux"):
    triangle = cdll.LoadLibrary("triangle.so")
elif sys.platform.startswith("win"):
    triangle = cdll.LoadLibrary("triangle.dll")
else:
    triangle = None


class Rhombus():
    def __init__(self, left, top, right, bottom, width, height, size):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.width = width
        self.height = height
        self.size = size
        self.cells = []
        self.subrhombuses = ()

    def contains(self, x, y):
        if triangle:
            return triangle.contains(int(x), int(y), *(self.left+self.top+self.right+self.left+self.bottom+self.right))
        else:
            # Если нет скомпилированной библиотеки под текущую ОС - используем медленную питоновую реализацию
            for x1, y1, x2, y2, x3, y3 in (self.left+self.top+self.right, self.left+self.bottom+self.right):
                s = abs(x2*y3-x3*y2-x1*y3+x3*y1+x1*y2-x2*y1)
                s1 = abs(x2*y3-x3*y2-x*y3+x3*y+x*y2-x2*y)
                s2 = abs(x*y3-x3*y-x1*y3+x3*y1+x1*y-x*y1)
                s3 = abs(x2*y-x*y2-x1*y+x*y1+x1*y2-x2*y1)
                if s == s1+s2+s3:
                    return True
            return False

    def subdivide(self):
        """
        Рекурсивно делит ромб на 4 меньших ромба, а те 4 еще на 4 каждый и т.д.
        """
        if self.size // 2 < RHOMBUS_SIZE:
            return

        width = self.width
        height = self.height
        offset_x = self.bottom[0]
        offset_y = self.bottom[1]
        rhombus1 = Rhombus((-width//4 + offset_x, height//4 + offset_y),
                           (0 + offset_x, height//2 + offset_y),
                           (width//4 + offset_x, height//4 + offset_y),
                           (0 + offset_x, 0 + offset_y),
                           width // 2,
                           height // 2,
                           self.size // 2)
        rhombus1.parent = self
        rhombus2 = Rhombus((-width//4 + offset_x, height*3//4 + offset_y),
                           (0 + offset_x, height + offset_y),
                           (width//4 + offset_x, height*3//4 + offset_y),
                           (0 + offset_x, height//2 + offset_y),
                           width // 2,
                           height // 2,
                           self.size // 2)
        rhombus2.parent = self
        rhombus3 = Rhombus((-width//2 + offset_x, height//2 + offset_y),
                           (-width//4 + offset_x, height*3//4 + offset_y),
                           (0 + offset_x, height//2 + offset_y),
                           (-width//4 + offset_x, height//4 + offset_y),
                           width // 2,
                           height // 2,
                           self.size // 2)
        rhombus3.parent = self
        rhombus4 = Rhombus((0 + offset_x, height//2 + offset_y),
                           (width//4 + offset_x, height*3//4 + offset_y),
                           (width//2 + offset_x, height//2 + offset_y),
                           (width//4 + offset_x, height//4 + offset_y),
                           width // 2,
                           height // 2,
                           self.size // 2)
        rhombus4.parent = self

        self.subrhombuses = (rhombus1, rhombus2, rhombus3, rhombus4)

        for rhombus in self.subrhombuses:
            rhombus.subdivide()


class Cell(c.sprite.Sprite, Rhombus):
    GROUND = "ground"
    ROAD = "road"

    # узлы - места ячеек дорог, где они соединяются с другими
    # ячейка проверяет своих соседей, и если они являются дорогами - она побитовым ИЛИ записывает себе нужные узлы
    # и потом из словаря выбирается нужное изображение
    NODE_LEFT = 0b1000
    NODE_TOP = 0b0100
    NODE_RIGHT = 0b0010
    NODE_BOTTOM = 0b0001

    NODES = {
        0b0000: textures.ROAD_IMAGES["road_tile.png"],
        0b0001: textures.ROAD_IMAGES["road_tile.png"],
        0b0010: textures.ROAD_IMAGES["road_tile_90.png"],
        0b0011: textures.ROAD_IMAGES["roadturn1.png"],
        0b0100: textures.ROAD_IMAGES["road_tile.png"],
        0b0101: textures.ROAD_IMAGES["road_tile.png"],
        0b0110: textures.ROAD_IMAGES["roadturn2.png"],
        0b0111: textures.ROAD_IMAGES["crossroad4.png"],
        0b1000: textures.ROAD_IMAGES["road_tile_90.png"],
        0b1001: textures.ROAD_IMAGES["roadturn3.png"],
        0b1010: textures.ROAD_IMAGES["road_tile_90.png"],
        0b1011: textures.ROAD_IMAGES["crossroad5.png"],
        0b1100: textures.ROAD_IMAGES["roadturn4.png"],
        0b1101: textures.ROAD_IMAGES["crossroad3.png"],
        0b1110: textures.ROAD_IMAGES["crossroad2.png"],
        0b1111: textures.ROAD_IMAGES["crossroad1.png"],
    }

    def __init__(self, cell_image, x, y, i, j, cell_type=GROUND):
        super(Cell, self).__init__(cell_image)
        # c.sprite.Sprite.__init__(self, cell_image)
        self.position = (x, y)
        self.i = i
        self.j = j
        self.left = (x-29, y)
        self.right = (x+29, y)
        self.top = (x, y+15)
        self.bottom = (x, y-15)
        self.type = cell_type
        self.neighbours = []
        self.child = None  # объект, который находится в object_layer и стоит на этой клетке. Например, дерево или дом.

        self.node = 0b0000

        self.passable = True
        self.G = 0
        self.H = 0
        self.F = 0
        self.parent_cell = None

    def contains(self, x, y):
        return Rhombus.contains(self, x, y)

    def add_road(self):
        self.type = Cell.ROAD
        self.node = 0b0000

        for index, neighbour in enumerate(self.neighbours):
            if neighbour.type == Cell.ROAD:
                if index == 0:
                    self.node |= Cell.NODE_LEFT
                elif index == 1:
                    self.node |= Cell.NODE_TOP
                elif index == 2:
                    self.node |= Cell.NODE_RIGHT
                elif index == 3:
                    self.node |= Cell.NODE_BOTTOM

                neighbour.change_road()
        self.image = Cell.NODES[self.node]

    def change_road(self):
        self.node = 0b0000
        for index, neighbour in enumerate(self.neighbours):
            if neighbour.type == Cell.ROAD:
                if index == 0:
                    self.node |= Cell.NODE_LEFT
                elif index == 1:
                    self.node |= Cell.NODE_TOP
                elif index == 2:
                    self.node |= Cell.NODE_RIGHT
                elif index == 3:
                    self.node |= Cell.NODE_BOTTOM
        self.image = Cell.NODES[self.node]

    def remove_road(self):
        self.type = Cell.GROUND
        self.node = 0b0000
        self.image = textures.GRASS_IMAGE
        for index, neighbour in enumerate(self.neighbours):
            if neighbour.type == Cell.ROAD:
                neighbour.change_road()