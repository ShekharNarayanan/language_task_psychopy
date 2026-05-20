from psychopy import visual, event, core, monitors


if __name__ == "__main__":
    # from psychopy import visual, monitors

    # Define monitor specifications
    monitorname = 'my_lab_monitor'
    width_cm = 53.1       # Physical width of the screen
    distance_cm = 60.0    # Distance from participant to screen
    width_px = 1920       # Horizontal pixels
    height_px = 1080      # Vertical pixels

    # Create Monitor Object
    mon = monitors.Monitor(monitorname, width=width_cm, distance=distance_cm)
    mon.setSizePix((width_px, height_px))

    win = visual.Window(
    size=(1080, 720), 
    checkTiming=False, 
    infoMsg="", 
    monitor=mon,
    units='deg',  # Units now scaled properly using your monitor specs
    fullscr=True

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
