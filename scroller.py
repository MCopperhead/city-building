import cocos as c
from pyglet.window import key
from cocos.director import director


class Scroller(c.layer.ScrollingManager):
    instance = None

    def __init__(self):
        super(Scroller, self).__init__()
        self.cam_pos = [0, 0]
        self.keyboard = key.KeyStateHandler()
        director.window.push_handlers(self.keyboard)
        self.schedule_interval(self.step, 0.05)

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Scroller, cls).__new__(cls)
        return cls.instance

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