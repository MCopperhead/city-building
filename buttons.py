import cocos as c
import shared_data
from pyglet import image
from shared_data import Modes
from highlight_layer import Highlight
from textures import BUTTON_IMAGES, WALLS

highlight = Highlight()


class Button(c.sprite.Sprite):
    """
    Manages the button appearance when it is pressed.
    """
    def __init__(self, *args, **kwargs):
        self.base_image = args[0]
        # self.normal = image.load(self.base_image)
        self.normal = BUTTON_IMAGES[self.base_image]
        super(Button, self).__init__(self.normal, *args[1:], **kwargs)
        # self.pressed = image.load("{}_pressed.png".format(self.base_image[:-4]))
        self.pressed = BUTTON_IMAGES["{}_pressed.png".format(self.base_image[:-4])]

    def restore_image(self):
        self.image = self.normal
        self.image_anchor = (24, 16)

    def on_press(self):
        self.image = self.pressed
        self.image_anchor = (21, 14)

    def on_release(self):
        pass


class ButtonRoad(Button):
    def __init__(self):
        super(ButtonRoad, self).__init__("road.png", position=(512, 75))

    def on_release(self):
        super(ButtonRoad, self).on_release()
        shared_data.mode = Modes.ROAD
        highlight.show()


class ButtonTree(Button):
    def __init__(self):
        super(ButtonTree, self).__init__("tree.png", position=(572, 75))

    def on_release(self):
        super(ButtonTree, self).on_release()
        shared_data.mode = Modes.TREE
        highlight.show()


class ButtonCross(Button):
    def __init__(self):
        super(ButtonCross, self).__init__("cross.png", position=(632, 75))

    def on_release(self):
        super(ButtonCross, self).on_release()
        shared_data.mode = Modes.NORMAL
        highlight.hide()


class ButtonHammer(Button):
    def __init__(self):
        super(ButtonHammer, self).__init__("hammer.png", position=(512, 31))

    def on_release(self):
        super(ButtonHammer, self).on_release()
        shared_data.mode = Modes.DELETE
        highlight.show()


class ButtonHouse(Button):
    def __init__(self):
        super(ButtonHouse, self).__init__("house.png", position=(572, 31))

    def on_release(self):
        super(ButtonHouse, self).on_release()
        shared_data.mode = Modes.HOUSING
        highlight.show()


class ButtonPillar(Button):
    def __init__(self):
        super(ButtonPillar, self).__init__("pillar.png", position=(632, 31))

    def on_release(self):
        super(ButtonPillar, self).on_release()
        shared_data.mode = Modes.PILLAR
        highlight.show()


class ButtonWall(Button):
    def __init__(self, index, **kwargs):
        super(ButtonWall, self).__init__("wall{}.png".format(index), **kwargs)
        self.index = index

    def on_release(self):
        super(ButtonWall, self).on_release()
        shared_data.mode = Modes.WALL[self.index-1]
        highlight.show()


class ButtonStairs(Button):
    def __init__(self):
        super(ButtonStairs, self).__init__("stairs.png", position=(752, 75))

    def on_release(self):
        super(ButtonStairs, self).on_release()
        shared_data.mode = Modes.STAIRS
        highlight.show()


class ButtonLevelAdd(Button):
    def __init__(self):
        super(ButtonLevelAdd, self).__init__("cell_level_add.png", position=(812, 75))

    def on_release(self):
        super(ButtonLevelAdd, self).on_release()
        shared_data.mode = Modes.LEVEL[0]
        highlight.show()


class ButtonLevelSub(Button):
    def __init__(self):
        super(ButtonLevelSub, self).__init__("cell_level_sub.png", position=(812, 31))

    def on_release(self):
        super(ButtonLevelSub, self).on_release()
        shared_data.mode = Modes.LEVEL[1]
        highlight.show()


class ButtonClose(Button):
    def __init__(self, **kwargs):
        super(ButtonClose, self).__init__("close.png", **kwargs)

    def on_press(self):
        self.image = self.pressed
        self.image_anchor = (43, 11)

    def on_release(self):
        super(ButtonClose, self).on_release()
        self.image_anchor = (47, 12)
        self.parent.close()


class Switcher(c.sprite.Sprite):
    def on_press(self):
        self.parent.change_panel(self.type)

    def on_release(self):
        pass

    def restore_image(self):
        pass


class SwitcherMain(Switcher):
    def __init__(self):
        super(SwitcherMain, self).__init__(BUTTON_IMAGES["switcher_main.png"], position=(512, 119))
        self.type = "main"


class SwitcherWall(Switcher):
    def __init__(self):
        super(SwitcherWall, self).__init__(BUTTON_IMAGES["switcher_wall.png"], position=(572, 119))
        self.type = "wall"