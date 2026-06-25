"""
audio_mcq.py
------------
Multiple choice screens where each option is a playable audio clip.

Part 1: Standard MCQ — options only, participant picks the one that sounds
        most like the language they heard.

Part 2: Same MCQ but with a primary audio clip shown at the top of the screen.
        The primary must be played first before the options become available.
"""

import random
from psychopy import visual, event, core, sound

# ---- Layout constants (degrees) ------------------------------------------------------------------------------------------------
_OPTION_START_Y  =  3.5 # 7.0    # y position of the first audio option
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

# Part 2 primary player sits above the MCQ options
_PRIMARY_Y       =  7.0 #  just below the instruction text
_PRIMARY_POS     = (0.0, _PRIMARY_Y)   # centred horizontally (-9.0, _PRIMARY_Y)
_PRIMARY_W       =  3.5
_PRIMARY_H       =  1.4
_PRIMARY_LABEL_X = -5.0    # label to the left of the play button -13.0

_LABELS          = ['A', 'B', 'C', 'D']


# ---- Shared helpers ------------------------------------------------------------------------------------------------------------------------

def _hit(mx, my, cx, cy, w, h):
    """Return True if the mouse click landed inside a rectangle."""
    return abs(mx - cx) <= w / 2 and abs(my - cy) <= h / 2


def _make_player(win, col, label, y, audio_path):
    """
    Build one audio option row — its label, play button, checkbox, and
    playback state — and return everything as a single dict.

    Playback end is detected using a clock rather than PsychoPy's isPlaying
    or isFinished, which behave inconsistently across audio backends.

    Args:
        win:        PsychoPy Window.
        col:        Colors dict from config.
        label:      Letter shown next to this option ('A', 'B', 'C', 'D').
        y:          Vertical position of this row on screen (degrees).
        audio_path: Path to this option's audio file.

    Returns:
        Dict containing all stims and playback state for this option.
    """
    audio = sound.Sound(audio_path)
    return {
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
            win, text="Play",
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
        'audio':      audio,
        'dur':        audio.getDuration(),
        'clock':      core.Clock(),
        'y':          y,
        'is_playing': False,
        'played':     False,
        'checked':    False,
    }


def _make_primary_player(win, col, audio_path):
    """
    Build the primary audio player for part 2 — a single play button at the
    top of the screen with no checkbox. Same clock-based end detection as
    the MCQ options.

    Args:
        win:        PsychoPy Window.
        col:        Colors dict from config.
        audio_path: Path to the primary audio file.

    Returns:
        Dict containing stims and playback state for the primary player.
    """
    audio = sound.Sound(audio_path)
    return {
        'lbl': visual.TextStim(
            win, text="Reference",
            pos=(_PRIMARY_LABEL_X, _PRIMARY_Y), height=1.0, bold=True,
            color=col['text']
        ),
        'play_bg': visual.Rect(
            win, width=_PRIMARY_W, height=_PRIMARY_H,
            pos=_PRIMARY_POS,
            fillColor=col['accent'], lineColor=None
        ),
        'play_lbl': visual.TextStim(
            win, text="Play",
            pos=_PRIMARY_POS, height=0.7, bold=True,
            color='white'
        ),
        'audio':      audio,
        'dur':        audio.getDuration(),
        'clock':      core.Clock(),
        'is_playing': False,
        'played':     False,   # gate — MCQ options locked until this is True
    }


