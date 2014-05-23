class Modes():
    NORMAL = "normal"
    ROAD = "road"
    TREE = "tree"
    DELETE = "delete"


mode = Modes.NORMAL

# Из-за динамической разбивки карты на более мелкие ромбы, размер карты должен быть степенью двойки
MAP_SIZE = 64
MAP_WIDTH = MAP_SIZE * 58
MAP_HEIGHT = MAP_SIZE * 30