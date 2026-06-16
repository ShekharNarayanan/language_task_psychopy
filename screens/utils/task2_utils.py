"""
trial_utils.py
--------------
Helper functions for building and ordering trial sequences.
"""

import random


def extract_trials(cfg_part, condition_key, condition_label):
    """
    Pull all trials from one condition block in the config, tag each
    with its condition label, and shuffle the order randomly.

    Args:
        cfg_part:        The part_1 section of the config dict.
        condition_key:   Key in cfg_part to read from ('congruent' or 'incongruent').
        condition_label: String label to tag each trial with ('congruent' or 'incongruent').

    Returns:
        Shuffled list of trial dicts, each with 'condition', 'sentence_a', 'sentence_b'.
    """
    trials = []
    for key, data in cfg_part[condition_key].items():
        if not key.startswith('trial_'):
            continue
        trials.append({
            'condition':  condition_label,
            'sentence_a': data['sentence_a'],
            'sentence_b': data['sentence_b'],
        })
    random.shuffle(trials)
    return trials


def build_constrained_sequence(congruent_pool, incongruent_pool, max_consecutive=2):
    """
    Merge two trial pools into a single pseudorandom sequence where no
    condition appears more than max_consecutive times in a row.

    Each pool is consumed one trial at a time. At each step the algorithm
    picks randomly from whichever conditions are still allowed. If the last
    max_consecutive trials were all from the same condition, the other
    condition is forced next.

    Args:
        congruent_pool:   List of congruent trial dicts (pre-shuffled).
        incongruent_pool: List of incongruent trial dicts (pre-shuffled).
        max_consecutive:  Maximum allowed consecutive trials from one condition.

    Returns:
        Ordered list of trial dicts ready to iterate over in the trial loop.
    """
    pools  = {'congruent': congruent_pool, 'incongruent': incongruent_pool}
    result = []

    while any(pools.values()):

        # Look at the last N conditions we placed
        last_conditions = [t['condition'] for t in result[-max_consecutive:]]

        # If they are all the same condition, we must switch to the other one
        last_n_same_condition = (
            len(last_conditions) == max_consecutive and
            len(set(last_conditions)) == 1
        )

        if last_n_same_condition:
            forced_condition   = 'congruent' if last_conditions[0] == 'incongruent' else 'incongruent'
            allowed_conditions = [forced_condition]
        else:
            # Both conditions are allowed, pick randomly from whatever still has trials
            allowed_conditions = [c for c in pools if pools[c]]

        chosen_condition = random.choice(allowed_conditions)
        result.append(pools[chosen_condition].pop(0))

    return result


def extract_part2_trials(cfg_part2):
    """
    Pull all part 2 trials from the config, tag each with whether the
    correct answer is 'geen betekenis' or a real word, and shuffle each
    group independently.

    Args:
        cfg_part2: The part_2 section of the config dict.

    Returns:
        Two shuffled lists: (geen_betekenis_pool, real_word_pool), each
        containing trial dicts with all fields needed by run_task2_part2.
    """
    geen_betekenis_pool = []
    real_word_pool      = []

    for key, data in cfg_part2.items():
        if not key.startswith('trial_'):
            continue
        trial = {
            'condition':         'geen_betekenis' if data['correct_answer'] == 'geen betekenis' else 'real_word',
            'audio_word':        data['audio_word'],
            'sentence_a':        data['sentence_a'],
            'sentence_b':        data['sentence_b'],
            'correct_answer':    data['correct_answer'],
            'incorrect_answer1': data['incorrect_answer1'],
            'incorrect_answer2': data['incorrect_answer2'],
        }
        if trial['condition'] == 'geen_betekenis':
            geen_betekenis_pool.append(trial)
        else:
            real_word_pool.append(trial)

    random.shuffle(geen_betekenis_pool)
    random.shuffle(real_word_pool)
    return geen_betekenis_pool, real_word_pool