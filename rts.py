import cocos as c
import heapq
import os
from random import randint
from cocos.director import director
from pyglet.window import key, mouse
from pyglet import image
from profilehooks import profile
from ctypes import cdll

triangle = cdll.LoadLibrary("triangle.so")

director.init(width=1024, height=768, do_not_scale=True)
texture_bin = image.atlas.TextureBin()
ROAD_IMAGES = {}
for file in os.listdir("images/roads"):
    ROAD_IMAGES[file] = texture_bin.add(image.load("images/roads/"+file))
GRASS_IMAGE = texture_bin.add(image.load("tiles.png"))

# Из-за динамической разбивки карты на более мелкие ромбы, размер карты должен быть степенью двойки
MAP_SIZE = 128
MAP_WIDTH = MAP_SIZE * 58
MAP_HEIGHT = MAP_SIZE * 30


class Scroller(c.layer.ScrollingManager):
    # is_event_handler = True

    def __init__(self):
        super(Scroller, self).__init__()
        self.cam_pos = [0, 0]
        self.keyboard = key.KeyStateHandler()
        director.window.push_handlers(self.keyboard)
        self.schedule_interval(self.step, 0.05)

    def check_keys(self, dt):
        if self.keyboard[key.RIGHT]:
            print('ok')

    def step(self, dt):
        k = self.keyboard
        if k[key.RIGHT]:
            self.cam_pos[0] += 32
            self.force_focus(*self.cam_pos)
        elif k[key.LEFT]:
            self.cam_pos[0] -= 32
            self.force_focus(*self.cam_pos)
        elif k[key.UP]:
            self.cam_pos[1] += 32
            self.force_focus(*self.cam_pos)
        elif k[key.DOWN]:
            self.cam_pos[1] -= 32
            self.force_focus(*self.cam_pos)


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

    @profile
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
        Делит ромб на четыре меньших ромба.
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

        self.node = 0b0000

        self.passable = True
        self.G = 0
        self.H = 0
        self.F = 0
        self.parent_cell = None

    def contains(self, x, y):
        return Rhombus.contains(self, x, y)


