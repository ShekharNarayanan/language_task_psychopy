from psychopy import visual, event


def run_fixation(win, text_color):
    banner = visual.TextStim(
        win, text="Press SPACE to exit",
        pos=(0, 12), height=2,
        color=text_color
    )
    fixation = visual.TextStim(
        win, text="+",
        pos=(0, 0), height=1,
        color=text_color
    )

    while True:
        banner.draw()
        fixation.draw()
        win.flip()
        if "space" in event.getKeys():
            break