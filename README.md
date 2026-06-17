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

6. Run Task 1:

```bash
python -m run_task1 --p_id 1 --set_num 1 --test_run True
```

Or run Task 2:

```bash
python -m run_task2 --p_id 1 --set_num 1 --test_run True
```

Meaning of parameters:
1. `p_id`: the participant number for this current session. Can be any integer.
2. `set_num`: the set for which the audio files have to be played. Can be 1 or 2.
3. `test_run`: to run the test version of the experiment. If the flag is set to `True` you will get **one** trial for each part of the experiment. If set to `False`, you get all the trials. You can change these in the `system_config.yaml` file.

---

## Table of contents

- [1. Task 1](#1-task-1)
  - [1.1 Introduction](#11-introduction)
  - [1.2 Experiment flow](#12-experiment-flow)
    - [1.2.1 Overview](#121-overview)
    - [1.2.2 Part 1, word recognition](#122-part-1-word-recognition)
    - [1.2.3 Part 2, syllable completion](#123-part-2-syllable-completion)
    - [1.2.4 Confidence ratings](#124-confidence-ratings)
    - [1.2.5 Results output](#125-results-output)
- [2. Task 2](#2-task-2)
  - [2.1 Introduction](#21-introduction)
  - [2.2 Experiment flow](#22-experiment-flow)
    - [2.2.1 Overview](#221-overview)
    - [2.2.2 Part 1, sentence exposure](#222-part-1-sentence-exposure)
    - [2.2.3 Part 2, word meaning test](#223-part-2-word-meaning-test)
    - [2.2.4 Confidence ratings](#224-confidence-ratings)
    - [2.2.5 Results output](#225-results-output)
- [3. Project layout and configuration](#3-project-layout-and-configuration)
  - [3.1 Project structure](#31-project-structure)
  - [3.2 What each module does](#32-what-each-module-does)
  - [3.3 Configuration](#33-configuration)
- [4. Installation and usage](#4-installation-and-usage)
  - [4.1 Clone the repository](#41-clone-the-repository)
  - [4.2 Install dependencies](#42-install-dependencies)
  - [4.3 Run the experiment](#43-run-the-experiment)

---

## 1. Task 1

### 1.1 Introduction

This experiment exposes participants to a continuous audio stream of an artificial language. Afterwards, participants complete two sets of audio-based multiple choice trials to assess how much of the language they implicitly learned.

All instructions are presented in Dutch. The experiment supports multiple stimulus sets (Set 1, Set 2, etc.), each with its own configuration file, so the same codebase can be reused across counterbalanced versions.

---

### 1.2 Experiment flow

#### 1.2.1 Overview

```
Welcome screen
    |
Primary audio exposure (seekable player)
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

#### 1.2.2 Part 1, word recognition

Each trial presents 2 to 4 audio options. The participant must:

1. Play all options at least once (play buttons gray out until clicked)
2. Tick the checkbox next to their chosen answer
3. Click Confirm (only active once all options played and one box ticked)

Options are shuffled on every trial so the correct answer never appears in a fixed position.

#### 1.2.3 Part 2, syllable completion

Same structure as Part 1 but with a reference audio clip shown at the top of the screen. The reference must be played before the options become available. The participant then plays all options, selects one, and confirms.

#### 1.2.4 Confidence ratings

After every trial (both parts), a 1 to 4 rating screen appears:

```
Hoe zeker bent u van uw antwoord?

[ 1 ]    [ 2 ]    [ 3 ]    [ 4 ]
 Gok                          Herinner
```

Press 1 to 4 to highlight a box, Enter to confirm.

#### 1.2.5 Results output

Results are saved as `participant_<p_id>_task1_set<set_num>.csv` in the `output` folder. One row per trial:

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

## 2. Task 2

### 2.1 Introduction

This experiment teaches participants new words through sentence context, then tests whether they learned the intended meanings. Each new word appears in two sentences during Part 1, and is later tested with a word meaning MCQ in Part 2.

All instructions are presented in Dutch. Trials are split into congruent (the word has one consistent meaning across both sentences) and incongruent (the word has no real meaning), shuffled so no condition appears more than twice in a row.

---

### 2.2 Experiment flow

#### 2.2.1 Overview

```
Part 1 instruction screen
    |
Part 1 trials x 20  (two sentences per trial, play buttons for each, type an answer or click 'geen betekenis')
    |
Part 2 instruction screen
    |
Part 2 trials x 20  (play the word, then choose its meaning + confidence rating after each)
    |
End, results saved
```

#### 2.2.2 Part 1, sentence exposure

Each trial shows two sentences, each with its own play button for the sentence audio. Only one sentence plays at a time. The participant either:

1. Types what they think the new word means and presses Enter, or
2. Clicks 'geen betekenis' if the word has no consistent meaning across the two sentences

#### 2.2.3 Part 2, word meaning test

Each trial plays the target word's audio first. Three text answer options (the correct meaning, two incorrect options, possibly including 'geen betekenis') appear only after the word has been played, shuffled on every trial. The participant clicks one to select it, which immediately advances to the confidence rating.

#### 2.2.4 Confidence ratings

Same 1 to 4 scale as Task 1, shown after every Part 2 trial.

#### 2.2.5 Results output

Results are saved as `participant_<p_id>_task2_set<set_num>.csv` in the `output` folder. One row per trial:

| Column | Description |
|---|---|
| `participant_id` | Value passed via `--p_id` |
| `part` | 1 or 2 |
| `trial_num` | Trial number within the part |
| `condition` | congruent or incongruent |
| `sentence_a`, `sentence_b` | Sentence text (Part 1 only) |
| `trial_word` | The target word (Part 2 only) |
| `chosen_answer` | Typed answer, 'geen betekenis', or selected option text |
| `is_correct` | True or False (Part 2 only) |
| `confidence` | Confidence rating (1 to 4, Part 2 only) |

---

## 3. Project layout and configuration

### 3.1 Project structure

```
.
├── run_task1.py                 Task 1 entry point
├── run_task2.py                 Task 2 entry point
├── system_config.yaml           Monitor, window, color, and shared text settings
├── config_task1_set1.yaml       Task 1 stimuli and trial definitions for Set 1
├── config_task1_set2.yaml       Task 1 stimuli and trial definitions for Set 2
├── config_task2_set1.yaml       Task 2 stimuli and trial definitions for Set 1
├── config_task2_set2.yaml       Task 2 stimuli and trial definitions for Set 2
├── screens/
│   ├── task1/
│   │   ├── audio_player.py      Primary audio exposure screen (with seek bar)
│   │   └── audio_mcq.py         Part 1 and Part 2 MCQ trial screens
│   ├── task2/
│   │   ├── exposure.py          Part 1 sentence screen with play buttons
│   │   └── testing.py           Part 2 word meaning MCQ screen
│   └── utils/
│       ├── instructions.py      Generic instruction screen (advances on SPACE)
│       ├── rating.py            Confidence rating screen (1 to 4 scale)
│       ├── fixation.py          Fixation cross screen
│       └── task2_utils.py       Trial extraction and constrained shuffling helpers
└── stimuli/
    ├── task1/
    │   ├── set1/                Audio files for Task 1, Set 1
    │   └── set2/                Audio files for Task 1, Set 2
    └── task2/
        ├── set1/                Audio files for Task 2, Set 1
        └── set2/                Audio files for Task 2, Set 2
```

### 3.2 What each module does

- **`run_task1.py`** / **`run_task2.py`**: load the relevant config files, set up the monitor and window, collect the participant ID via `--p_id`, and run all screens in order. Results are collected as a list of dicts and saved as a CSV at the end.
- **`system_config.yaml`**: holds machine-level settings shared by both tasks, monitor dimensions, viewing distance, window units, colors, and exit/rating instruction text.
- **`config_task{n}_set{m}.yaml`**: holds all stimulus paths, trial definitions, instruction texts, and correct answers for a given task and stimulus set.
- **`audio_player.py`**: shows a seekable audio player with a progress bar and play/pause toggle. The participant must play the audio at least once before continuing.
- **`audio_mcq.py`**: contains `run_audio_mcq_part1` for standard MCQ trials (options only) and `run_audio_mcq_part2` for completion trials (reference audio shown at the top, options below). Options are shuffled on every trial, the participant must play all options before confirming, and a checkbox is used for single selection.
- **`exposure.py`**: shows two sentences with individual play buttons, a text input box, and a 'geen betekenis' button.
- **`testing.py`**: plays the target word, then reveals three shuffled text answer options once the word has been played.
- **`rating.py`**: shows a 1 to 4 confidence scale. Participant presses a number key to select, then Enter to confirm.
- **`instructions.py`**: displays any block of text and waits for SPACE.
- **`task2_utils.py`**: pulls trials out of the config and tags them by condition (`extract_trials`, `extract_part2_trials`), then interleaves two trial pools into a single pseudorandom sequence with no more than `max_consecutive` trials from the same condition in a row (`build_constrained_trial_sequence`).

### 3.3 Configuration

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

rating_instruction: 'Hoe zeker ben je van je keuze? ...'

task_1:
  exit_instruction: '...'
  test_trials_part_1: 1
  test_trials_part_2: 1

task_2:
  exit_instruction: '...'
  test_trials_part_1: 1
  test_trials_part_2: 1
```

Task-level settings live in `config_task1_set{n}.yaml` and `config_task2_set{n}.yaml`. For Task 1, each trial specifies its audio paths and which index is the correct answer (always 0 before shuffling):

```yaml
stimuli:
  welcome_text: 'In dit deel van het experiment ...'
  test_text: 'Je wordt nu gevraagd ...'

  part_1:
    n_trials: 34
    primary_audio: 'stimuli/task1/set1/audio_set1.wav'
    trial_1:
      correct: 0
      audio_paths: [stimuli/task1/set1/set1_words1.wav, ...]
```

For Task 2, Part 1 trials hold two sentences with their own audio, and Part 2 trials hold a target word and its answer options:

```yaml
part_1:
  instruction: 'In deze taak lees en hoor je ...'
  geen_betekenis_label: 'geen betekenis'

  congruent:
    n_trials: 10
    trial_1:
      sentence_a: 'Van het harde geluid schrok de jopes'
      sentence_a_audio: 'stimuli/task2/set1/sentence1a.wav'
      sentence_b: 'De moeder is bevallen van een nieuwe jopes'
      sentence_b_audio: 'stimuli/task2/set1/sentence1b.wav'

  incongruent:
    n_trials: 10
    trial_11:
      sentence_a: '...'
      sentence_a_audio: '...'
      sentence_b: '...'
      sentence_b_audio: '...'

part_2:
  instruction: 'Nu word je gevraagd naar de betekenissen ...'
  n_trials: 20
  trial_1:
    word: jopes
    audio_word: 'stimuli/task2/set1/jopes.wav'
    correct_answer: baby
    incorrect_answer1: auto
    incorrect_answer2: geen betekenis
```

---

## 4. Installation and usage

### 4.1 Clone the repository

```bash
git clone https://github.com/ShekharNarayanan/language_task_psychopy.git
cd language_task_psychopy
```

### 4.2 Install dependencies

This project uses [uv](https://docs.astral.sh/uv/) for environment and dependency management with Python 3.10.

```bash
uv venv
uv sync
.venv\Scripts\activate
```

Main dependencies:

- `psychopy` for experiment infrastructure
- `sounddevice` and `pygame` as audio backends
- `pyyaml` for loading config files
- `pandas` for results output

### 4.3 Run the experiment

```bash
python -m run_task1 --p_id 1 --set_num 1 --test_run True
```

```bash
python -m run_task2 --p_id 1 --set_num 1 --test_run True
```

- `--p_id`: participant identifier, used to name the results CSV
- `--set_num`: which stimulus set to load (1 or 2)
- `--test_run`: set to `True` for one trial per part, `False` for all trials

Press **Escape** or **Q** at any point to quit the experiment.