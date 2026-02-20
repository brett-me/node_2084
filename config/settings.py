class GamePlayConfig:
    """central behavioural tuning"""

    SUSPICION_GAIN_RATE = 8  # per second while detected
    SENSOR_DETECTION = 100  # lower equals faster detection, linked to infrared alpha

    MAX_INFRARED_ALPHA = 200  # infrared brightness

    # bright green glitch intensity
    PHOS_MIN_ALPHA = 180
    PHOS_MAX_ALPHA = 255


class TimingConfig:
    """central timing controls"""

    # intensity of bright green glitch
    PHOS_FADE_TIME = 0.6

    # bright green glitch frequency
    PHOS_MIN_HOLD = 0.8
    PHOS_MAX_HOLD = 6

    # boot sequence pacing
    BOOT_CURSOR_BLINK = 0.5
    BOOT_CURSOR_ONLY_1 = 2.5
    BOOT_CURSOR_ONLY_2 = 1.5
    BOOT_LINE_GAP = 1
    BOOT_HOLD_AFTER_BLOCK = 3

    # player spawn
    PLAYER_SPAWN_DELAY = 0.5  # seconds before player exists
    PLAYER_FADE_DURATION = 1.0  # seconds to fade in fully

    # sensor timing
    SENSOR_START_DELAY = 3
    SENSOR_ON_TIME = 3
    SENSOR_OFF_TIME = 3

    # movement message
    MSG_DELAY = 0.1
    MSG_DURATION = 2

    # truth terminal
    TERMINAL_LINE_DELAY = 1
    TERMINAL_BLOCK_PAUSE = 0.35
    POST_ATTACH_PAUSE = 0.8
