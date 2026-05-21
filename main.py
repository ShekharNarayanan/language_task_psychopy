import yaml
from pathlib import Path

# ── Load config ───────────────────────────────────────────────────────────────
cfg_path = Path(__file__).parent / "config.yaml"
with open(cfg_path) as f:   
    cfg = yaml.safe_load(f)

cfg_path = Path(__file__).parent / "config.yaml"


# ── Audio backend must be set before other psychopy imports ───────────────────
from psychopy import prefs
prefs.hardware['audioLib'] = cfg['audio']['backends']

from psychopy import monitors, visual, core
from psychopy.hardware import mouse

from screens.welcome      import run_welcome
from screens.audio_player import run_audio_player
from screens.fixation     import run_fixation


mon = monitors.Monitor(
cfg['monitor']['name'],
width=cfg['monitor']['width_cm'],
distance=cfg['monitor']['distance_cm']
)
mon.setSizePix((cfg['monitor']['width_px'], cfg['monitor']['height_px']))

win = visual.Window(
    size=cfg['window']['size'],
    checkTiming=False,
    infoMsg='',
    monitor=mon,
    units=cfg['window']['units'],
    fullscr=cfg['window']['fullscreen'],
    color=cfg['colors']['background']
)

m = mouse.Mouse(win=win)



run_welcome(win, cfg)
run_audio_player(win, m, cfg)
run_fixation(win, cfg)

win.close()
core.quit()