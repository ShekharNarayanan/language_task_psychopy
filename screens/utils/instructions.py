"""
instruction.py
--------------
Generic instruction screen that displays a block of text and advances on SPACE.
"""

from psychopy import visual, event

from screens.utils.quit_confirmation import QuitConfirmation

def show_instruction(win, text, text_color):
    """
    Display an instruction screen and wait for SPACE to continue.

    Args:
        win:        PsychoPy Window object.
        text:       Instruction string to display.
        text_color: Color of the text (string or RGB).
    """
    stim = visual.TextStim(
        win, text=text,
        pos=(0, 0), height=0.8,
        color=text_color,
        wrapWidth=35   # wraps long text within the screen
    )

    quit_confirmation = QuitConfirmation(win)

    while True:
        stim.draw()
        keys = event.getKeys()
        input_blocked = quit_confirmation.update(keys)
        quit_confirmation.draw()
        win.flip()
        if input_blocked:
            continue
        if 'space' in keys:
            break
