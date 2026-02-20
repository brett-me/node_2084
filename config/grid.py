class GridConfig:
    SCREEN_W = 800
    SCREEN_H = 600

    CELL_SIZE = 16
    MAP_COLS = 50
    MAP_ROWS = 37

    MAP_W = MAP_COLS * CELL_SIZE
    MAP_H = MAP_ROWS * CELL_SIZE

    MAP_OFFSET_X = (SCREEN_W - MAP_W) // 2
    MAP_OFFSET_Y = (SCREEN_H - MAP_H) // 2 