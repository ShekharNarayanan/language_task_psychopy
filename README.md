# Designing a behavioral experiment in Psychopy.

The repository contains python code for developing a language task based behavioral experiment. Made primarily using the PsychoPy library.

**Note: Under active development.**

---

## For returning users

1. Navigate to the project folder using the windows command line. You can open the windows cmd window by searching `cmd` in the windows search bar.
2. Once you have opened it, navigate to the folder for this project. You can use the example below and replace the path after `cd` with your own path.

**Note**: Press Enter after copy pasting a code chunk.

```bash
cd your/project/folder
```

3. Next step is to update your local code and make it up to date with the repository.

```bash
git pull
```

4. Once you have the updated code, please update your environment.

```bash
uv sync
```

5. When your environment is updated, copy paste the following code:

```bash
.venv\Scripts\activate
```

6. Run the behavioral experiment:

```bash
python -m main --p_id 1 --set_num 1 --test_run True
```

Meaning of parameters:
1. `p_id`: the participant number for this current session. Can be any integer.
2. `set_num`: the set for which the audio files have to be played. Can be 1 or 2.
3. `test_run`: to run the test version of the experiment. If the flag is set to `True` you will get **one** trial for each part of the experiment. If set to `False`, you get all the trials. You can change these in the `system_config.yaml` file.

---

## Table of contents

