import cocos as c
import shared_data
from cocos.director import director
from buttons import ButtonRoad, ButtonCross, ButtonTree, ButtonHammer, ButtonHouse, ButtonPillar, SwitcherMain, \
    SwitcherWall, ButtonWall


class Interface(c.layer.Layer):
    is_event_handler = True
    instance = None

    def __init__(self):
        super(Interface, self).__init__()

        # TODO: главная панель состоит из нескольких изображений:
        # Центральное: фиксированного размера с кнопками и миникартой, посередине.
        # Разрешение игры по ширине не должно быть меньше этого центрального изображения.
        # По бокам чисто декоративные картинки, которые будут заполнять экран по бокам от центрального изображения,
        # когда разрешение игры больше, чем центральная картинка.
        self._main_panel = c.sprite.Sprite("main_panel.png", position=(512, 75))
        self.add(self._main_panel)

        self._switchers = [SwitcherMain(), SwitcherWall()]
        for switcher in self._switchers:
            self.add(switcher)

        self._active_buttons = []
        self.buttons = {
            "main": (ButtonRoad(), ButtonTree(), ButtonCross(), ButtonHammer(), ButtonHouse(), ButtonPillar()),
            "wall": []
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
        for button in self._switchers + self._active_buttons:
            if button.contains(x, y):
                self._pressed_button = button
                button.on_press()
                break

    def on_mouse_release(self, x, y, m_button, modifiers):
        x, y = director.get_virtual_coordinates(x, y)
        for button in self._switchers + self._active_buttons:
            if button.contains(x, y):
                button.on_release()
                break

        self._pressed_button = None

    def on_mouse_drag(self, x, y, dx, dy, m_button, modifiers):
        x, y = director.get_virtual_coordinates(x, y)
        for button in self._switchers + self._active_buttons:
            if button.contains(x, y) and self._pressed_button == button:
                button.on_press()
                break
            elif (not button.contains(x, y)) and self._pressed_button == button:
                button.on_release()
                break
