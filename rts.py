import cocos as c
from cocos.director import director
from isomap import IsoMap
from scroller import Scroller
from textures import GRASS_IMAGE


director.init(width=1024, height=768, do_not_scale=True)
level = IsoMap(GRASS_IMAGE)
scroller = Scroller()
scroller.add(level)
scene = c.scene.Scene(scroller)
director.run(scene)

