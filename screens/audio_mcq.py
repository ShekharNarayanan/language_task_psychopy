"""
audio_mcq.py
------------
Multiple choice screen where each option is a playable audio clip.
Participant must play all options at least once, then select one via
checkbox and click Confirm to advance. Returns the selected index and
whether it was correct.
"""

import random
from psychopy import visual, event, core, sound

# ── Layout constants (degrees) ────────────────────────────────────────────────
_OPTION_START_Y  =  7.0    # y position of the first audio option
_OPTION_SPACING  =  4.5    # vertical distance between options
_LABEL_X         = -13.0   # x position of the A/B/C label
_PLAY_X          = -9.0    # x centre of the play button
_PLAY_W          =  3.5
_PLAY_H          =  1.4
_CHECK_X         =  12.0   # x centre of the checkbox
_CHECK_SIZE      =  1.0    # width and height of checkbox square
_CONFIRM_POS     = (10.0, -10.0)
_CONFIRM_W       =  5.0
_CONFIRM_H       =  1.8
_CLICK_DEBOUNCE  =  0.2
_LABELS          = ['A', 'B', 'C', 'D']


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hit(mx, my, cx, cy, w, h):
    """Return True if (mx, my) is inside an axis-aligned rectangle."""
    return abs(mx - cx) <= w / 2 and abs(my - cy) <= h / 2


def _make_player(win, col, label, y, audio_path):
    """
    Build stims and state dict for a single audio option.

    Uses a clock to detect natural end of playback, consistent with the
    primary audio player, avoiding unreliable backend-specific attributes
    like isPlaying or isFinished.

    Args:
        win:        PsychoPy Window.
        col:        Colors dict from config.
        label:      Option label string ('A', 'B', 'C', 'D').
        y:          Vertical centre position for this option (degrees).
        audio_path: Path to the audio file.

    Returns:
        A dict with all stims and playback state for this option.
    """
    audio = sound.Sound(audio_path)
    return {
        # ── Stims ─────────────────────────────────────────────────────────────
        'lbl': visual.TextStim(
            win, text=label,
            pos=(_LABEL_X, y), height=1.0, bold=True,
            color=col['text']
        ),
        'play_bg': visual.Rect(
            win, width=_PLAY_W, height=_PLAY_H,
            pos=(_PLAY_X, y),
            fillColor=col['accent'], lineColor=None
        ),
        'play_lbl': visual.TextStim(
            win, text="▶  Play",
            pos=(_PLAY_X, y), height=0.7, bold=True,
            color='white'
        ),
        'check_bg': visual.Rect(
            win, width=_CHECK_SIZE, height=_CHECK_SIZE,
            pos=(_CHECK_X, y),
            fillColor='white', lineColor=col['text'], lineWidth=2
        ),
        'check_mark': visual.TextStim(
            win, text='',
            pos=(_CHECK_X, y), height=0.8, bold=True,
            color=col['accent']
        ),
        # ── Playback state ────────────────────────────────────────────────────
        'audio':      audio,
        'dur':        audio.getDuration(),   # used to detect natural end
        'clock':      core.Clock(),          # measures time since play was pressed
        'y':          y,
        'is_playing': False,
        'played':     False,   # True once played at least once
        'checked':    False,   # True if this option is selected
    }


