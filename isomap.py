import cocos as c
import heapq
import shared_data
from shared_data import Modes
from cocos.director import director
from cell import Rhombus, Cell
from highlight_layer import Highlight
from object_layer import ObjectLayer
from scroller import Scroller
from textures import GRASS_IMAGE
from objects import Tree

# Из-за динамической разбивки карты на более мелкие ромбы, размер карты должен быть степенью двойки
MAP_SIZE = 64
MAP_WIDTH = MAP_SIZE * 58
MAP_HEIGHT = MAP_SIZE * 30


class IsoMap(c.layer.ScrollableLayer):
    is_event_handler = True

    def __init__(self, atlas):
        super(IsoMap, self).__init__()
        self.batch = c.batch.BatchNode()
        self.cells = []
        self.start_cell = None
        self.current_cell = None
        self.highlight = Highlight()
        self.object_layer = ObjectLayer()
        self.scroller = Scroller()

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

        for rhombus in self.rhombuses:
            rhombus.subdivide()

        for row in range(MAP_SIZE):
            self.cells.append([])
            for col in range(MAP_SIZE):
                cell = Cell(atlas, -row*29 + col*29, row*15 + col*15, row, col)
                self.cells[row].append(cell)
                self.batch.add(cell)
                # if random.randint(1, 100) > 95:
                #     self.object_layer.batch.add(c.sprite.Sprite("tree1.png", position=cell.position, anchor=(29, 15)))
                #     cell.passable = False

                size = MAP_SIZE
                rhombuses = self.rhombuses
                rhombus = None
                while size > 16:
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

        rows = len(self.cells)
        cols = len(self.cells[0])
        for row in self.cells:
            for cell in row:
                for i, j in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    cell_i = cell.i+i
                    cell_j = cell.j+j
                    if cell_i < 0 or cell_j < 0 or cell_i >= cols or cell_j >= rows:
                        continue
                    cell.neighbours.add(self.cells[cell_i][cell_j])

        self.add(self.batch)
        self.add(self.object_layer)
        self.add(self.highlight)

    def on_mouse_motion(self, x, y, dx, dy):
        if y < 150:
            return
        x, y = director.get_virtual_coordinates(*self.scroller.pixel_from_screen(x, y))
        cell = self.find_cell(x, y)
        if not cell:
            return
        self.highlight.tile_highlight.position = cell.position

    def on_mouse_press(self, x, y, button, modifiers):
        if y < 150:
            return

        x, y = director.get_virtual_coordinates(*self.scroller.pixel_from_screen(x, y))
        cell = self.find_cell(x, y)
        if cell and cell.passable:
            if shared_data.mode == Modes.ROAD:
                self.add_road(cell)
                self.start_cell = cell
            elif shared_data.mode == Modes.TREE:
                self.add_tree(cell)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if y < 150:
            return
        x, y = director.get_virtual_coordinates(*self.scroller.pixel_from_screen(x, y))
        cell = self.find_cell(x, y)
        if not cell:
            return

        self.highlight.tile_highlight.position = cell.position
        if shared_data.mode == Modes.ROAD:
            if not self.start_cell:
                return
            if cell != self.current_cell:
                self.current_cell = cell
                self.draw_road_path(cell)
        elif shared_data.mode == Modes.TREE:
            if cell.passable and cell.type != Cell.ROAD:
                self.add_tree(cell)

    def on_mouse_release(self, x, y, button, modifiers):
        self.start_cell = None
        self.highlight.roads.clear()

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

    def add_tree(self, cell):
        self.object_layer.batch.add(Tree(position=cell.position))
        cell.passable = False

    def draw_road_path(self, cell):
        path = self.calculate_path(cell)
        for cell in self.highlight.roads[:]:
            self.highlight.roads.remove(cell)
            self.remove_road(cell)
        # пропускаем стартовую клетку, так как дорога туда уже добавилась при нажатии кнопки
        for cell in path[1:]:
            if cell.type != Cell.ROAD:
                self.highlight.roads.append(cell)
                self.add_road(cell)

    def add_road(self, cell):
        cell.type = Cell.ROAD
        cell.node = 0b0000

        left = self.cells[cell.i+1][cell.j]
        top = self.cells[cell.i][cell.j+1]
        right = self.cells[cell.i-1][cell.j]
        bottom = self.cells[cell.i][cell.j-1]

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
        n_left = self.cells[cell.i+1][cell.j]
        n_top = self.cells[cell.i][cell.j+1]
        n_right = self.cells[cell.i-1][cell.j]
        n_bottom = self.cells[cell.i][cell.j-1]
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

        left = self.cells[cell.i+1][cell.j]
        top = self.cells[cell.i][cell.j+1]
        right = self.cells[cell.i-1][cell.j]
        bottom = self.cells[cell.i][cell.j-1]
        for index, neighbour in enumerate((left, top, right, bottom)):
            if neighbour.type == Cell.ROAD:
                self.change_road(neighbour)

    def calculate_path(self, finish_cell):
        """
        Функция ищет путь от стартовой клетки к финишной.
        """
        start_cell = self.start_cell
        closed_list = set()
        opened_list = set()
        heap = []
        opened_list.add(start_cell)
        heap.append((0, 0, start_cell))
        cells_counter = 1
        while opened_list:
            current_cell = heapq.heappop(heap)[2]
            if current_cell == finish_cell:
                break
            opened_list.remove(current_cell)
            closed_list.add(current_cell)
            for cell in current_cell.neighbours:
                if cell not in closed_list and cell.passable:
                    if cell not in opened_list:
                        cell.G = current_cell.G + 1
                        cell.H = abs(finish_cell.i - cell.i) + abs(finish_cell.j - cell.j)
                        cell.F = cell.G + cell.H
                        cell.parent_cell = current_cell
                        opened_list.add(cell)
                        heapq.heappush(heap, (cell.F, cells_counter, cell))
                        cells_counter += 1
                    else:
                        if cell.G > current_cell.G + 1:
                            cell.G = current_cell.G + 1
                            cell.F = cell.G + cell.H
                            cell.parent_cell = current_cell

            if not heap:
                return []

        path = []
        current_cell = finish_cell
        path.append(finish_cell)
        while current_cell != start_cell:
            next_cell = current_cell.parent_cell
            path.append(next_cell)
            current_cell = next_cell
        path.reverse()

        return path
