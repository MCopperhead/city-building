class Modes():
    NORMAL = "normal"
    ROAD = "road"
    TREE = "tree"
    DELETE = "delete"
    HOUSING = "housing"
    PILLAR = "pillar"
    WALL = ("wall1", "wall2", "wall3", "wall4", "wall5", "wall6", "wall7", "wall8")
    STAIRS = "stairs"
    LEVEL = ("level_add", "level_sub")


mode = Modes.NORMAL

# MAP_SIZE must be a power of two, because map is subdivided on small rhombuses.
# RHOMBUS_SIZE - size of helper rhombuses. The smaller - the faster will be cell finding, but longer map loading time.
MAP_SIZE = 32
RHOMBUS_SIZE = 8
MAP_WIDTH = MAP_SIZE * 58
MAP_HEIGHT = MAP_SIZE * 30
