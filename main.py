from psychopy import visual, event, core, monitors


if __name__ == "__main__":
    mon = monitors.Monitor(name="my_monitor")
    mon.setSizePix((1920, 1080))
    mon.setWidth(52)
    mon.setDistance(60)

    win = visual.Window(
        size=(1920, 1080),
        monitor=mon,
        color="gray",
        fullscr=False,
        units="deg",
        screen=0,
        waitBlanking=True,  # syncs to 60hz refresh
    )
    banner = visual.TextStim(win,text="Press space to exit",pos=(0, 8),height=2,color='black')
    fixation = visual.TextStim(win, text="+", color="black", height=1)

    while True:
        banner.draw()
        fixation.draw()
        win.flip()

        if "space" in event.getKeys():
            break

    win.close()
    core.quit()
