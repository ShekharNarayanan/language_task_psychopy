"""
rating.py
---------
Confidence rating screen. Participant presses 1-4 to select a rating,
then Enter to confirm. Returns the selected rating as an integer.
"""

from psychopy import visual, event

# ── Layout constants (degrees) ────────────────────────────────────────────────
_BOX_Y          =  0.0    # vertical centre of the rating boxes
_BOX_SIZE       =  2.0    # width and height of each box
_BOX_SPACING    =  3.5    # distance between box centres
_LABEL_OFFSET_Y = -2.0    # y offset for 'Guess' / 'Remember' labels below boxes
_TITLE_Y        =  4.0    # y position of the instruction text
_RATINGS        = [1, 2, 3, 4]


def run_rating(win, text_color, rating_text):
    """
    Show a 1-4 confidence rating screen and wait for the participant to
    confirm their choice with Enter.

    Participant presses 1, 2, 3, or 4 to highlight a box, then Enter to
    confirm. The selected box turns black to show the current choice.
    Backspace clears the selection.

    Args:
        win:         PsychoPy Window object.
        text_color:  Color for all text and unselected box outlines.
        rating_text: Instruction string shown above the rating boxes
                     (e.g. the Dutch confidence question from config).

    Returns:
        Selected rating as an int (1, 2, 3, or 4).
    """
    # Centre the 4 boxes horizontally
    total_w   = (_BOX_SPACING * 3)
    start_x   = -total_w / 2

    title = visual.TextStim(
        win, text=rating_text,
        pos=(0, _TITLE_Y), height=0.9, bold=True,
        color=text_color, wrapWidth=30
    )

    # Build one box + number label per rating
    boxes = []
    for i, rating in enumerate(_RATINGS):
        x = start_x + i * _BOX_SPACING
        boxes.append({
            'rating': rating,
            'x':      x,
            'bg': visual.Rect(
                win, width=_BOX_SIZE, height=_BOX_SIZE,
                pos=(x, _BOX_Y),
                fillColor='white', lineColor=text_color, lineWidth=2
            ),
            'lbl': visual.TextStim(
                win, text=str(rating),
                pos=(x, _BOX_Y), height=0.9, bold=True,
                color=text_color
            ),
        })

    # 'Guess' under box 1, 'Remember' under box 4
    lbl_guess = visual.TextStim(
        win, text="Gok",
        pos=(boxes[0]['x'], _BOX_Y + _LABEL_OFFSET_Y),
        height=0.7, color=text_color
    )
    lbl_remember = visual.TextStim(
        win, text="Herinner",
        pos=(boxes[3]['x'], _BOX_Y + _LABEL_OFFSET_Y),
        height=0.7, color=text_color
    )

    # hint = visual.TextStim(
    #     win, text="Press 1-4 to select, Enter to confirm",
    #     pos=(0, _BOX_Y - 3.5), height=0.7,
    #     color=text_color
    # )

    selected = None

    while True:

        # ── Update box colours based on selection ─────────────────────────────
        for b in boxes:
            if b['rating'] == selected:
                b['bg'].fillColor  = text_color   # selected — filled
                b['lbl'].color     = 'white'
            else:
                b['bg'].fillColor  = 'white'      # unselected — empty
                b['lbl'].color     = text_color

        # ── Draw ──────────────────────────────────────────────────────────────
        title.draw()
        for b in boxes:
            b['bg'].draw()
            b['lbl'].draw()
        lbl_guess.draw()
        lbl_remember.draw()
        # hint.draw()
        win.flip()

        # ── Keyboard input ────────────────────────────────────────────────────
        keys = event.getKeys()

        for k in keys:
            if k in ('1', '2', '3', '4'):
                selected = int(k)
            elif k == 'return' and selected is not None:
                return selected
            elif k == 'backspace':
                selected = None