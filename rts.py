import cocos as c

from cocos.director import director
director.init(width=1024, height=768, do_not_scale=True)

from isomap import IsoMap
from scroller import scroller
from textures import GRASS_IMAGE

level = IsoMap(GRASS_IMAGE)
scroller.add(level)
scene = c.scene.Scene(scroller)
director.run(scene)

