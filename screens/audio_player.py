"""
audio_player.py
---------------
Audio playback screen with a seekable progress bar and play/pause toggle.
Participants must play the audio at least once before continuing.
"""

from psychopy import visual, event, core, sound

# ── Layout constants (degrees) ────────────────────────────────────────────────
# All positions and sizes are in degrees of visual angle to stay consistent
# with the monitor-calibrated window units set in main.py.
_SEEK_Y         =  0.0    # vertical centre of the seek bar
_SEEK_LEFT      = -10.0   # left edge of seek bar
_SEEK_RIGHT     =  10.0   # right edge of seek bar
_SEEK_W         = _SEEK_RIGHT - _SEEK_LEFT
_SEEK_H         =  0.4    # thickness of the seek bar track
_SEEK_HIT_PAD   =  1.5    # vertical click tolerance around the seek bar
_PLAY_POS       = (0, -2.5)
_PLAY_W         =  6
_PLAY_H         =  4
_CONT_POS       = (0, -5.5)
_CONT_W         =  6
_CONT_H         =  4
_CLICK_DEBOUNCE =  0.2    # seconds to wait after a button click to prevent double-firing


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt(seconds):
    """Convert a duration in seconds to a 'm:ss' display string."""
    s = int(max(0, seconds))
    return f"{s // 60}:{s % 60:02d}"


def _ratio(mouse_x):
    """
    Map a mouse x-position to a 0-1 seek ratio along the seek bar.
    Clamps to [0, 1] so clicks outside the bar don't overshoot.
    """
    return max(0.0, min(1.0, (mouse_x - _SEEK_LEFT) / _SEEK_W))


def _hit(mx, my, cx, cy, w, h):
    """Return True if (mx, my) is inside an axis-aligned rectangle."""
    return abs(mx - cx) <= w / 2 and abs(my - cy) <= h / 2


def _on_seekbar(mx, my):
    """Return True if the mouse is within the clickable seek bar region."""
    return (abs(my - _SEEK_Y) < _SEEK_HIT_PAD
            and _SEEK_LEFT - 0.5 <= mx <= _SEEK_RIGHT + 0.5)


# ── Stim builder ──────────────────────────────────────────────────────────────

