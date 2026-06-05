import yaml
import argparse
from pathlib import Path
import pandas as pd

# -- Load config ------------------------------------------
root         = Path(__file__).parent
sys_cfg_path = root / "system_config.yaml"
with open(sys_cfg_path) as f:   
    sys_cfg = yaml.safe_load(f)



# -- Audio backend must be set before other psychopy imports ------------─
from psychopy import prefs
prefs.hardware['audioLib'] = sys_cfg['audio']['backends']

from psychopy import monitors, visual, core, gui
from psychopy.hardware import mouse


from screens.audio_player import run_audio_player
from screens.audio_mcq    import run_audio_mcq_part1, run_audio_mcq_part2
from screens.instructions  import show_instruction
# from screens.fixation     import run_fixation

if  __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--p_id', required=True, help='Participant ID')
    parser.add_argument('--set_num',required=True)
    args = parser.parse_args()

    # get pid and set_num
    participant_id = args.p_id
    set_num        = args.set_num

    # load config file for chosen set
    cfg_set_path = root / f'config_set{set_num}.yaml'
    with open (cfg_set_path) as f:
        cfg_set = yaml.safe_load(f)

    # load all config params

    # monitor related specs from system config
    monitor_name    = sys_cfg['monitor']['name']
    width_cm        = sys_cfg['monitor']['width_cm']
    distance_cm     = sys_cfg['monitor']['distance_cm']
    width_px        = sys_cfg['monitor']['width_px']
    height_px       = sys_cfg['monitor']['height_px']

    # colors for visual stimuli
    all_colors      = sys_cfg['colors']
    text_color      = sys_cfg['colors']['text']
    screen_bg_color = sys_cfg['colors']['background']

    # window units and params
    window_size     = sys_cfg['window']['size']
    window_units    = sys_cfg['window']['units']
    full_scr        = sys_cfg['window']['fullscreen']

    # texts for different screens
    welcome_text   = cfg_set['welcome_text']
    testing_text   = cfg_set['test_text']

    # get info for part 1
    primary_audio_part_1       = cfg_set['part_1']['primary_audio']
    total_trials_part_1        = cfg_set['part_1']['n_trials']

    # get info for part 2
    total_trials_part_2        = 1 #cfg_set['part_2']['n_trials']
    part2_msg                  = cfg_set['part_2']['part_2_msg']


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

    # define participant params
    participant_results = []


    # run process for part 1
    show_instruction(win=win, text=welcome_text, text_color=text_color)
    run_audio_player(win=win, m=m, colors=all_colors, audio_path=primary_audio_part_1)
    show_instruction(win=win, text=testing_text, text_color=text_color)

    # loop all trials for part 1
    for i in range(1,total_trials_part_1+1):

        audios_i_trial = cfg_set['part_1'][f'trial_{i}']['audio_paths']
        correct, selected, is_correct = run_audio_mcq_part1(win,m,all_colors,audio_paths=audios_i_trial, trial_num=i)
        
        # save participant info
        participant_results.append({
        'participant_id'  :  participant_id,
        'part'            :  1,
        'trial_num'       :  i + 1,
        'correct_option'  :  correct,
        'selected_option' :  selected,
        'is_correct':        is_correct,        
        })

    trial_offset = total_trials_part_1 # remember the trial at which part 1 ended

    # show transition screen to part 2
    show_instruction(win=win, text=part2_msg, text_color=text_color)

    for j in range(1,total_trials_part_2+1):
        trial_num       = j + trial_offset # include offset, use this number to display on screen and in the participant data

        audios_j_trial  = cfg_set['part_2'][f'trial_{j}']['audio_paths']
        primary_audio   = audios_j_trial[0]
        options         = audios_j_trial[1:]

        correct, selected, is_correct = run_audio_mcq_part2(win=win,m=m,colors=all_colors,primary_audio=primary_audio,audio_paths=options,trial_num=trial_num)

        participant_results.append({
        'participant_id'  :  participant_id,
        'part'            :  2,
        'trial_num'       :  trial_num,
        'correct_option'  :  correct,
        'selected_option' :  selected,
        'is_correct':        is_correct,        
        })



    # run_fixation(win, text_color=text_color)
    participant_df = pd.DataFrame(participant_results)
    win.close()
    print("participant details")
    print(participant_df.head())
    core.quit()
