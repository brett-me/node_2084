def parse_markers(grid):
    """
    grid: 2D list of tokens (rows then cols)
    Returns a dict of marker data without pygame imports.
    """
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    spawn_cell = None
    sensors = []          # list of (c, r, token) where token in ^ v < >
    task_cells = {}       # "A".."D" -> list[(c,r)]
    discovery_cells = {}  # "x".."z" -> list[(c,r)]
    anomalies = []        # list[(c,r,token)] e.g. "o","p"
    dynamic_walls = {"!": [], "?": []}  # cells that can change later

    for r in range(rows):
        for c in range(cols):
            t = grid[r][c]

            if t == "S":
                spawn_cell = (c, r)

            elif t in ("^", "v", "<", ">"):
                sensors.append((c, r, t))

            elif t in ("A", "B", "C", "D"):
                task_cells.setdefault(t, []).append((c, r))

            elif t in ("x", "y", "z"):
                discovery_cells.setdefault(t, []).append((c, r))

            elif t in ("!", "?"):
                dynamic_walls[t].append((c, r))

            elif t in ("o", "p"):
                anomalies.append((c, r, t))

    return {
        "spawn_cell": spawn_cell,
        "sensors": sensors,
        "task_cells": task_cells,
        "discovery_cells": discovery_cells,
        "dynamic_walls": dynamic_walls,
        "anomalies": anomalies,
    }