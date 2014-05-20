import cocos as c
from cocos.director import director
from pyglet.window import key


director.init(width=1024, height=768, do_not_scale=True)

class Scroller(c.layer.ScrollingManager):
    is_event_handler = True

    def __init__(self):
        super(Scroller, self).__init__()
        self.cam_pos = [0, 0]

    def on_key_press(self, pressed_key, modifiers):
        if pressed_key == key.RIGHT:
            self.cam_pos[0] += 32
        elif pressed_key == key.LEFT:
            self.cam_pos[0] -= 32
        elif pressed_key == key.UP:
            self.cam_pos[1] += 32
        elif pressed_key == key.DOWN:
            self.cam_pos[1] -= 32
        self.force_focus(*self.cam_pos)


class Cell(c.sprite.Sprite):
    def __init__(self, image, x, y):
        super(Cell, self).__init__(image)
        self.position = (x, y)
        self.left = (x-29, y)
        self.right = (x+29, y)
        self.top = (x, y+15)
        self.bottom = (x, y-15)

    def contains(self, x, y):
        for x1, y1, x2, y2, x3, y3 in (self.left+self.top+self.right, self.left+self.bottom+self.right):
            s = abs(x2*y3-x3*y2-x1*y3+x3*y1+x1*y2-x2*y1)
            s1 = abs(x2*y3-x3*y2-x*y3+x3*y+x*y2-x2*y)
            s2 = abs(x*y3-x3*y-x1*y3+x3*y1+x1*y-x*y1)
            s3 = abs(x2*y-x*y2-x1*y+x*y1+x1*y2-x2*y1)

            if s == s1+s2+s3:
                return True

        return False


class Highlights(c.layer.Layer):
    is_event_handler = True
    def __init__(self):
        super(Highlights, self).__init__()
        self.tile_highlight = c.sprite.Sprite("highlight.png")
        self.add(self.tile_highlight)

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = director.get_virtual_coordinates(*scroller.pixel_from_screen(x, y))
        for cell in cells:
            if cell.contains(x, y):
                self.tile_highlight.position = cell.position
                break

    def on_mouse_press(self, x, y, button, modifiers):
        x, y = director.get_virtual_coordinates(*scroller.pixel_from_screen(x, y))
        for cell in cells:
            if cell.contains(x, y):
                self.add(c.sprite.Sprite("road_tile.png", position=cell.position))
                break

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        x, y = director.get_virtual_coordinates(*scroller.pixel_from_screen(x, y))
        for cell in cells:
            if cell.contains(x, y):
                self.add(c.sprite.Sprite("road_tile.png", position=cell.position))
                break

layer = Highlights()


class IsoMap(c.layer.ScrollableLayer):
    is_event_handler = True

    def __init__(self, atlas):
        super(IsoMap, self).__init__()
        map_size = 20
        map_width = map_size * 58 + 29
        map_height = map_size * 30
        center_x = map_width // 2
        self.batch = c.batch.BatchNode()

        for row in range(map_size):
            for col in range(map_size):
                cell = Cell(atlas, (center_x-29) - row*29 + col*29, row*15 + col*15)
                cells.append(cell)
                self.batch.add(cell)

                # layer.add(c.text.Label(
                #     "{};{}".format((center_x-29) - row*29 + col*29, row*15 + col*15),
                #     font_size=8,
                #     position=((center_x-29) - row*29 + col*29, row*15 + col*15),
                #     anchor_x="center",
                # ))

        self.add(self.batch)

        self.add(layer)


cells = []
level = IsoMap('tiles.png')

scroller = Scroller()
scroller.add(level)
scene = c.scene.Scene(scroller)
director.run(scene)

