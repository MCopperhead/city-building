import cocos as c
import heapq
import shared_data
from pyglet.window import key
from shared_data import Modes, MAP_SIZE, MAP_WIDTH, MAP_HEIGHT, RHOMBUS_SIZE
from cocos.director import director
from cell import Rhombus, Cell
from highlight_layer import Highlight
from interface import Interface
from object_layer import ObjectLayer
from scroller import Scroller
from objects import Tree, House, Pillar, Building, Stairs, Wall
# from profilehooks import profile

interface = Interface()


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
                cell = Cell(atlas, -row*30 + col*30, row*15 + col*15, row, col)
                self.cells[row].append(cell)
                self.batch.add(cell)
                # if random.randint(1, 100) > 95:
                #     self.object_layer.batch.add(c.sprite.Sprite("tree1.png", position=cell.position, anchor=(29, 15)))
                #     cell.passable = False

                size = MAP_SIZE
                rhombuses = self.rhombuses
                rhombus = None
                while size > RHOMBUS_SIZE:
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
                for i, j in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    cell_i = cell.i+i
                    cell_j = cell.j+j
                    if cell_i < 0 or cell_j < 0 or cell_i >= cols or cell_j >= rows:
                        continue
                    cell.neighbours.append(self.cells[cell_i][cell_j])

        self.marked_cells = []
        self.pillar_cell = None
        self.population = 0

        self.add(self.batch)
        self.add(self.object_layer)
        self.add(self.highlight)

        self.buildings_queue = set()
        self.schedule_interval(self.process_buildings_queue, 1)

    def on_mouse_motion(self, x, y, dx, dy):
        if y < 150 or interface.modal_window:
            return
        x, y = director.get_virtual_coordinates(*self.scroller.pixel_from_screen(x, y))
        cell = self.find_cell(x, y)
        if not cell:
            return
        self.highlight.tile_highlight.position = cell.position

    def on_mouse_press(self, x, y, button, modifiers):
        if y < 150 or interface.modal_window:
            return
        x, y = director.get_virtual_coordinates(*self.scroller.pixel_from_screen(x, y))
        if shared_data.mode == Modes.NORMAL:
            buildings = [(building.z, building) for building in self.object_layer.buildings if building.contains(x, y)]
            obj = min(buildings)[1]
            interface.show_infocard(obj)
        else:
            cell = self.find_cell(x, y)
            if cell:
                self.start_cell = cell
                if shared_data.mode == Modes.DELETE:
                    self.mark_cells(cell)
                elif shared_data.mode == Modes.TREE:
                    self.object_layer.add_object(cell, Tree)
                elif shared_data.mode == Modes.ROAD:
                    if cell.passable:
                        cell.add_road()
                elif shared_data.mode == Modes.HOUSING:
                    self.object_layer.add_object(cell, House, building=True)
                elif shared_data.mode == Modes.PILLAR:
                    if not self.pillar_cell:
                        if self.object_layer.add_object(cell, Pillar):
                            self.pillar_cell = cell
                            cell.type = Cell.ROAD
                elif shared_data.mode in Modes.WALL:
                    self.object_layer.add_wall(cell, int(shared_data.mode[-1]))
                elif shared_data.mode == Modes.STAIRS:
                    self.object_layer.add_object(cell, Stairs)

                    # Place road at bottom of the stairs, so stairs will have correct road continuation.
                    top_cell = self.cells[cell.i+1][cell.j+1]
                    top_cell.add_road()
                    cell.add_road()

                    # Set cells at bottom and at top of the stairs to neighbours of each other,
                    # so they will be connected when finding path.
                    right_cell = self.cells[cell.i-1][cell.j]
                    left_cell = self.cells[cell.i+2][cell.j+1]
                    right_cell.neighbours.append(left_cell)
                    left_cell.neighbours.append(right_cell)
                    right_cell.level = -1
                elif shared_data.mode in Modes.LEVEL:
                    if shared_data.mode == Modes.LEVEL[0]:
                        cell.level += 1
                    if shared_data.mode == Modes.LEVEL[1]:
                        cell.level -= 1
                    self.object_layer.add(c.text.Label(str(cell.level), position=cell.position))

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if y < 150 or interface.modal_window:
            return
        x, y = director.get_virtual_coordinates(*self.scroller.pixel_from_screen(x, y))
        cell = self.find_cell(x, y)
        if not cell:
            return
        self.highlight.tile_highlight.position = cell.position
        if shared_data.mode == Modes.ROAD:
            if self.start_cell and self.start_cell.passable and cell.passable:
                if cell != self.current_cell:
                    self.current_cell = cell
                    self.draw_road_path(cell)
        elif shared_data.mode == Modes.TREE:
            self.object_layer.add_object(cell, Tree)
        elif shared_data.mode == Modes.HOUSING:
            self.object_layer.add_object(cell, House, building=True)
        elif shared_data.mode == Modes.DELETE:
            if self.start_cell:
                self.mark_cells(cell)

    def on_mouse_release(self, x, y, button, modifiers):
        if interface.modal_window:
            return

        self.start_cell = None
        self.highlight.roads.clear()

        if shared_data.mode == Modes.DELETE:
            self.clear_cells()
            if y > 150:
                self.calculate_buildings_availability()
        elif shared_data.mode == Modes.ROAD:
            if y > 150:
                self.populate_buildings_queue()
        elif shared_data.mode == Modes.HOUSING:
            self.populate_buildings_queue()
        elif shared_data.mode == Modes.PILLAR:
            if y > 150:
                self.populate_buildings_queue()

    def populate_buildings_queue(self):
        self.calculate_buildings_availability()
        for building in self.object_layer.buildings:
            if isinstance(building, House) and building.connected and not building.is_full():
                self.buildings_queue.add(building)

    def process_buildings_queue(self, dt):
        if self.buildings_queue:
            building = self.buildings_queue.pop()
            building.population += 1
            self.population += 1
            interface.update_population(self.population)
            path = self.calculate_path(building.cell, self.pillar_cell, only_roads=True)
            self.object_layer.summon_creature(path)
            if not building.is_full():
                self.buildings_queue.add(building)

    def mark_cells(self, cell):
        self.unmark_cells()
        if self.start_cell.i < cell.i:
            range_i = (self.start_cell.i, cell.i+1)
        else:
            range_i = (cell.i, self.start_cell.i+1)
        if self.start_cell.j < cell.j:
            range_j = (self.start_cell.j, cell.j+1)
        else:
            range_j = (cell.j, self.start_cell.j+1)
        for i in range(*range_i):
            for j in range(*range_j):
                cell_to_mark = self.cells[i][j]
                cell_to_mark.color = (255, 0, 0)
                if cell_to_mark.child:
                    cell_to_mark.child.color = (255, 0, 0)
                self.marked_cells.append(cell_to_mark)

    def unmark_cells(self):
        for marked_cell in self.marked_cells:
            marked_cell.color = (255, 255, 255)
            if marked_cell.child:
                marked_cell.child.color = (255, 255, 255)
        self.marked_cells.clear()

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

    def clear_cells(self):
        for cell in self.marked_cells:
            if cell == self.pillar_cell:
                self.pillar_cell = None
            if cell.child:
                if isinstance(cell.child, Building):
                    self.object_layer.buildings.remove(cell.child)
                cell.child.kill()
                cell.child = None
                cell.passable = True
            if cell.type == Cell.ROAD:
                cell.remove_road()
        self.unmark_cells()

    def draw_road_path(self, cell):
        path = self.calculate_path(cell)
        for cell in self.highlight.roads[:]:
            self.highlight.roads.remove(cell)
            cell.remove_road()
        # пропускаем стартовую клетку, так как дорога туда уже добавилась при нажатии кнопки
        for cell in path[1:]:
            if cell.type != Cell.ROAD:
                self.highlight.roads.append(cell)
                cell.add_road()

    def calculate_path(self, finish_cell, start_cell=None, only_roads=False):
        """
        Finding path from start cell to finish cell.
        """
        # TODO: add "level" property to cells
        # this must be a virtual level of cell above the ground.
        # When finding path, enter to the another level is available only through the stairs.
        # So, level of current cell is compares with level of neighbour cell, and if their levels are different
        # the path here is blocked. And the stairs must have two levels at the same time.

        if not start_cell:
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
                if cell == finish_cell or (cell not in closed_list and cell.passable):
                    if cell.level != -1 and current_cell.level != -1:
                        if cell.level != current_cell.level:
                            continue
                    if only_roads and cell.type != Cell.ROAD and cell != finish_cell:
                        closed_list.add(cell)
                        continue
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
        else:
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

    def calculate_buildings_availability(self):
        """
        Checks which Houses connected with road to Pillar.
        """
        for building in self.object_layer.buildings:
            building.connected = False

        start_cell = self.pillar_cell
        if not start_cell:
            return

        closed_list = set()
        opened_list = set()
        opened_list.add(start_cell)
        while opened_list:
            current_cell = opened_list.pop()
            closed_list.add(current_cell)
            for cell in current_cell.neighbours:
                if cell not in closed_list:
                    if cell.type == Cell.ROAD:
                        opened_list.add(cell)
                    elif isinstance(cell.child, Building):
                        cell.child.connected = True
                        closed_list.add(cell)

        # for building in self.object_layer.buildings:
        #     if building.connected:
        #         building.color = (0, 255, 0)
        #     else:
        #         building.color = (255, 0, 0)

    # def change_cell_level(self, start_cell, level):
    #     closed_list = set()
    #     opened_list = set()
    #     opened_list.add(start_cell)
    #     while opened_list:
    #         current_cell = opened_list.pop()
    #         closed_list.add(current_cell)
    #
    #         if current_cell.wall == "thick":
    #             continue
    #         elif current_cell.wall == "thin":
    #             current_cell.level += level
    #             continue
    #         current_cell.level += level
    #         for cell in current_cell.neighbours:
    #             if cell not in closed_list:
    #                 # if cell.wall:
    #                 #     if cell.wall == "thin":
    #                 #         cell.level += 1
    #                 #     closed_list.add(cell)
    #                 #     continue
    #                 if cell not in opened_list:
    #                     opened_list.add(cell)
    #
    #
    #     for row in self.cells:
    #         for cell in row:
    #             if cell.level == 1:
    #                 cell.color = (0, 255, 0)