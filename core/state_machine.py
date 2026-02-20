class StateMachine:
    """controls mode switching: BOOT, PLAY, TERMINAL"""

    def __init__(self, starting_state):
        self.game = None
        self.state = starting_state
        self._bind(self.state)

    def _bind(self, state):
        state.machine = self
        state.game = self.game

    def set_game(self, game):
        self.game = game
        self._bind(self.state)

    def change_state(self, new_state):
        self.state = new_state
        self._bind(self.state)

    def handle_event(self, event):
        handler = getattr(self.state, "handle_event", None)
        if handler:
            handler(event)

    def update(self, dt):
        self.state.update(dt)

    def render(self, screen):
        self.state.render(screen)


