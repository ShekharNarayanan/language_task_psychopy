"""
testing.py
----------
Part 2 trial screen for Task 2. Plays the target word audio, then shows
three text answer options once the word has been played (shuffled). The
participant clicks one to select it. Returns the selected answer and
whether it was correct.
"""

import random
from psychopy import visual, event, core, sound

# ── Layout constants (degrees) ────────────────────────────────────────────────
_TITLE_Y         =  10.0
_WORD_POS        = (-8.0, 7.0)    # play button for the target word
_WORD_LABEL_X    = -13.0
_PLAY_W          =  3.5
_PLAY_H          =  1.4
_OPTION_START_Y  =  3.0           # top of the answer options
_OPTION_SPACING  =  3.0
_OPTION_W        =  10.0
_OPTION_H        =  1.6
_CLICK_DEBOUNCE  =  0.2


def _hit(mx, my, cx, cy, w, h):
    """Return True if the mouse click landed inside a rectangle."""
    return abs(mx - cx) <= w / 2 and abs(my - cy) <= h / 2


def _make_audio_btn(win, col, label, pos):
    """Build a single play button with a text label to its left."""
    audio_lbl = visual.TextStim(
        win, text=label,
        pos=(_WORD_LABEL_X, pos[1]), height=0.8, bold=True,
        color=col['text']
    )
    play_bg = visual.Rect(
        win, width=_PLAY_W, height=_PLAY_H,
        pos=pos,
        fillColor=col['accent'], lineColor=None
    )
    play_lbl = visual.TextStim(
        win, text="Play",
        pos=pos, height=0.7, bold=True,
        color='white'
    )
    return {
        'label':      audio_lbl,
        'play_bg':    play_bg,
        'play_lbl':   play_lbl,
        'pos':        pos,
        'is_playing': False,
        'played':     False,
    }


def _make_option(win, col, text, y):
    """Build one clickable text answer option."""
    return {
        'text':    text,
        'bg': visual.Rect(
            win, width=_OPTION_W, height=_OPTION_H,
            pos=(0, y),
            fillColor='white', lineColor=col['muted'], lineWidth=2
        ),
        'lbl': visual.TextStim(
            win, text=text,
            pos=(0, y), height=0.85,
            color=col['text']
        ),
        'y':       y,
        'selected': False,
    }


def run_task2_part2(win, m, colors, trial_num,
                    audio_word,
                    correct_answer, incorrect_answer1, incorrect_answer2):
    """
    Run one Part 2 trial for Task 2.

    The target word must be played before the answer options become visible.
    The participant clicks one of the three shuffled text options to select
    it. Selecting a new option deselects the previous one.

    Args:
        win:               PsychoPy Window object.
        m:                 PsychoPy Mouse object.
        colors:            Colors dict from config.
        trial_num:         Trial number shown in the title.
        audio_word:        Path to the target word audio file.
        correct_answer:    Correct answer string (from config).
        incorrect_answer1: First incorrect answer string (from config).
        incorrect_answer2: Second incorrect answer string (from config).

    Returns:
        Tuple (selected_answer, is_correct):
            selected_answer -- the text option the participant clicked.
            is_correct      -- True if they picked the correct answer.
    """
    col = colors

    # Shuffle the three answer options
    options_texts = [correct_answer, incorrect_answer1, incorrect_answer2]
    random.shuffle(options_texts)

    # Load audio
    snd_word = sound.Sound(audio_word)

    # Clock for end-of-playback detection
    clk_word = core.Clock()
    dur_word = snd_word.getDuration()

    is_playing  = False
    word_played = False   # gate -- options hidden until word is played

    title = visual.TextStim(
        win, text=f"Trial {trial_num}",
        pos=(0, _TITLE_Y), height=1.1, bold=True,
        color=col['text']
    )
    hint = visual.TextStim(
        win, text="Speel het woord eerst af.",
        pos=(0, _OPTION_START_Y - 0.5), height=0.75,
        color=col['muted']
    )

    word_btn = _make_audio_btn(win, col, "Woord", _WORD_POS)

    options = [
        _make_option(win, col, text, _OPTION_START_Y - i * _OPTION_SPACING)
        for i, text in enumerate(options_texts)
    ]

    selected_text = None

    def stop_word():
        """Stop the word audio if it's playing."""
        nonlocal is_playing
        snd_word.stop()
        is_playing             = False
        word_btn['is_playing'] = False
        word_btn['play_lbl'].text = "Play"

    while True:

        # ── 1. Detect natural end of playback ─────────────────────────────────
        if is_playing and clk_word.getTime() >= dur_word:
            stop_word()

        # ── 2. Highlight selected option ──────────────────────────────────────
        for opt in options:
            if opt['selected']:
                opt['bg'].fillColor  = col['accent']
                opt['lbl'].color     = 'white'
            else:
                opt['bg'].fillColor  = 'white'
                opt['lbl'].color     = col['text']

        # ── 3. Draw ───────────────────────────────────────────────────────────
        title.draw()
        word_btn['label'].draw()
        word_btn['play_bg'].draw()
        word_btn['play_lbl'].draw()

        if word_played:
            for opt in options:
                opt['bg'].draw()
                opt['lbl'].draw()
        else:
            hint.draw()

        win.flip()

        # ── 4. Mouse input ────────────────────────────────────────────────────
        if m.getLeftButtonPressed():
            mx, my = m.getPos()

            # Word play button -- always clickable
            if _hit(mx, my, *_WORD_POS, _PLAY_W, _PLAY_H):
                if is_playing:
                    stop_word()
                else:
                    snd_word.seek(0)
                    snd_word.play()
                    clk_word.reset()
                    is_playing                = True
                    word_btn['is_playing']    = True
                    word_btn['play_lbl'].text = "Pause"
                    word_played               = True
                core.wait(_CLICK_DEBOUNCE)

            # Answer options -- only after word played
            elif word_played:
                for opt in options:
                    if _hit(mx, my, 0, opt['y'], _OPTION_W, _OPTION_H):
                        for other in options:
                            other['selected'] = False
                        opt['selected'] = True
                        selected_text   = opt['text']
                        core.wait(_CLICK_DEBOUNCE)
                        break

        # Return as soon as an option is selected (no confirm button here)
        if selected_text is not None:
            stop_word()
            is_correct = selected_text == correct_answer
            return selected_text, is_correct

        keys = event.getKeys()
        if 'escape' in keys or 'q' in keys:
            stop_word()
            win.close()
            core.quit()