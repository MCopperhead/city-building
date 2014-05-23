import cocos as c
from ctypes import cdll
from textures import ROAD_IMAGES
triangle = cdll.LoadLibrary("triangle.so")


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

    # @profile
    def contains(self, x, y):
        # Пока оставил это на случай, если не удастся скомпилировать С-шную библиотеку под винду
        # for x1, y1, x2, y2, x3, y3 in (self.left+self.top+self.right, self.left+self.bottom+self.right):
        #     s = abs(x2*y3-x3*y2-x1*y3+x3*y1+x1*y2-x2*y1)
        #     s1 = abs(x2*y3-x3*y2-x*y3+x3*y+x*y2-x2*y)
        #     s2 = abs(x*y3-x3*y-x1*y3+x3*y1+x1*y-x*y1)
        #     s3 = abs(x2*y-x*y2-x1*y+x*y1+x1*y2-x2*y1)
        #
        #     if s == s1+s2+s3:
        #         return True

        # return False
        return triangle.contains(int(x), int(y), *(self.left+self.top+self.right+self.left+self.bottom+self.right))

    def subdivide(self):
        """
        Рекурсивно делит ромб на 4 меньших ромба, а те 4 еще на 4 каждый и т.д.
        """
        if self.size // 2 < 16:
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
        0b0000: ROAD_IMAGES["road_tile.png"],
        0b0001: ROAD_IMAGES["road_tile.png"],
        0b0010: ROAD_IMAGES["road_tile_90.png"],
        0b0011: ROAD_IMAGES["roadturn1.png"],
        0b0100: ROAD_IMAGES["road_tile.png"],
        0b0101: ROAD_IMAGES["road_tile.png"],
        0b0110: ROAD_IMAGES["roadturn2.png"],
        0b0111: ROAD_IMAGES["crossroad4.png"],
        0b1000: ROAD_IMAGES["road_tile_90.png"],
        0b1001: ROAD_IMAGES["roadturn3.png"],
        0b1010: ROAD_IMAGES["road_tile_90.png"],
        0b1011: ROAD_IMAGES["crossroad5.png"],
        0b1100: ROAD_IMAGES["roadturn4.png"],
        0b1101: ROAD_IMAGES["crossroad3.png"],
        0b1110: ROAD_IMAGES["crossroad2.png"],
        0b1111: ROAD_IMAGES["crossroad1.png"],
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
        self.neighbours = set()

        self.node = 0b0000

        self.passable = True
        self.G = 0
        self.H = 0
        self.F = 0
        self.parent_cell = None

    def contains(self, x, y):
        return Rhombus.contains(self, x, y)