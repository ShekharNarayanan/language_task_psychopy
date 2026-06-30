"""
exposure.py
-----------
Part 1 trial screen for Task 2. Displays two sentences, each with a play
button for its audio, and asks the participant to type what they think the
target word means. They either type an answer and press Enter, or click
'geen betekenis' if the word had no congruent meaning based on the sentences.

Returns the participant's response as a string.
"""

from psychopy import visual, event, core, sound

# ── Layout constants (degrees) ────────────────────────────────────────────────
_TITLE_Y         =  9.0
_SENTENCE_A_Y    =  5.5
_PLAY_A_POS      = (13.0, 5.5)
_SENTENCE_B_Y    =  2.0
_PLAY_B_POS      = (13.0, 2.0)
_PLAY_W          =  3.0
_PLAY_H          =  1.2
_INPUT_Y         = -2.0
_INPUT_W         =  20.0
_INPUT_H         =  2.0
_GEEN_POS        = (0, -6.0)
_GEEN_W          =  6.0
_GEEN_H          =  1.8
_CLICK_DEBOUNCE  =  0.2
_GEEN_LABEL      = 'geen betekenis'


def _hit(mx, my, cx, cy, w, h):
    """Return True if the mouse click landed inside a rectangle."""
    return abs(mx - cx) <= w / 2 and abs(my - cy) <= h / 2


def _make_play_button(win, col, pos):
    """Build a single play/pause button with its own playback state."""
    return {
        'bg': visual.Rect(
            win, width=_PLAY_W, height=_PLAY_H,
            pos=pos,
            fillColor=col['accent'], lineColor=None
        ),
        'lbl': visual.TextStim(
            win, text="Afspelen",
            pos=pos, height=0.7, bold=True,
            color='white'
        ),
        'pos':        pos,
        'is_playing': False,
    }


