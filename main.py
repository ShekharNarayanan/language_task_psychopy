from psychopy import prefs
prefs.hardware['audioLib'] = ['sounddevice', 'pygame']
from psychopy import visual, event, core, monitors, sound

if __name__ == "__main__":
    # Define monitor specifications
    monitorname = 'my_lab_monitor'
    width_cm = 53.1
    distance_cm = 60.0
    width_px = 1920
    height_px = 1080

    # Create Monitor Object
    mon = monitors.Monitor(monitorname, width=width_cm, distance=distance_cm)
    mon.setSizePix((width_px, height_px))

    win = visual.Window(
        size=(1080, 720),
        checkTiming=False,
        infoMsg="",
        monitor=mon,
        units='deg',
        fullscr=True
    )

    # --- Screen 1: Welcome ---
    welcome_text = visual.TextStim(win, text="Press SPACE to start the experiment", pos=(0, 0), height=1.5, color='black')

    while True:
        welcome_text.draw()
        win.flip()
        if "space" in event.getKeys():
            break

    # --- Screen 2: Audio ---
    audio_stim = sound.Sound('stimuli/audio1.mp3')

    instruction = visual.TextStim(win, text="Press P to play the audio\nPress R to replay\nPress SPACE to continue", pos=(0, 3), height=1, color='black')
    status_text = visual.TextStim(win, text="", pos=(0, -3), height=0.9, color='black')

    audio_played = False

    while True:
        instruction.draw()
        status_text.draw()
        win.flip()

        keys = event.getKeys()

        if "p" in keys or "r" in keys:
            audio_stim.stop()
            audio_stim.play()
            audio_played = True
            status_text.text = "Playing..." if "p" in keys else "Replaying..."

        if "space" in keys and audio_played:
            break
        elif "space" in keys and not audio_played:
            status_text.text = "Please listen to the audio first (press P)"

    audio_stim.stop()

    # --- Screen 3: Fixation cross ---
    banner = visual.TextStim(win, text="Press SPACE to exit", pos=(0, 12), height=2, color='black')
    fixation = visual.TextStim(win, text="+", color="black", height=1)

    while True:
        banner.draw()
        fixation.draw()
        win.flip()
        if "space" in event.getKeys():
            break

    win.close()
    core.quit()