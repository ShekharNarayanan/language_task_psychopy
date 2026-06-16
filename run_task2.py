import yaml
import random
import argparse
from pathlib import Path
import pandas as pd

# ── Load system config ────────────────────────────────────────────────────────
root         = Path(__file__).parent
sys_cfg_path = root / "system_config.yaml"
with open(sys_cfg_path) as f:
    sys_cfg = yaml.safe_load(f)

# ── Audio backend must be set before other psychopy imports ───────────────────
from psychopy import prefs
prefs.hardware['audioLib'] = sys_cfg['audio']['backends']

from psychopy import monitors, visual, core
from psychopy.hardware import mouse

from screens.instructions  import show_instruction
from screens.rating        import run_rating
from screens.task2_part1   import run_task2_part1
from screens.task2_part2   import run_task2_part2


def _get_part1_trials(cfg_set):
    """
    Collect all congruent and incongruent trials from the config into a
    flat list, tag each with its condition, then shuffle randomly.

    Returns a list of dicts ready to iterate over in the trial loop.
    """
    trials = []

    for trial_key, trial_data in cfg_set['part_1']['congruent'].items():
        if not trial_key.startswith('trial_'):
            continue
        trials.append({
            'condition':  'congruent',
            'sentence_a': trial_data['sentence_a'],
            'sentence_b': trial_data['sentence_b'],
        })

    for trial_key, trial_data in cfg_set['part_1']['incongruent'].items():
        if not trial_key.startswith('trial_'):
            continue
        trials.append({
            'condition':  'incongruent',
            'sentence_a': trial_data['sentence_a'],
            'sentence_b': trial_data['sentence_b'],
        })

    random.shuffle(trials)
    return trials


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--p_id',     required=True, help='Participant ID')
    parser.add_argument('--set_num',  required=True, help='Stimulus set number')
    parser.add_argument('--test_run', required=True, help='True for one trial per part')
    args = parser.parse_args()

    participant_id = args.p_id
    set_num        = args.set_num
    test_run_flag  = args.test_run.lower() == 'true'

    # ── Load task 2 config ────────────────────────────────────────────────────
    cfg_path = root / f'config_task2_set{set_num}.yaml'
    with open(cfg_path) as f:
        cfg_set = yaml.safe_load(f)

    # ── Monitor specs ─────────────────────────────────────────────────────────
    monitor_name    = sys_cfg['monitor']['name']
    width_cm        = sys_cfg['monitor']['width_cm']
    distance_cm     = sys_cfg['monitor']['distance_cm']
    width_px        = sys_cfg['monitor']['width_px']
    height_px       = sys_cfg['monitor']['height_px']

    # ── Colors ────────────────────────────────────────────────────────────────
    all_colors      = sys_cfg['colors']
    text_color      = sys_cfg['colors']['text']
    screen_bg_color = sys_cfg['colors']['background']

    # ── Window params ─────────────────────────────────────────────────────────
    window_units    = sys_cfg['window']['units']
    full_scr        = sys_cfg['window']['fullscreen']

    # ── Instruction texts ─────────────────────────────────────────────────────
    welcome_text       = cfg_set['part_1']['instruction']
    part2_msg          = cfg_set['part_2']['instruction']
    rating_instruction = sys_cfg['rating_instruction']
    exit_instruction   = sys_cfg['task_2']['exit_instruction']

    # ── Trial counts ──────────────────────────────────────────────────────────
    if test_run_flag:
        total_trials_part_1 = sys_cfg['task_2']['test_trials_part_1']
        total_trials_part_2 = sys_cfg['task_2']['test_trials_part_2']
    else:
        total_trials_part_1 = cfg_set['part_1']['congruent']['n_trials'] + cfg_set['part_1']['incongruent']['n_trials']
        total_trials_part_2 = cfg_set['part_2']['n_trials']

    # ── Create monitor ────────────────────────────────────────────────────────
    mon = monitors.Monitor(
        name=monitor_name,
        width=width_cm,
        distance=distance_cm
    )
    mon.setSizePix((width_px, height_px))

    # ── Create window ─────────────────────────────────────────────────────────
    win = visual.Window(
        checkTiming=False,
        infoMsg='',
        monitor=mon,
        units=window_units,
        fullscr=full_scr,
        color=screen_bg_color
    )

    # ── Create mouse ──────────────────────────────────────────────────────────
    m = mouse.Mouse(win=win)

    participant_results = []

    # ── Part 1 ────────────────────────────────────────────────────────────────
    show_instruction(win=win, text=welcome_text, text_color=text_color)

    part1_trials = _get_part1_trials(cfg_set)[:total_trials_part_1]

    for i, trial in enumerate(part1_trials, start=1):
        chosen_answer = run_task2_part1(
            win=win, m=m, colors=all_colors,
            trial_num=i,
            sentence_a=trial['sentence_a'],
            sentence_b=trial['sentence_b']
        )
        # confidence_rating = run_rating(
        #     win, text_color=text_color,
        #     rating_text=rating_instruction
        # )

        participant_results.append({
            'participant_id': participant_id,
            'part':           1,
            'trial_num':      i,
            'condition':      trial['condition'],
            'sentence_a':     trial['sentence_a'],
            'sentence_b':     trial['sentence_b'],
            'chosen_answer':  chosen_answer,
            # 'confidence':     confidence_rating,
        })

    trial_offset = len(part1_trials)

    # ── Part 2 ────────────────────────────────────────────────────────────────
    show_instruction(win=win, text=part2_msg, text_color=text_color)

    for j in range(1, total_trials_part_2 + 1):
        trial_num    = j + trial_offset
        trial_cfg    = cfg_set['part_2'][f'trial_{j}']

        chosen_answer, is_correct = run_task2_part2(
            win=win, m=m, colors=all_colors,
            trial_num=trial_num,
            audio_word=trial_cfg['audio_word'],
            audio_sentence_a=trial_cfg['sentence_a'],
            audio_sentence_b=trial_cfg['sentence_b'],
            correct_answer=trial_cfg['correct_answer'],
            incorrect_answer1=trial_cfg['incorrect_answer1'],
            incorrect_answer2=trial_cfg['incorrect_answer2'],
        )
        confidence_rating = run_rating(
            win, text_color=text_color,
            rating_text=rating_instruction
        )

        participant_results.append({
            'participant_id': participant_id,
            'part':           2,
            'trial_num':      trial_num,
            'chosen_answer':  chosen_answer,
            'is_correct':     is_correct,
            'confidence':     confidence_rating,
        })

    # ── Save results ──────────────────────────────────────────────────────────
    participant_df = pd.DataFrame(participant_results)
    show_instruction(win=win, text=exit_instruction, text_color=text_color)

    suffix     = '_test' if test_run_flag else ''
    output_path = root / 'output' / f'participant_{participant_id}_task2_set{set_num}{suffix}.csv'
    participant_df.to_csv(output_path, index=False)

    core.quit()