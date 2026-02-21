import pygame
from config.palette import Colour

def draw_markers(screen, map_obj, phosphor_alpha):
    """
    map_obj is your Map instance.
    Assumes Map exposes:
      - cell_to_world(c,r, centre=False)
      - cell_rect(c,r)
      - marker_data dict
    """
    col = Colour.phosphor_colour(Colour.BRIGHT_GREEN, phosphor_alpha)

    md = map_obj.marker_data

    # Spawn cell (outline)
    c, r = md["spawn_cell"]
    pygame.draw.rect(screen, col, map_obj.cell_rect(c, r), 1)

    # Sensors (small orange dot + direction glyph optional)
    for c, r, token in md["sensors"]:
        cx, cy = map_obj.cell_to_world(c, r, centre=True)
        pygame.draw.circle(screen, Colour.SENSOR, (cx, cy), 3)

        # optional: tiny direction line
        dx, dy = 0, 0
        if token == "^": dy = -5
        if token == "v": dy = 5
        if token == "<": dx = -5
        if token == ">": dx = 5
        pygame.draw.line(screen, Colour.SENSOR, (cx, cy), (cx + dx, cy + dy), 1)

    # Tasks (outline)
    for k, cells in md["task_cells"].items():
        for c, r in cells:
            pygame.draw.rect(screen, col, map_obj.cell_rect(c, r), 1)

    # Discoveries (outline)
    for k, cells in md["discovery_cells"].items():
        for c, r in cells:
            pygame.draw.rect(screen, col, map_obj.cell_rect(c, r), 1)

    # Dynamic walls (! and ?) outlines
    for t, cells in md["dynamic_walls"].items():
        for c, r in cells:
            pygame.draw.rect(screen, col, map_obj.cell_rect(c, r), 1)

    # Anomalies (o/p) outline (optional)
    for c, r, t in md["anomalies"]:
        pygame.draw.rect(screen, col, map_obj.cell_rect(c, r), 1)