class Highlights(c.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super(Highlights, self).__init__()
        self.tile_highlight = c.sprite.Sprite("highlight.png")
        self.add(self.tile_highlight)

        self.roads = []

        self.batch = c.batch.BatchNode()
        self.add(self.batch)

highlights = Highlights()


class IsoMap(c.layer.ScrollableLayer):
    is_event_handler = True

    def __init__(self, atlas):
        super(IsoMap, self).__init__()
        # center_x = MAP_WIDTH // 2
        # print(center_x)
        self.batch = c.batch.BatchNode()
        self.start_cell = None
        self.prev_cell = None

        self.rhombuses = (
            Rhombus((-MAP_WIDTH//4, MAP_HEIGHT//4-15),
                    (0, MAP_HEIGHT//2-15),
                    (MAP_WIDTH//4, MAP_HEIGHT//4-15),
                    (0, -15),
                    MAP_WIDTH // 2,
                    MAP_HEIGHT // 2,
                    MAP_SIZE // 2),
            Rhombus((-MAP_WIDTH//4,
                     MAP_HEIGHT*3//4-15),
                    (0, MAP_HEIGHT-15),
                    (MAP_WIDTH//4, MAP_HEIGHT*3//4-15),
                    (0, MAP_HEIGHT//2-15),
                    MAP_WIDTH // 2,
                    MAP_HEIGHT // 2,
                    MAP_SIZE // 2),
            Rhombus((-MAP_WIDTH//2, MAP_HEIGHT//2-15),
                    (-MAP_WIDTH//4, MAP_HEIGHT*3//4-15),
                    (0, MAP_HEIGHT//2-15),
                    (-MAP_WIDTH//4, MAP_HEIGHT//4-15),
                    MAP_WIDTH // 2,
                    MAP_HEIGHT // 2,
                    MAP_SIZE // 2),
            Rhombus((0, MAP_HEIGHT//2-15),
                    (MAP_WIDTH//4, MAP_HEIGHT*3//4-15),
                    (MAP_WIDTH//2, MAP_HEIGHT//2-15),
                    (MAP_WIDTH//4, MAP_HEIGHT//4-15),
                    MAP_WIDTH // 2,
                    MAP_HEIGHT // 2,
                    MAP_SIZE // 2)
        )

        # rhombus_size = MAP_SIZE // 2
        # co = 1
        # rhombuses = self.rhombuses
        # while rhombus_size > 10:
        #     co += 1
        for rhombus in self.rhombuses:
            rhombus.subdivide()

        # print(co)

        for row in range(MAP_SIZE):
            cells.append([])
            for col in range(MAP_SIZE):
                cell = Cell(atlas, -row*29 + col*29, row*15 + col*15, row, col)
                cells[row].append(cell)
                self.batch.add(cell)

                size = MAP_SIZE
                rhombuses = self.rhombuses
                rhombus = None
                while size > 16:
                    # if rhombuses == self.rhombuses[2].subrhombuses[0].subrhombuses:
                    #     pass

                    offset_i = 0 if not rhombus else rhombus.cells[0].i
                    offset_j = 0 if not rhombus else rhombus.cells[0].j
                    limit_row = row - offset_i
                    limit_col = col - offset_j

                    if limit_row < size // 2 and limit_col < size // 2:
                        rhombus = rhombuses[0]
                    elif limit_row >= size // 2 and limit_col >= size // 2:
                        rhombus = rhombuses[1]
                    elif limit_row  >= size // 2 and limit_col < size // 2:
                        rhombus = rhombuses[2]
                    else:
                        rhombus = rhombuses[3]
                    rhombus.cells.append(cell)

                    size //= 2
                    rhombuses = rhombus.subrhombuses


                # highlights.add(c.text.Label(
                    # "{};{}".format((center_x-29) - row*29 + col*29, row*15 + col*15),
                    # "{};{}".format(cell.i, cell.j),
                    # font_size=8,
                    # position=((center_x-29) - row*29 + col*29, row*15 + col*15),
                    # anchor_x="center",
                # ))

        self.add(self.batch)

        # for rhombus in self.rhombuses[0].subrhombuses:
        #     for cell in rhombus.cells:
        #         self.add(c.sprite.Sprite("point.png", position=cell.position, color=(0, 255, 0)))

        # for rhombus in self.rhombuses[0].subrhombuses:
        # for rhombus in self.rhombuses:
        #     for i in (rhombus.left, rhombus.top, rhombus.right, rhombus.bottom):
        #         self.add(c.sprite.Sprite("point.png", position=i, color=(0, 255, 255)))
        self.add(highlights)

    def on_mouse_motion(self, x, y, dx, dy):
        # return
        x, y = director.get_virtual_coordinates(*scroller.pixel_from_screen(x, y))
        cell = self.find_cell(x, y)
        if not cell:
            return
        highlights.tile_highlight.position = cell.position

    def on_mouse_press(self, x, y, button, modifiers):
        x, y = director.get_virtual_coordinates(*scroller.pixel_from_screen(x, y))
        cell = self.find_cell(x, y)
        if not cell:
            return
        # print(cell.i, cell.j)
        # if button == mouse.LEFT:
        self.add_road(cell)
        # elif button == mouse.RIGHT:
        #     if not self.start_cell:
        self.start_cell = cell
            # else:
            #     self.calculate_path(self.start_cell, cell)

    # @profile
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        x, y = director.get_virtual_coordinates(*scroller.pixel_from_screen(x, y))
        cell = self.find_cell(x, y)
        if not cell:
            return

        if cell == self.prev_cell:
            return
        else:
            self.prev_cell = cell
        highlights.tile_highlight.position = cell.position
        # self.add_road(cell)
        path = self.calculate_path(cell)
        for cell in highlights.roads[:]:
            highlights.roads.remove(cell)
            self.remove_road(cell)
        for cell in path:
            if cell.type != Cell.ROAD:
                highlights.roads.append(cell)
                self.add_road(cell)

    def on_mouse_release(self, x, y, button, modifiers):
        self.start_cell = None
        highlights.roads.clear()

    def find_cell(self, x, y):
        rhombuses = self.rhombuses
        while rhombuses:
            for rhombus in rhombuses:
                if rhombus.contains(x, y):
                    rhombuses = rhombus.subrhombuses
                    break
            else:
                break

        for cell in rhombus.cells:
            if cell.contains(x, y):
                return cell

        return None

    def add_road(self, cell):
        cell.type = Cell.ROAD
        cell.node = 0b0000

        left = cells[cell.i+1][cell.j]
        top = cells[cell.i][cell.j+1]
        right = cells[cell.i-1][cell.j]
        bottom = cells[cell.i][cell.j-1]

        for index, neighbour in enumerate((left, top, right, bottom)):
            if neighbour.type == Cell.ROAD:
                if index == 0:
                    cell.node |= Cell.NODE_LEFT
                elif index == 1:
                    cell.node |= Cell.NODE_TOP
                elif index == 2:
                    cell.node |= Cell.NODE_RIGHT
                elif index == 3:
                    cell.node |= Cell.NODE_BOTTOM

                self.change_road(neighbour)
        cell.image = Cell.NODES[cell.node]

    def change_road(self, cell):
        cell.node = 0b0000
        n_left = cells[cell.i+1][cell.j]
        n_top = cells[cell.i][cell.j+1]
        n_right = cells[cell.i-1][cell.j]
        n_bottom = cells[cell.i][cell.j-1]
        if n_left.type == Cell.ROAD:
            cell.node |= Cell.NODE_LEFT
        if n_top.type == Cell.ROAD:
            cell.node |= Cell.NODE_TOP
        if n_right.type == Cell.ROAD:
            cell.node |= Cell.NODE_RIGHT
        if n_bottom.type == Cell.ROAD:
            cell.node |= Cell.NODE_BOTTOM
        cell.image = Cell.NODES[cell.node]

    def remove_road(self, cell):
        cell.type = Cell.GROUND
        cell.node = 0b0000
        cell.image = GRASS_IMAGE

        left = cells[cell.i+1][cell.j]
        top = cells[cell.i][cell.j+1]
        right = cells[cell.i-1][cell.j]
        bottom = cells[cell.i][cell.j-1]
        for index, neighbour in enumerate((left, top, right, bottom)):
            if neighbour.type == Cell.ROAD:
                self.change_road(neighbour)

    def calculate_path(self, finish_cell):
        """
        Функция ищет путь от стартовой клетки к финишной.
        """

        start_cell = self.start_cell
        opened_list = []
        closed_list = []
        heap = []

        orth_neighbours = [
            (0, 1),
            (1, 0),
            (0, -1),
            (-1, 0),
        ]

        current_cell = start_cell
        opened_list.append(start_cell)
        cols = len(cells)
        rows = len(cells[0])

        cells_counter = 0
        do_search = True
        while current_cell != finish_cell:
            opened_list.remove(current_cell)
            closed_list.append(current_cell)

            # random.shuffle(orth_neighbours)
            for i, j in orth_neighbours:
                cell_i = current_cell.i+i
                cell_j = current_cell.j+j
                if cell_i < 0 or cell_j < 0 or cell_i >= cols or cell_j >= rows:
                    continue

                cell = cells[cell_i][cell_j]

                if not cell.passable or cell in closed_list:
                    continue

                if cell not in opened_list:
                    cell.parent_cell = current_cell

                    cell.G = current_cell.G + 10

                    # при поиске ближайшей выделенной клетки отключаем эвристику
                    cell.H = (abs((finish_cell.i - cell_i) + abs(finish_cell.j - cell.j))) * 10
                    cell.F = cell.G + cell.H

                    opened_list.append(cell)
                    heapq.heappush(heap, (cell.F, cells_counter, cell))
                    cells_counter += 1
                else:
                    if cell.G > current_cell.G + 10:
                        cell.parent_cell = current_cell
                        cell.G = current_cell.G + 10
                        cell.F = cell.G + cell.H

            if not opened_list:
                return []

            current_cell = heapq.heappop(heap)[2]

        path = []
        current_cell = finish_cell
        path.append(finish_cell)
        while current_cell != start_cell:
            next_cell = current_cell.parent_cell
            path.append(next_cell)
            current_cell = next_cell
        path.reverse()

        return path

cells = []
level = IsoMap(GRASS_IMAGE)

scroller = Scroller()
scroller.add(level)
scene = c.scene.Scene(scroller)
director.run(scene)