def _build_screen_stims(win, col, trial_num, show_divider=False):
    """
    Build the title, instruction, optional divider, and confirm button
    shared across all options.

    Args:
        win:          PsychoPy Window.
        col:          Colors dict from config.
        trial_num:    Trial number shown in the title.
        show_divider: If True, adds a label separating the primary player
                      from the MCQ options (used in part 2).
    """
    stims = {
        'title': visual.TextStim(
            win, text=f"Trial {trial_num}",
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
    if show_divider:
        stims['divider'] = visual.TextStim(
            win, text="--- Options ---",
            pos=(0, _OPTION_START_Y + 1.5), height=0.7,
            color=col['muted']
        )

    return stims


def _stop_all(players):
    """Stop all currently playing audio in a player list and reset their state."""
    for p in players:
        if p['is_playing']:
            p['audio'].stop()
            p['is_playing']    = False
            p['play_lbl'].text = "Play"


# ---- Part 1 ----------------------------------------------------------------------------------------------------------------------------------------

def run_audio_mcq_part1(win, m, colors, audio_paths, trial_num, correct_index=0):
    """
    Run one part 1 multiple choice trial.

    The audio options are shuffled before display so the correct answer
    doesn't always appear in the same position. We record where the correct
    answer ended up after shuffling so we can compare it to what the
    participant picked.

    The Confirm button only becomes active once all options have been played
    at least once and one checkbox is ticked. Only one audio can play at a
    time — pressing play on one option stops any other that is playing.

    Args:
        win:           PsychoPy Window object.
        m:             PsychoPy Mouse object.
        colors:        Colors dict from config (keys: text, accent, muted, success).
        audio_paths:   List of 2-4 audio file paths. The correct answer is
                       whichever path sits at correct_index before shuffling.
        trial_num:     Trial number shown as the screen title.
        correct_index: Which path in audio_paths is the correct answer
                       (default 0, meaning the first path is always correct).

    Returns:
        Tuple (correct_position, selected, is_correct):
            correct_position -- where the correct answer ended up after shuffling (0 = A, etc.)
            selected         -- which option the participant picked (0 = A, etc.)
            is_correct       -- True if the participant picked the correct answer.
    """
    col = colors

    # Shuffle paths while tracking where the correct answer ends up
    indexed = list(enumerate(audio_paths))
    random.shuffle(indexed)
    original_indices, shuffled_paths = zip(*indexed)
    correct_position = list(original_indices).index(correct_index)

    screen  = _build_screen_stims(win, col, trial_num)
    confirm_y = (_OPTION_START_Y - (len(audio_paths) - 1) * _OPTION_SPACING) - 3.0  # added
    screen['confirm_bg'].pos  = (10.0, confirm_y)  # added
    screen['confirm_lbl'].pos = (10.0, confirm_y) # added                                    
    players = [
        _make_player(win, col, _LABELS[i], _OPTION_START_Y - i * _OPTION_SPACING, path)
        for i, path in enumerate(shuffled_paths)
    ]

    while True:

        # ---- 1. Update playback states ----------------------------------------------------------------------------------
        for p in players:
            if p['is_playing'] and p['clock'].getTime() >= p['dur']:
                p['audio'].stop()
                p['is_playing']    = False
                p['play_lbl'].text = "Play"

        # ---- 2. Update confirm button ------------------------------------------------------------------------------------
        all_played  = all(p['played'] for p in players)
        any_checked = any(p['checked'] for p in players)
        can_confirm = all_played and any_checked
        screen['confirm_bg'].fillColor = col['success'] if can_confirm else col['muted']

        # ---- 3. Draw ----------------------------------------------------------------------------------------------------------------------
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

        # ---- 4. Mouse input --------------------------------------------------------------------------------------------------------
        if m.getLeftButtonPressed():
            mx, my = m.getPos()

            for p in players:
                if _hit(mx, my, _PLAY_X, p['y'], _PLAY_W, _PLAY_H):
                    if p['is_playing']:
                        p['audio'].stop()
                        p['is_playing']    = False
                        p['play_lbl'].text = "Play"
                    else:
                        _stop_all(players)
                        p['audio'].seek(0)
                        p['audio'].play()
                        p['clock'].reset()
                        p['is_playing']    = True
                        p['played']        = True
                        p['play_lbl'].text = "Pause"
                    core.wait(_CLICK_DEBOUNCE)
                    break

                if _hit(mx, my, _CHECK_X, p['y'], _CHECK_SIZE * 2, _CHECK_SIZE * 2):
                    checked_now = not p['checked']
                    for other in players:
                        other['checked'] = False
                    p['checked'] = checked_now
                    core.wait(_CLICK_DEBOUNCE)
                    break

            if can_confirm and _hit(mx, my, 10.0, confirm_y, _CONFIRM_W, _CONFIRM_H):
                _stop_all(players)
                selected   = next(i for i, p in enumerate(players) if p['checked'])
                is_correct = selected == correct_position
                return correct_position, selected, is_correct

        if "escape" in event.getKeys():
            _stop_all(players)
            win.close()
            core.quit()


# ---- Part 2 ----------------------------------------------------------------------------------------------------------------------------------------

def run_audio_mcq_part2(win, m, colors, primary_audio, audio_paths, trial_num, correct_index=0):
    """
    Run one part 2 multiple choice trial.

    Same logic as part 1 but with a primary (reference) audio clip shown at
    the top of the screen. The primary must be played at least once before
    the MCQ options become clickable. After that, all options must be played
    before Confirm activates.

    Args:
        win:           PsychoPy Window object.
        m:             PsychoPy Mouse object.
        colors:        Colors dict from config (keys: text, accent, muted, success).
        primary_audio: Path to the reference audio shown at the top of the screen.
        audio_paths:   List of 2-4 MCQ option audio file paths. The correct answer
                       is whichever path sits at correct_index before shuffling.
        trial_num:     Trial number shown as the screen title.
        correct_index: Which path in audio_paths is the correct answer
                       (default 0, meaning the first path is always correct).

    Returns:
        Tuple (correct_position, selected, is_correct):
            correct_position -- where the correct answer ended up after shuffling (0 = A, etc.)
            selected         -- which option the participant picked (0 = A, etc.)
            is_correct       -- True if the participant picked the correct answer.
    """
    col = colors

    # Shuffle MCQ paths while tracking where the correct answer ends up
    indexed = list(enumerate(audio_paths))
    random.shuffle(indexed)
    original_indices, shuffled_paths = zip(*indexed)
    correct_position = list(original_indices).index(correct_index)

    primary = _make_primary_player(win, col, primary_audio)
    screen  = _build_screen_stims(win, col, trial_num, show_divider=True)
    confirm_y = (_OPTION_START_Y - (len(audio_paths) - 1) * _OPTION_SPACING) - 3.0  # added
    screen['confirm_bg'].pos  = (10.0, confirm_y) # added
    screen['confirm_lbl'].pos = (10.0, confirm_y) # added

    players = [
        _make_player(win, col, _LABELS[i], _OPTION_START_Y - i * _OPTION_SPACING, path)
        for i, path in enumerate(shuffled_paths)
    ]

    while True:

        # ---- 1. Update primary playback state --------------------------------------------------------------------
        if primary['is_playing'] and primary['clock'].getTime() >= primary['dur']:
            primary['audio'].stop()
            primary['is_playing']    = False
            primary['play_lbl'].text = "Play"

        # ---- 2. Update MCQ playback states --------------------------------------------------------------------------
        options_unlocked = primary['played']
        for p in players:
            if p['is_playing'] and p['clock'].getTime() >= p['dur']:
                p['audio'].stop()
                p['is_playing']    = False
                p['play_lbl'].text = "Play"

        # ---- 3. Update button states --------------------------------------------------------------------------------------
        all_played  = options_unlocked and all(p['played'] for p in players)
        any_checked = any(p['checked'] for p in players)
        can_confirm = all_played and any_checked

        # Option play buttons are grayed out until primary has been played
        for p in players:
            p['play_bg'].fillColor = col['accent'] if options_unlocked else col['muted']
        screen['confirm_bg'].fillColor = col['success'] if can_confirm else col['muted']

        # ---- 4. Draw ----------------------------------------------------------------------------------------------------------------------
        primary['lbl'].draw()
        primary['play_bg'].draw()
        primary['play_lbl'].draw()

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

        # ---- 5. Mouse input --------------------------------------------------------------------------------------------------------
        if m.getLeftButtonPressed():
            mx, my = m.getPos()

            # Primary play button — always clickable
            if _hit(mx, my, *_PRIMARY_POS, _PRIMARY_W, _PRIMARY_H):
                if primary['is_playing']:
                    primary['audio'].stop()
                    primary['is_playing']    = False
                    primary['play_lbl'].text = "Play"
                else:
                    _stop_all(players)
                    primary['audio'].stop()
                    primary['audio'].seek(0)
                    primary['audio'].play()
                    primary['clock'].reset()
                    primary['is_playing']    = True
                    primary['played']        = True
                    primary['play_lbl'].text = "Pause"
                core.wait(_CLICK_DEBOUNCE)

            # MCQ options — only clickable after primary has been played
            elif options_unlocked:
                for p in players:
                    if _hit(mx, my, _PLAY_X, p['y'], _PLAY_W, _PLAY_H):
                        if p['is_playing']:
                            p['audio'].stop()
                            p['is_playing']    = False
                            p['play_lbl'].text = "Play"
                        else:
                            _stop_all(players)
                            # Also stop primary if it somehow started again
                            if primary['is_playing']:
                                primary['audio'].stop()
                                primary['is_playing']    = False
                                primary['play_lbl'].text = "Play"
                            p['audio'].seek(0)
                            p['audio'].play()
                            p['clock'].reset()
                            p['is_playing']    = True
                            p['played']        = True
                            p['play_lbl'].text = "Pause"
                        core.wait(_CLICK_DEBOUNCE)
                        break

                    if _hit(mx, my, _CHECK_X, p['y'], _CHECK_SIZE * 2, _CHECK_SIZE * 2):
                        checked_now = not p['checked']
                        for other in players:
                            other['checked'] = False
                        p['checked'] = checked_now
                        core.wait(_CLICK_DEBOUNCE)
                        break

                if can_confirm and _hit(mx, my, 10.0, confirm_y, _CONFIRM_W, _CONFIRM_H):
                    _stop_all(players)
                    primary['audio'].stop()
                    selected   = next(i for i, p in enumerate(players) if p['checked'])
                    is_correct = selected == correct_position
                    return correct_position, selected, is_correct

        if "escape" in event.getKeys():
            _stop_all(players)
            primary['audio'].stop()
            win.close()
            core.quit()