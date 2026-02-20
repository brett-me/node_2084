class GridConfig:
    COLS = 50
    ROWS = 37
    CELL = 16
    SCREEN_W = 800
    SCREEN_H = 600

    @staticmethod
    def offset():
        # centre the 592px tall grid inside 600px
        grid_h = GridConfig.ROWS * GridConfig.CELL  # 592
        return (0, (GridConfig.SCREEN_H - grid_h) // 2)  # (0, 4)
