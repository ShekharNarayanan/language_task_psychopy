"""Recover Task 2 randomization seeds from previous response files."""

import csv
from pathlib import Path
import re
import secrets


def load_or_create_seed(output_dir, participant_id, set_num, test_run):
    """Reuse the newest saved seed for this participant, set, and run mode."""
    suffix = '_test' if test_run else ''
    prefix = f'participant_{participant_id}_task2_set{set_num}{suffix}'
    pattern = re.compile(re.escape(prefix) + r'(?:_\d{8}_\d{6}_\d{6})?\.csv')
    output_dir = Path(output_dir)
    files = []
    if output_dir.exists():
        files = sorted(
            (path for path in output_dir.iterdir()
             if path.is_file() and pattern.fullmatch(path.name)),
            key=lambda path: (path.stat().st_mtime_ns, path.name), reverse=True,
        )

    for path in files:
        with path.open(newline='', encoding='utf-8-sig') as stream:
            rows = csv.DictReader(stream)
            if 'random_seed' not in (rows.fieldnames or []):
                continue
            values = {row['random_seed'] for row in rows if row.get('random_seed')}
        if not values:
            continue
        try:
            seeds = {int(value) for value in values}
        except ValueError as error:
            raise ValueError(f'Invalid random_seed in {path}') from error
        if len(seeds) != 1 or not 0 <= next(iter(seeds)) < 2**32:
            raise ValueError(f'Expected one consistent 32-bit random_seed in {path}')
        seed = seeds.pop()
        print(f'Task 2: restoring random seed {seed} from {path.name}')
        return seed

    seed = secrets.randbits(32)
    if files:
        print('Task 2: previous data has no saved random seed; '
              'the previous stimulus order cannot be restored.')
    print(f'Task 2: using new random seed {seed}')
    return seed
