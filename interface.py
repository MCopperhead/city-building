import cocos as c
import textures
import objects
from cocos.director import director
from buttons import ButtonRoad, ButtonCross, ButtonTree, ButtonHammer, ButtonHouse, ButtonPillar, SwitcherMain, \
    SwitcherWall, ButtonWall, ButtonLevelAdd, ButtonLevelSub, ButtonStairs, ButtonClose


class InfoCard(c.sprite.Sprite):
    def __init__(self, obj):
        window_size = director.get_window_size()
        super(InfoCard, self).__init__(textures.INFOCARD, position=(window_size[0] // 2, window_size[1] // 2))
        if isinstance(obj, objects.House):
            self.add(c.text.Label("Population: {}".format(obj.population), position=(50, 100), color=(152, 47, 0, 255)))

        self.button_close = ButtonClose(position=(0, 0))
        self.add(self.button_close)

    def close(self):
        self.kill()
        self.parent.clear_modal()


class Interface(c.layer.Layer):
    is_event_handler = True
    instance = None

    def __init__(self):
        super(Interface, self).__init__()

        # TODO: main panel must consist from several images:
        # Central: fixed size, with buttons and minimap.
        # Window width resolution must be larger or equal than central image width.
        # Decorative images on central image left and right sides, for filling the empty space if window width resolution
        # is bigger than central image width.
        self._main_panel = c.sprite.Sprite("main_panel.png", position=(512, 75))
        self.add(self._main_panel)
        self.modal_window = None
        self._switchers = [SwitcherMain(), SwitcherWall()]
        for switcher in self._switchers:
            self.add(switcher)

        self._active_buttons = []
        self._modal_buttons = []
        self.buttons = {
            "main": (ButtonRoad(), ButtonTree(), ButtonCross(), ButtonHammer(), ButtonHouse(), ButtonPillar()),
            "wall": [ButtonLevelAdd(), ButtonLevelSub(), ButtonStairs()]
        }

        x = 512
        for i in range(8):
            if i < 4:
                y = 75
            else:
                y = 31
                x = 272
            self.buttons['wall'].append(ButtonWall(i+1, position=(x + i*60, y)))

        self._pressed_button = None
        self._population = c.text.Label("Pop.: 0", position=(300, 75))
        self.add(self._population)

        self.change_panel("main")

    def clear_panel(self):
        for button in self._active_buttons:
            button.kill()

        self._active_buttons.clear()

    def change_panel(self, panel):
        self.clear_panel()
        for button in self.buttons[panel]:
            self._active_buttons.append(button)
            self.add(button)

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Interface, cls).__new__(cls)
        return cls.instance

    def update_population(self, population):
        self._population.element.text = "Pop.: {}".format(population)

    def on_mouse_press(self, x, y, m_button, modifiers):
        x, y = director.get_virtual_coordinates(x, y)
        if self.modal_window:
            button_set = self._modal_buttons
            x, y = x-self.modal_window.x, y-self.modal_window.y
        else:
            button_set = self._switchers + self._active_buttons

        for button in button_set:
            if button.contains(x, y):
                self._pressed_button = button
                button.on_press()
                break

    def on_mouse_release(self, x, y, m_button, modifiers):
        x, y = director.get_virtual_coordinates(x, y)
        if self.modal_window:
            button_set = self._modal_buttons
            x, y = x-self.modal_window.x, y-self.modal_window.y
        else:
            button_set = self._switchers + self._active_buttons

        for button in button_set:
            if button.contains(x, y) and button == self._pressed_button:
                button.restore_image()
                button.on_release()
                break

        self._pressed_button = None

    def on_mouse_drag(self, x, y, dx, dy, m_button, modifiers):
        x, y = director.get_virtual_coordinates(x, y)
        if self.modal_window:
            button_set = self._modal_buttons
            x, y = x-self.modal_window.x, y-self.modal_window.y
        else:
            button_set = self._switchers + self._active_buttons

        for button in button_set:
            if button.contains(x, y) and self._pressed_button == button:
                button.on_press()
                break
            elif (not button.contains(x, y)) and self._pressed_button == button:
                button.restore_image()
                break

    def show_infocard(self, obj):
        self.modal_window = InfoCard(obj)
        self._modal_buttons.append(self.modal_window.button_close)
        self.add(self.modal_window)

    def clear_modal(self):
        self.modal_window = None
        self._modal_buttons.clear()