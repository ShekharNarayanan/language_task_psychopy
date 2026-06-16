"""
task2_part1.py
--------------
Part 1 trial screen for Task 2. Displays two sentences and asks the
participant to type what they think the target word means. They either
type an answer and press Enter, or click 'geen betekenis' if the word
had no congruent meaning based on the sentences.

Returns the participant's response as a string.
"""

from psychopy import visual, event, core

# ── Layout constants (degrees) ────────────────────────────────────────────────
_TITLE_Y         =  9.0
_SENTENCE_A_Y    =  5.0
_SENTENCE_B_Y    =  2.0
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


def run_task2_part1(win, m, colors, trial_num, sentence_a, sentence_b):
    """
    Run one Part 1 trial for Task 2.

    Shows two sentences on screen. The participant types their interpretation
    of the target word in the input box and presses Enter to confirm, or
    clicks 'geen betekenis' if the sentences had no congruent meaning.

    Args:
        win:        PsychoPy Window object.
        m:          PsychoPy Mouse object.
        colors:     Colors dict from config (keys: text, accent, muted, success).
        trial_num:  Trial number shown in the title.
        sentence_a: First sentence string (from config).
        sentence_b: Second sentence string (from config).

    Returns:
        Response string — either the typed answer or 'geen betekenis'.
    """
    col          = colors
    typed_text   = ''

    title = visual.TextStim(
        win, text=f"Trial {trial_num}",
        pos=(0, _TITLE_Y), height=1.1, bold=True,
        color=col['text']
    )
    stim_a = visual.TextStim(
        win, text=sentence_a,
        pos=(0, _SENTENCE_A_Y), height=0.9,
        color=col['text'], wrapWidth=35
    )
    stim_b = visual.TextStim(
        win, text=sentence_b,
        pos=(0, _SENTENCE_B_Y), height=0.9,
        color=col['text'], wrapWidth=35
    )

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
        win, text='Type your answer and press Enter...',
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

    while True:

        # ── Draw ──────────────────────────────────────────────────────────────
        title.draw()
        stim_a.draw()
        stim_b.draw()
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
            if k == 'return' and typed_text:
                return typed_text.strip()

            elif k == 'backspace':
                typed_text = typed_text[:-1]

            elif k == 'escape':
                win.close()
                core.quit()

            elif len(k) == 1:  # single printable character
                typed_text += k

        # ── Mouse input ───────────────────────────────────────────────────────
        if m.getLeftButtonPressed():
            mx, my = m.getPos()
            if _hit(mx, my, *_GEEN_POS, _GEEN_W, _GEEN_H):
                core.wait(_CLICK_DEBOUNCE)
                return _GEEN_LABEL
