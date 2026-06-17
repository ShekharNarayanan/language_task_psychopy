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
        Shuffled list of trial dicts, each with 'condition', 'sentence_a',
        'sentence_a_audio', 'sentence_b', 'sentence_b_audio'.
    """
    trials = []
    for key, data in cfg_part[condition_key].items():
        if not key.startswith('trial_'):
            continue
        trials.append({
            'condition':        condition_label,
            'sentence_a':       data['sentence_a'],
            'sentence_a_audio': data['sentence_a_audio'],
            'sentence_b':       data['sentence_b'],
            'sentence_b_audio': data['sentence_b_audio'],
        })
    random.shuffle(trials)
    return trials


def build_constrained_trial_sequence(pool_a, pool_b, max_consecutive=2):
    """
    Merge two trial pools into a single pseudorandom sequence where no
    condition appears more than max_consecutive times in a row.

    Each pool is consumed one trial at a time. At each step the algorithm
    picks randomly from whichever conditions are still allowed. If the last
    max_consecutive trials were all from the same condition, the other
    condition is forced next, unless that pool is empty, in which case the
    constraint is relaxed for that step.

    The condition labels are read directly from the trial dicts, so this
    works for any pair of pools regardless of what their 'condition' values
    are (e.g. congruent/incongruent, or real_word/geen_betekenis).

    Args:
        pool_a:           List of trial dicts for the first condition (pre-shuffled).
        pool_b:           List of trial dicts for the second condition (pre-shuffled).
        max_consecutive:  Maximum allowed consecutive trials from one condition.

    Returns:
        Ordered list of trial dicts ready to iterate over in the trial loop.
    """
    if not pool_a and not pool_b:
        return []

    label_a = pool_a[0]['condition'] if pool_a else pool_b[0]['condition'] + '_other'
    label_b = pool_b[0]['condition'] if pool_b else pool_a[0]['condition'] + '_other'

    pools  = {label_a: pool_a, label_b: pool_b}
    result = []

    while any(pools.values()):

        # Look at the last N conditions we placed
        last_conditions = [t['condition'] for t in result[-max_consecutive:]]

        # If they are all the same condition, we should switch to the other one
        last_n_same_condition = (
            len(last_conditions) == max_consecutive and
            len(set(last_conditions)) == 1
        )

        if last_n_same_condition:
            other_label = label_b if last_conditions[0] == label_a else label_a
            if pools[other_label]:
                # The other pool still has trials, so force the switch
                allowed_conditions = [other_label]
            else:
                # The other pool is empty, relax the constraint for this step
                allowed_conditions = [c for c in pools if pools[c]]
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
            'word':              data['word'],
            'audio_word':        data['audio_word'],
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