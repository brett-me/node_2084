class Colour:
    """central colour palette"""

    BLACK = (0, 0, 0)
    BACKGROUND = (0, 10, 0)
    DIM_GREEN = (0, 25, 5)
    BRIGHT_GREEN = (0, 255, 70)
    PLAYER_CORE = (220, 255, 220)  # almost pure white
    SENSOR = (255, 140, 0)

    @staticmethod
    def phosphor_colour(base_rgb, alpha_value):
        # alpha_value is 200..255; convert to 0.78..1.0 brightness factor
        factor = alpha_value / 255.0
        r, g, b = base_rgb
        return (int(r * factor), int(g * factor), int(b * factor))
