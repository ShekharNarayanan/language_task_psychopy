"""Shared, nonblocking confirmation overlay for leaving an experiment."""

import math

from psychopy import core, visual


class QuitConfirmation:
    """Process keys before responses; draw over the current screen before flip.

    ``update`` returns True while input belongs to the overlay, including the
    frame that dismisses it. Playback and its clocks can continue normally.
    """

    def __init__(self, win, on_quit=None):
        self.win = win
        self.on_quit = on_quit
        self.active = False
        self.clock = core.Clock()
        self.shade = visual.Rect(
            win, units='norm', width=2, height=2,
            fillColor='black', lineColor=None, opacity=0.65,
        )
        self.panel = visual.Rect(
            win, units='norm', width=1.7, height=0.8,
            fillColor='black', lineColor='white',
        )
        self.message = visual.TextStim(
            win, units='norm', text='', height=0.065,
            color='white', wrapWidth=1.5,
        )

    def update(self, keys):
        """Require a separate Y after Escape; N or five seconds cancels."""
        if not self.active:
            if 'escape' not in keys:
                return False
            self.clock.reset()
            self.active = True
            # Ignore other keys from the opening frame: show the prompt first.
            return True

        if self.clock.getTime() >= 5 or 'n' in keys:
            self.active = False
        elif 'y' in keys:
            print(
                "Experiment ended with ESC and confirmation (Y).",
                flush=True,
            )
            try:
                if self.on_quit is not None:
                    self.on_quit()
            finally:
                self.win.close()
                core.quit()
        return True

    def draw(self):
        if not self.active:
            return
        remaining = max(0, math.ceil(5 - self.clock.getTime()))
        self.message.text = (
            "Experiment stoppen?\n\n"
            "Druk op Y om te bevestigen.\n"
            "Druk op N om verder te gaan.\n\n"
            f"Automatisch verder over {remaining} s."
        )
        self.shade.draw()
        self.panel.draw()
        self.message.draw()
