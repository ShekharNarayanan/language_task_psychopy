"""
instruction.py
--------------
Generic instruction screen that displays a block of text and advances on SPACE.
"""

from psychopy import visual, event

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

    while True:
        stim.draw()
        win.flip()
        if 'space' in event.getKeys():
            break