- [1. Task 1](#1-task)
  - [1.1 Introduction](#11-introduction)
  - [1.2 Project layout and configuration](#12-project-layout-and-configuration)
    - [1.2.1 Project structure](#121-project-structure)
    - [1.2.2 What each module does](#122-what-each-module-does)
    - [1.2.3 Configuration](#123-configuration)
  - [1.3 Experiment flow](#13-experiment-flow)
    - [1.3.1 Overview](#131-overview)
    - [1.3.2 Part 1, word recognition](#132-part-1-word-recognition)
    - [1.3.3 Part 2, syllable completion](#133-part-2-syllable-completion)
    - [1.3.4 Confidence ratings](#134-confidence-ratings)
    - [1.3.5 Results output](#135-results-output)
  - [1.4 Installation and usage](#14-installation-and-usage)
    - [1.4.1 Clone the repository](#141-clone-the-repository)
    - [1.4.2 Install dependencies](#142-install-dependencies)
    - [1.4.3 Run the experiment](#143-run-the-experiment)

---

## 1. Task 1

### 1.1 Introduction

This experiment exposes participants to a continuous audio stream of an artificial language. Afterwards, participants complete two sets of audio-based multiple choice trials to assess how much of the language they implicitly learned.

All instructions are presented in Dutch. The experiment supports multiple stimulus sets (Set 1, Set 2, etc.), each with its own configuration file, so the same codebase can be reused across counterbalanced versions.

---

### 1.2 Project layout and configuration

#### 1.2.1 Project structure

```
.
├── main.py                      Experiment entry point
├── system_config.yaml           Monitor, window, and color settings
├── config_set1.yaml             Stimuli and trial definitions for Set 1
├── config_set2.yaml             Stimuli and trial definitions for Set 2
├── screens/
│   ├── audio_player.py          Primary audio exposure screen (with seek bar)
│   ├── audio_mcq.py             Part 1 and Part 2 MCQ trial screens
│   ├── rating.py                Confidence rating screen (1 to 4 scale)
│   ├── instruction.py           Generic instruction screen (advances on SPACE)
│   └── fixation.py              Fixation cross screen
└── stimuli/
    ├── task1/
    │   ├── set1/                Audio files for Set 1
    │   └── set2/                Audio files for Set 2
    └── ...
```

#### 1.2.2 What each module does

- **`main.py`**: loads the config, sets up the monitor and window, collects the participant ID via `--p_id`, and runs all screens in order. Results are collected as a list of dicts and saved as a CSV at the end.
- **`system_config.yaml`**: holds machine-level settings, monitor dimensions, viewing distance, window units, and colors. This file stays the same across experiments.
- **`config_set{n}.yaml`**: holds all stimulus paths, trial definitions, instruction texts, and correct answer indices for a given stimulus set.
- **`audio_player.py`**: shows a seekable audio player with a progress bar and play/pause toggle. The participant must play the audio at least once before continuing.
- **`audio_mcq.py`**: contains two functions, `run_audio_mcq_part1` for standard MCQ trials (options only) and `run_audio_mcq_part2` for completion trials (reference audio shown at the top, options below). In both, options are shuffled on every trial, the participant must play all options before confirming, and a checkbox is used for single selection.
- **`rating.py`**: shows a 1 to 4 confidence scale after each trial. Participant presses a number key to select, then Enter to confirm.
- **`instruction.py`**: displays any block of text and waits for SPACE. Used for welcome, pre-test instructions, and part transitions.

#### 1.2.3 Configuration

Machine-level settings live in `system_config.yaml`:

```yaml
monitor:
  name: my_lab_monitor
  width_cm: 53.1
  distance_cm: 60.0
  width_px: 1920
  height_px: 1080

window:
  units: deg
  fullscreen: true

colors:
  background: white
  text: black
  accent: blue
  success: green
  muted: gray

audio:
  backends: [sounddevice, pygame]
```

Stimulus-level settings live in `config_set{n}.yaml`. Each trial specifies its audio paths and which index is the correct answer (always 0 before shuffling):

```yaml
stimuli:
  welcome_text: 'In dit deel van het experiment ...'
  test_text: 'Je wordt nu gevraagd ...'
  rating_text: 'Hoe zeker bent u van uw antwoord?'

  part_1:
    n_trials: 34
    primary_audio: 'stimuli/task1/set1/audio_set1.wav'
    trial_1:
      correct: 0
      audio_paths: [stimuli/task1/set1/set1_words1.wav, ...]

  part_2:
    n_trials: 8
    part_2_msg: 'Kies bij deze woorden ...'
    trial_1:
      correct: 0
      primary_audio: 'stimuli/task1/set1/set1_complete1.wav'
      audio_paths: [stimuli/task1/set1/set1_syll2.wav, ...]
```

---

### 1.3 Experiment flow

#### 1.3.1 Overview

```
Welcome screen
    |
Primary audio exposure (seekable player, ~15 min)
    |
Pre-test instruction screen
    |
Part 1 trials x 34  (word recognition MCQ + confidence rating after each)
    |
Part 2 instruction screen
    |
Part 2 trials x 8   (syllable completion MCQ + confidence rating after each)
    |
End, results saved
```

#### 1.3.2 Part 1, word recognition

Each trial presents 2 to 4 audio options. The participant must:

1. Play all options at least once (play buttons gray out until clicked)
2. Tick the checkbox next to their chosen answer
3. Click Confirm (only active once all options played and one box ticked)

Options are shuffled on every trial so the correct answer never appears in a fixed position.

#### 1.3.3 Part 2, syllable completion

Same structure as Part 1 but with a reference audio clip shown at the top of the screen. The reference must be played before the options become available. The participant then plays all options, selects one, and confirms.

#### 1.3.4 Confidence ratings

After every trial (both parts), a 1 to 4 rating screen appears:

```
Hoe zeker bent u van uw antwoord?

[ 1 ]    [ 2 ]    [ 3 ]    [ 4 ]
 Gok                          Herinner
```

Press 1 to 4 to highlight a box, Enter to confirm.

#### 1.3.5 Results output

Results are saved as `results_<participant_id>.csv` in the project root. One row per trial:

| Column | Description |
|---|---|
| `participant_id` | Value passed via `--p_id` |
| `part` | 1 or 2 |
| `trial_num` | Trial number within the part |
| `correct_option` | Position of correct answer after shuffling |
| `selected_option` | Position chosen by participant |
| `is_correct` | True or False |
| `rating` | Confidence rating (1 to 4) |

---

### 1.4 Installation and usage

#### 1.4.1 Clone the repository

```bash
git clone <repo_url>
cd <repo_folder>
```

#### 1.4.2 Install dependencies

This project uses [uv](https://docs.astral.sh/uv/) for environment and dependency management with Python 3.10.

```bash
uv venv
uv sync
```

Main dependencies:

- `psychopy` for experiment infrastructure
- `sounddevice` and `pygame` as audio backends
- `pyyaml` for loading config files
- `pandas` for results output

#### 1.4.3 Run the experiment

```bash
python -m main --p_id 1 --set_num 1 --test_run True
```

- `--p_id`: participant identifier, used to name the results CSV
- `--set_num`: which stimulus set to load (1 or 2)
- `--test_run`: set to `True` for one trial per part, `False` for all trials

Press **Escape** or **Q** at any point to quit the experiment.