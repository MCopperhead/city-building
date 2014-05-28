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

# Из-за динамической разбивки карты на более мелкие ромбы, размер карты должен быть степенью двойки
# RHOMBUS_SIZE = размер до которого делятся вспомогательные ромбы. Чем меньше - тем быстрее будет происходить
# поиск клеток, но увеличивается время подготовки карты.
MAP_SIZE = 32
RHOMBUS_SIZE = 8
MAP_WIDTH = MAP_SIZE * 58
MAP_HEIGHT = MAP_SIZE * 30
