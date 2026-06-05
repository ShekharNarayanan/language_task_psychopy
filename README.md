# Designing a behavioral experiment in Psychopy.

The repository contains python code for developing a language task based behavioral experiment. Made primarily using the PyschoPy library.

**Note: Under active development.**

## For returning users
1. Navigate to the project folder using the windows command line. You can open the windows cmd window by searching `cmd` in the windows search bar.
2. Once you have opened it, you can navigate to the folder for this project. You can use the example below and replace the path after `cd` with your own path.

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
1. `pid`        : the participant number for this current session. Can be any integer.
2. `set_num`    : the set for which the audio files have to be played. Can be 1 or 2.
3. `test_run`   : to run the test version of the experiment. If the flag is set to `True` you will get **one** trial for each part of the experiment. If set to `False`, you get all the trials of the experiment. You can change these in the `system_config.yaml` file.
