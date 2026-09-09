from psychopy import visual, event

from screens.utils.quit_confirmation import QuitConfirmation


def run_fixation(win, text_color):
    banner = visual.TextStim(
        win, text="Press SPACE to proceed to the next part",
        pos=(0, 12), height=2,
        color=text_color
    )
    fixation = visual.TextStim(
        win, text="+",
        pos=(0, 0), height=0.5,
        wrapWidth=50,
        color=text_color
    )

    quit_confirmation = QuitConfirmation(win)

    while True:
        banner.draw()
        fixation.draw()
        keys = event.getKeys()
        input_blocked = quit_confirmation.update(keys)
        quit_confirmation.draw()
        win.flip()
        if input_blocked:
            continue
        if "space" in keys:
            break
