from psychopy import visual, event


def run_welcome(win, text_color, welcome_text):
    text = visual.TextStim(
        win,
        text=f"{welcome_text}",
        pos=(0, 0),
        height=1.5,
        color=text_color
    )

    while True:
        text.draw()
        win.flip()
        if "space" in event.getKeys():
            break