from psychopy import visual, event


def run_welcome(win, cfg):
    text = visual.TextStim(
        win,
        text="Press SPACE to start the experiment",
        pos=(0, 0),
        height=1.5,
        color=cfg['colors']['text']
    )

    while True:
        text.draw()
        win.flip()
        if "space" in event.getKeys():
            break