def _build_screen_stims(win, col,trial_num):
    """Build stims that belong to the screen rather than individual players."""
    return {
        'title': visual.TextStim(
            win, text=f" Trial num: {trial_num}",
            pos=(0, 10.5), height=1.1, bold=True,
            color=col['text']
        ),
        'instruction': visual.TextStim(
            win, text="Choose the correct audio file",
            pos=(0, 9.0), height=0.7,
            color=col['muted']
        ),
        'confirm_bg': visual.Rect(
            win, width=_CONFIRM_W, height=_CONFIRM_H,
            pos=_CONFIRM_POS,
            fillColor=col['muted'], lineColor=None
        ),
        'confirm_lbl': visual.TextStim(
            win, text="Confirm",
            pos=_CONFIRM_POS, height=0.8, bold=True,
            color='white'
        ),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def run_audio_mcq(win, m, colors, audio_paths,trial_num, correct_index=0):
    """
    Run the audio multiple choice screen.

    Audio paths are shuffled on each call so the correct answer does not
    always appear in the same position. The function tracks where the correct
    answer lands after shuffling and compares it to the participant's choice.

    Each option has a play button and a checkbox. The confirm button activates
    only when all options have been played at least once and exactly one
    checkbox is ticked. Checking a new option unchecks the previous one.
    Only one audio plays at a time — starting a new one stops the current.

    Args:
        win:           PsychoPy Window object.
        m:             PsychoPy Mouse object.
        colors:        Colors dict from config (keys: text, accent, muted, success).
        audio_paths:   List of 2–4 audio file paths, one per option. The correct
                       answer is identified by correct_index into this list before
                       shuffling.
        correct_index: Index into audio_paths pointing to the correct answer
                       (default 0, i.e. the first path is always correct).

    Returns:
        Tuple (correct_position, selected_index, is_correct) where selected_index is the position
        of the chosen option in the shuffled display order (0 = A, 1 = B, etc.)
        and is_correct is True if the participant chose the correct answer.
    """
    col = colors

    # Shuffle paths while tracking where the correct answer ends up
    indexed = list(enumerate(audio_paths))
    random.shuffle(indexed)
    original_indices, shuffled_paths = zip(*indexed)
    correct_position = list(original_indices).index(correct_index)

    screen  = _build_screen_stims(win, col, trial_num)
    players = [
        _make_player(win, col, _LABELS[i], _OPTION_START_Y - i * _OPTION_SPACING, path)
        for i, path in enumerate(shuffled_paths)
    ]

    while True:

        # ── 1. Update each player's playback state ────────────────────────────
        for p in players:
            if p['is_playing'] and p['clock'].getTime() >= p['dur']:
                # Audio finished naturally — reset to stopped state
                p['audio'].stop()
                p['is_playing']    = False
                p['play_lbl'].text = "▶  Play"

        # ── 2. Update confirm button state ────────────────────────────────────
        all_played  = all(p['played'] for p in players)
        any_checked = any(p['checked'] for p in players)
        can_confirm = all_played and any_checked
        screen['confirm_bg'].fillColor = col['success'] if can_confirm else col['muted']

        # ── 3. Draw ───────────────────────────────────────────────────────────
        for stim in screen.values():
            stim.draw()

        for p in players:
            p['check_mark'].text = 'X' if p['checked'] else ''
            p['lbl'].draw()
            p['play_bg'].draw()
            p['play_lbl'].draw()
            p['check_bg'].draw()
            p['check_mark'].draw()

        win.flip()

        # ── 4. Mouse input ────────────────────────────────────────────────────
        if m.getLeftButtonPressed():
            mx, my = m.getPos()

            for p in players:

                if _hit(mx, my, _PLAY_X, p['y'], _PLAY_W, _PLAY_H):
                    # Toggle play / pause; stop any other currently playing option
                    if p['is_playing']:
                        p['audio'].stop()
                        p['is_playing']    = False
                        p['play_lbl'].text = "▶  Play"
                    else:
                        for other in players:
                            if other['is_playing']:
                                other['audio'].stop()
                                other['is_playing']    = False
                                other['play_lbl'].text = "▶  Play"
                        p['audio'].stop()
                        p['audio'].seek(0)
                        p['audio'].play()
                        p['clock'].reset()    # clock now measures time since play
                        p['is_playing']    = True
                        p['played']        = True
                        p['play_lbl'].text = "⏸  Pause"
                    core.wait(_CLICK_DEBOUNCE)
                    break

                if _hit(mx, my, _CHECK_X, p['y'], _CHECK_SIZE * 2, _CHECK_SIZE * 2):
                    # Single select — uncheck all others, toggle this one
                    checked_now = not p['checked']
                    for other in players:
                        other['checked'] = False
                    p['checked'] = checked_now
                    core.wait(_CLICK_DEBOUNCE)
                    break

            # Confirm button — only fires when gate conditions are met
            if can_confirm and _hit(mx, my, *_CONFIRM_POS, _CONFIRM_W, _CONFIRM_H):
                for p in players:
                    p['audio'].stop()
                selected = next(i for i, p in enumerate(players) if p['checked'])
                is_correct = selected == correct_position
                return correct_position, selected, is_correct

        if "escape" in event.getKeys():
            for p in players:
                p['audio'].stop()
            win.close()
            core.quit()