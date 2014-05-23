import cocos as c
import shared_data
from pyglet import image
from shared_data import Modes
from highlight_layer import Highlight

highlight = Highlight()


class Button(c.sprite.Sprite):
    """
    Класс для кнопок, управляющий сменой их вида при нажатии.
    """
    def __init__(self, *args, **kwargs):
        super(Button, self).__init__(*args, **kwargs)
        self.base_image = args[0]
        self.normal = image.load(self.base_image)
        self.pressed = image.load("{}_pressed.png".format(self.base_image[:-4]))

    def on_press(self):
        self.image = self.pressed
        self.image_anchor = (21, 14)

    def on_release(self):
        self.image = self.normal
        self.image_anchor = (24, 16)


class ButtonRoad(Button):
    def __init__(self):
        super(ButtonRoad, self).__init__("images/buttons/road.png", position=(512, 75))

    def on_release(self):
        super(ButtonRoad, self).on_release()
        shared_data.mode = Modes.ROAD
        highlight.show()


class ButtonTree(Button):
    def __init__(self):
        super(ButtonTree, self).__init__("images/buttons/tree.png", position=(572, 75))

    def on_release(self):
        super(ButtonTree, self).on_release()
        shared_data.mode = Modes.TREE
        highlight.show()


class ButtonCross(Button):
    def __init__(self):
        super(ButtonCross, self).__init__("images/buttons/cross.png", position=(632, 75))

    def on_release(self):
        super(ButtonCross, self).on_release()
        shared_data.mode = Modes.NORMAL
        highlight.hide()


class ButtonHammer(Button):
    def __init__(self):
        super(ButtonHammer, self).__init__("images/buttons/hammer.png", position=(512, 31))

    def on_release(self):
        super(ButtonHammer, self).on_release()
        shared_data.mode = Modes.DELETE
        highlight.show()