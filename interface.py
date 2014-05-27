import cocos as c
from cocos.director import director
from buttons import ButtonRoad, ButtonCross, ButtonTree, ButtonHammer, ButtonHouse, ButtonPillar


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

        # self.button_road = Button("images/buttons/road.png", position=(512, 75))
        # self.button_road = ButtonRoad()
        self._buttons = {ButtonRoad(), ButtonTree(), ButtonCross(), ButtonHammer(), ButtonHouse(), ButtonPillar()}
        for button in self._buttons:
            self.add(button)
        self._pressed_button = None

        self._population = c.text.Label("Pop.: 0", position=(300, 75))
        self.add(self._population)
        # self.buttons = {self.button_road}

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Interface, cls).__new__(cls)
        return cls.instance

    def update_population(self, population):
        self._population.element.text = "Pop.: {}".format(population)

    def on_mouse_press(self, x, y, m_button, modifiers):
        x, y = director.get_virtual_coordinates(x, y)
        for button in self._buttons:
            if button.contains(x, y):
                self._pressed_button = button
                button.on_press()
                break

    def on_mouse_release(self, x, y, m_button, modifiers):
        x, y = director.get_virtual_coordinates(x, y)
        for button in self._buttons:
            if button.contains(x, y):
                button.on_release()
                break

        self._pressed_button = None

    def on_mouse_drag(self, x, y, dx, dy, m_button, modifiers):
        x, y = director.get_virtual_coordinates(x, y)
        for button in self._buttons:
            if button.contains(x, y) and self._pressed_button == button:
                button.on_press()
                break
            elif (not button.contains(x, y)) and self._pressed_button == button:
                button.on_release()
                break