def _build_stims(win, col, total_dur):
    """
    Instantiate and return all visual stimuli as a dict.

    Keeping construction here and out of the frame loop makes run_audio_player
    easier to read - the loop only handles logic, not object creation.

    Draw order is determined by insertion order (Python 3.7+): title first,
    continue button last.
    """
    return {
        'title': visual.TextStim(
            win, text="Listen to the audio",
            pos=(0, 3), height=1.1, bold=True,
            color=col['text']
        ),
        # Seek bar: track (background) + fill (progress) + handle (scrubber dot)
        'seek_track': visual.Rect(
            win, width=_SEEK_W, height=_SEEK_H,
            pos=(0, _SEEK_Y),
            fillColor=col['muted'], lineColor=None
        ),
        # Fill rect: we manually compute centre pos each frame to avoid
        # relying on anchor='left' which is not available in older PsychoPy
        'seek_fill': visual.Rect(
            win, width=0.01, height=_SEEK_H,
            pos=(_SEEK_LEFT, _SEEK_Y),
            fillColor=col['accent'], lineColor=None
        ),
        'seek_handle': visual.Circle(
            win, radius=0.45,
            pos=(_SEEK_LEFT, _SEEK_Y),           # x position updated each frame
            fillColor=col['accent'], lineColor=None
        ),
        # Time labels flanking the seek bar
        'lbl_elapsed': visual.TextStim(
            win, text="0:00",
            pos=(_SEEK_LEFT - 1.2, _SEEK_Y),
            height=0.7, color=col['text']
        ),
        'lbl_total': visual.TextStim(
            win, text=_fmt(total_dur),
            pos=(_SEEK_RIGHT + 1.2, _SEEK_Y),
            height=0.7, color=col['text']
        ),
        # Play / Pause button
        'play_bg': visual.Rect(
            win, width=_PLAY_W, height=_PLAY_H,
            pos=_PLAY_POS,
            fillColor=col['accent'], lineColor=None
        ),
        'play_lbl': visual.TextStim(
            win, text="▶  Play",
            pos=_PLAY_POS, height=0.85, bold=True,
            color='white'
        ),
        # Continue button - fillColor toggled green once audio has been played
        'cont_bg': visual.Rect(
            win, width=_CONT_W, height=_CONT_H,
            pos=_CONT_POS,
            fillColor=col['muted'], lineColor=None
        ),
        'cont_lbl': visual.TextStim(
            win, text="Continue ->",
            pos=_CONT_POS, height=0.85, bold=True,
            color='white'
        ),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def run_audio_player(win, m, colors, audio_path):
    """
    Run the audio player screen.

    Each iteration of the while loop is one display frame. The loop:
      1. Advances the playhead if audio is playing.
      2. Updates seek bar visuals to reflect current progress.
      3. Draws all stimuli and flips the window.
      4. Handles mouse clicks (seek, play/pause, continue).

    Blocks until the participant clicks Continue, which is only enabled after
    the audio has been played at least once. Escape quits the experiment.

    Args:
        win: PsychoPy Window object.
        m:   PsychoPy Mouse object.
        cfg: Config dict loaded from config.yaml.
    """
    col   = colors
    audio = sound.Sound(f'{audio_path}')
    dur   = audio.getDuration()
    clock = core.Clock()   # measures time elapsed since last play/seek
    s     = _build_stims(win, col, dur)

    is_playing   = False   # whether audio is currently playing
    audio_played = False   # whether audio has been played at least once
    elapsed      = 0.0     # current playback position in seconds
    play_start   = 0.0     # value of elapsed when play was last pressed

    while True:

        # ── 1. Advance playhead ───────────────────────────────────────────────
        if is_playing:
            # elapsed = where we started + how long clock has been running
            elapsed = min(play_start + clock.getTime(), dur)
            if elapsed >= dur:
                # Audio finished naturally - reset to stopped state
                audio.stop()
                is_playing         = False
                elapsed            = dur
                s['play_lbl'].text = "▶  Play"

        # ── 2. Update seek bar visuals ────────────────────────────────────────
        progress = elapsed / dur if dur > 0 else 0
        fill_w   = max(0.01, progress * _SEEK_W)

        # Centre the fill rect so its left edge always aligns with _SEEK_LEFT
        s['seek_fill'].width  = fill_w
        s['seek_fill'].pos    = (_SEEK_LEFT + fill_w / 2, _SEEK_Y)
        s['seek_handle'].pos  = (_SEEK_LEFT + progress * _SEEK_W, _SEEK_Y)
        s['lbl_elapsed'].text = _fmt(elapsed)

        # Continue button is gray until audio has been played at least once
        s['cont_bg'].fillColor = col['success'] if audio_played else col['muted']

        # ── 3. Draw & flip ────────────────────────────────────────────────────
        for stim in s.values():
            stim.draw()
        win.flip()

        # ── 4. Mouse input ────────────────────────────────────────────────────
        if m.getLeftButtonPressed():
            mx, my = m.getPos()

            if _on_seekbar(mx, my):
                # Scrub to clicked position; resume playing if already playing
                elapsed    = _ratio(mx) * dur
                play_start = elapsed
                audio.stop()
                audio.seek(elapsed)
                if is_playing:
                    audio.play()
                    clock.reset()
                audio_played = True

            elif _hit(mx, my, *_PLAY_POS, _PLAY_W, _PLAY_H):
                # Toggle play / pause
                if is_playing:
                    audio.stop()
                    is_playing         = False
                    s['play_lbl'].text = "▶  Play"
                else:
                    audio.stop()
                    audio.seek(elapsed)
                    audio.play()
                    play_start         = elapsed  # remember where we resumed from
                    clock.reset()                 # clock now measures time since resume
                    is_playing         = True
                    audio_played       = True
                    s['play_lbl'].text = "⏸  Pause"
                core.wait(_CLICK_DEBOUNCE)  # prevent double-firing on a single click

            elif audio_played and _hit(mx, my, *_CONT_POS, _CONT_W, _CONT_H):
                # Advance to next screen
                audio.stop()
                break

        if "escape" in event.getKeys():
            audio.stop()
            win.close()
            core.quit()