def run_task2_part1(win, m, colors, trial_num,
                    sentence_a, sentence_a_audio,
                    sentence_b, sentence_b_audio):
    """
    Run one Part 1 trial for Task 2.

    Shows two sentences on screen, each with a play button for its audio.
    The participant types their interpretation of the target word in the
    input box and presses Enter to confirm, or clicks 'geen betekenis' if
    the sentences had no congruent meaning. Only one sentence audio plays
    at a time.

    Args:
        win:               PsychoPy Window object.
        m:                 PsychoPy Mouse object.
        colors:            Colors dict from config (keys: text, accent, muted, success).
        trial_num:         Trial number shown in the title.
        sentence_a:        First sentence string (from config).
        sentence_a_audio:  Path to sentence A audio file.
        sentence_b:        Second sentence string (from config).
        sentence_b_audio:  Path to sentence B audio file.

    Returns:
        Response string -- either the typed answer or 'geen betekenis'.
    """
    col          = colors
    typed_text   = ''

    # Load sentence audio and clocks for end-of-playback detection
    snd_a = sound.Sound(sentence_a_audio)
    snd_b = sound.Sound(sentence_b_audio)
    clk_a = core.Clock()
    clk_b = core.Clock()
    dur_a = snd_a.getDuration()
    dur_b = snd_b.getDuration()

    playing = None   # 'a', 'b', or None -- only one plays at a time
    played_a = False
    played_b = False
    

    title = visual.TextStim(
        win, text=f"Trial {trial_num}",
        pos=(0, _TITLE_Y), height=1.1, bold=True,
        color=col['text']
    )    
    
    instruction = visual.TextStim( # added instruction to clarify both need to be played
        win, text = "Speel beide zinnen af voordat je antwoord geeft",
        pos = (0, _TITLE_Y - 1.5), height=0.7,
        color=col['muted']
    ) 
    
    stim_a = visual.TextStim(
        win, text=sentence_a,
        pos=(-2.0, _SENTENCE_A_Y), height=0.9, 
        color=col['text'], wrapWidth=20 # shifted left (-2.0) and reduced from 25 to prevent overlap with play button
    )
    stim_b = visual.TextStim(
        win, text=sentence_b,
        pos=(-2.0, _SENTENCE_B_Y), height=0.9,
        color=col['text'], wrapWidth=20 # shifted left (-2.0) and reduced from 25 to prevent overlap with play button
    )

    play_a_btn = _make_play_button(win, col, _PLAY_A_POS)
    play_b_btn = _make_play_button(win, col, _PLAY_B_POS)

    # Text input box
    input_bg = visual.Rect(
        win, width=_INPUT_W, height=_INPUT_H,
        pos=(0, _INPUT_Y),
        fillColor='white', lineColor=col['text'], lineWidth=2
    )
    input_lbl = visual.TextStim(
        win, text='',
        pos=(0, _INPUT_Y), height=0.8,
        color=col['text']
    )
    input_hint = visual.TextStim(
        win, text='Typ hier je antwoord en druk op Enter...',
        pos=(0, _INPUT_Y), height=0.7,
        color=col['muted']
    )

    # Geen betekenis button
    geen_bg = visual.Rect(
        win, width=_GEEN_W, height=_GEEN_H,
        pos=_GEEN_POS,
        fillColor=col['muted'], lineColor=None
    )
    geen_lbl = visual.TextStim(
        win, text=_GEEN_LABEL,
        pos=_GEEN_POS, height=0.8, bold=True,
        color='white'
    )

    def stop_all():
        """Stop whichever sentence audio is currently playing."""
        nonlocal playing, played_a, played_b
        snd_a.stop()
        snd_b.stop()
        play_a_btn['is_playing'] = False
        play_b_btn['is_playing'] = False
        play_a_btn['lbl'].text   = "Afspelen"
        play_b_btn['lbl'].text   = "Afspelen"
        playing = None

    while True:

        # ── Detect natural end of playback ──────────────────────────────────
        if playing == 'a' and clk_a.getTime() >= dur_a:
            stop_all()
            played_a = True
        elif playing == 'b' and clk_b.getTime() >= dur_b:
            stop_all()
            played_b = True

        # ── Draw ──────────────────────────────────────────────────────────────
        title.draw()
        instruction.draw()
        stim_a.draw()
        play_a_btn['bg'].draw()
        play_a_btn['lbl'].draw()
        stim_b.draw()
        play_b_btn['bg'].draw()
        play_b_btn['lbl'].draw()
        input_bg.draw()

        # Show hint when nothing typed yet, typed text otherwise
        if typed_text:
            input_lbl.text = typed_text
            input_lbl.draw()
        else:
            input_hint.draw()

        geen_bg.draw()
        geen_lbl.draw()
        win.flip()

        # ── Keyboard input ────────────────────────────────────────────────────
        keys = event.getKeys()

        for k in keys:
            if k == 'escape' or k == 'q':
                stop_all()
                win.close()
                core.quit()
                
            elif played_a and played_b: # both audios need to have been played
                if k == 'return' and typed_text:
                    stop_all()
                    return typed_text.strip()

                elif k == 'backspace':
                    typed_text = typed_text[:-1]

                elif len(k) == 1:  # single printable character
                    typed_text += k

        # ── Mouse input ───────────────────────────────────────────────────────
        if m.getLeftButtonPressed():
            mx, my = m.getPos()

            if _hit(mx, my, *_PLAY_A_POS, _PLAY_W, _PLAY_H):
                stop_all()
                snd_a.seek(0)
                snd_a.play()
                clk_a.reset()
                playing                  = 'a'
                play_a_btn['is_playing'] = True
                play_a_btn['lbl'].text   = "Pauzeren"
                core.wait(_CLICK_DEBOUNCE)

            elif _hit(mx, my, *_PLAY_B_POS, _PLAY_W, _PLAY_H):
                stop_all()
                snd_b.seek(0)
                snd_b.play()
                clk_b.reset()
                playing                  = 'b'
                play_b_btn['is_playing'] = True
                play_b_btn['lbl'].text   = "Pauzeren"
                core.wait(_CLICK_DEBOUNCE)

            elif played_a and played_b and _hit(mx, my, *_GEEN_POS, _GEEN_W, _GEEN_H):
                stop_all()
                core.wait(_CLICK_DEBOUNCE)
                return _GEEN_LABEL