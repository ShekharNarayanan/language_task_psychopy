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
from screens.audio_mcq    import run_audio_mcq
from screens.fixation     import run_fixation

# load all config params

# monitor related specs
monitor_name    = cfg['monitor']['name']
width_cm        = cfg['monitor']['width_cm']
distance_cm     = cfg['monitor']['distance_cm']
width_px        = cfg['monitor']['width_px']
height_px       = cfg['monitor']['height_px']

# colors for visual stimuli
all_colors      = cfg['colors']
text_color      = cfg['colors']['text']
screen_bg_color = cfg['colors']['background']

# window units and params
window_size     = cfg['window']['size']
window_units    = cfg['window']['units']
full_scr        = cfg['window']['fullscreen']

# texts for different screens
welcome_text    = cfg['stimuli']['welcome_text']

# set 1 audio files
primary_audio       = cfg['stimuli']['set_1']['primary_audio']
set_1_trials        = cfg['stimuli']['set_1']['n_trials']

# create monitor object
mon = monitors.Monitor(
name=monitor_name,
width=width_cm,
distance=distance_cm
)
# set size of monitor in pixels
mon.setSizePix((width_px, height_px))

# create window object (dont use size until final monitor is decided)
win = visual.Window(
    checkTiming=False,
    infoMsg='',
    monitor=mon,
    units=window_units,
    fullscr=full_scr,
    color=screen_bg_color
)

# create mouse object
m = mouse.Mouse(win=win)

# run process for set 1
run_welcome(win, welcome_text=welcome_text, text_color=text_color)
run_audio_player(win, m, colors=all_colors, audio_path=primary_audio)

for i_trial in range(set_1_trials):
    audios_i_trial = cfg['stimuli']['set_1'][f'trial_{i_trial+1}']['audio_paths']
    run_audio_mcq(win,m,all_colors,audio_paths=audios_i_trial)
# run_fixation(win, text_color=text_color)

win.close()
core.quit()