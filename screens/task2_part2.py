"""
task2_part2.py
--------------
Part 2 trial screen for Task 2. Plays a target word audio, then lets the
participant play two context sentences. Once the word has been played,
three text answer options appear (shuffled). The participant clicks one
to select it. Returns the selected answer and whether it was correct.
"""

import random
from psychopy import visual, event, core, sound

# ── Layout constants (degrees) ────────────────────────────────────────────────
_TITLE_Y         =  10.0
_WORD_POS        = (-8.0, 7.0)    # play button for the target word
_WORD_LABEL_X    = -13.0
_SENT_A_POS      = (-8.0, 4.0)    # play button for sentence A
_SENT_B_POS      = (-8.0, 1.5)    # play button for sentence B
_PLAY_W          =  3.5
_PLAY_H          =  1.4
_OPTION_START_Y  = -1.5           # top of the answer options
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
                    audio_word, audio_sentence_a, audio_sentence_b,
                    correct_answer, incorrect_answer1, incorrect_answer2):
    """
    Run one Part 2 trial for Task 2.

    The target word must be played before the answer options become visible.
    The two sentence audio clips can be played freely at any time. The
    participant clicks one of the three shuffled text options to select it.
    Selecting a new option deselects the previous one.

    Args:
        win:               PsychoPy Window object.
        m:                 PsychoPy Mouse object.
        colors:            Colors dict from config.
        trial_num:         Trial number shown in the title.
        audio_word:        Path to the target word audio file.
        audio_sentence_a:  Path to sentence A audio file.
        audio_sentence_b:  Path to sentence B audio file.
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
    snd_a    = sound.Sound(audio_sentence_a)
    snd_b    = sound.Sound(audio_sentence_b)

    # Clocks for end-of-playback detection
    clk_word = core.Clock()
    clk_a    = core.Clock()
    clk_b    = core.Clock()
    dur_word = snd_word.getDuration()
    dur_a    = snd_a.getDuration()
    dur_b    = snd_b.getDuration()

    # Track which is currently playing so only one plays at a time
    playing  = None   # 'word', 'a', 'b', or None

    word_played = False   # gate — options hidden until word is played

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
    sent_a_btn = _make_audio_btn(win, col, "Zin A", _SENT_A_POS)
    sent_b_btn = _make_audio_btn(win, col, "Zin B", _SENT_B_POS)

    options = [
        _make_option(win, col, text, _OPTION_START_Y - i * _OPTION_SPACING)
        for i, text in enumerate(options_texts)
    ]

    selected_text = None

    def stop_all():
        """Stop whichever audio is currently playing."""
        nonlocal playing
        snd_word.stop()
        snd_a.stop()
        snd_b.stop()
        word_btn['is_playing']   = False
        sent_a_btn['is_playing'] = False
        sent_b_btn['is_playing'] = False
        word_btn['play_lbl'].text   = "Play"
        sent_a_btn['play_lbl'].text = "Play"
        sent_b_btn['play_lbl'].text = "Play"
        playing = None

    while True:

        # ── 1. Detect natural end of playback ─────────────────────────────────
        if playing == 'word' and clk_word.getTime() >= dur_word:
            stop_all()
        elif playing == 'a' and clk_a.getTime() >= dur_a:
            stop_all()
        elif playing == 'b' and clk_b.getTime() >= dur_b:
            stop_all()

        # ── 2. Gray out sentence buttons until word is played ─────────────────
        for btn in [sent_a_btn, sent_b_btn]:
            btn['play_bg'].fillColor = col['accent'] if word_played else col['muted']

        # ── 3. Highlight selected option ──────────────────────────────────────
        for opt in options:
            if opt['selected']:
                opt['bg'].fillColor  = col['accent']
                opt['lbl'].color     = 'white'
            else:
                opt['bg'].fillColor  = 'white'
                opt['lbl'].color     = col['text']

        # ── 4. Draw ───────────────────────────────────────────────────────────
        title.draw()

        for btn in [word_btn, sent_a_btn, sent_b_btn]:
            btn['label'].draw()
            btn['play_bg'].draw()
            btn['play_lbl'].draw()

        if word_played:
            for opt in options:
                opt['bg'].draw()
                opt['lbl'].draw()
        else:
            hint.draw()

        win.flip()

        # ── 5. Mouse input ────────────────────────────────────────────────────
        if m.getLeftButtonPressed():
            mx, my = m.getPos()

            # Word play button — always clickable
            if _hit(mx, my, *_WORD_POS, _PLAY_W, _PLAY_H):
                stop_all()
                snd_word.seek(0)
                snd_word.play()
                clk_word.reset()
                playing                  = 'word'
                word_btn['is_playing']   = True
                word_btn['play_lbl'].text = "Pause"
                word_played              = True
                core.wait(_CLICK_DEBOUNCE)

            # Sentence A — only after word played
            elif word_played and _hit(mx, my, *_SENT_A_POS, _PLAY_W, _PLAY_H):
                stop_all()
                snd_a.seek(0)
                snd_a.play()
                clk_a.reset()
                playing                    = 'a'
                sent_a_btn['is_playing']   = True
                sent_a_btn['play_lbl'].text = "Pause"
                core.wait(_CLICK_DEBOUNCE)

            # Sentence B — only after word played
            elif word_played and _hit(mx, my, *_SENT_B_POS, _PLAY_W, _PLAY_H):
                stop_all()
                snd_b.seek(0)
                snd_b.play()
                clk_b.reset()
                playing                    = 'b'
                sent_b_btn['is_playing']   = True
                sent_b_btn['play_lbl'].text = "Pause"
                core.wait(_CLICK_DEBOUNCE)

            # Answer options — only after word played
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
            stop_all()
            is_correct = selected_text == correct_answer
            return selected_text, is_correct

        keys = event.getKeys()
        if 'escape' in keys or 'q' in keys:
            stop_all()
            win.close()
            core.quit()
