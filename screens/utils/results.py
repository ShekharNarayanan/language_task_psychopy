"""Save trial responses immediately using the existing pandas CSV format."""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd


class TrialResults:
    """Checkpoint responses and ratings without exposing a partially written CSV."""

    def __init__(self, output_path, *, index=True):
        self.output_path = Path(output_path)
        self.index = index
        self.rows = []

    def append(self, row):
        self.rows.append(dict(row))
        self._save()

    def update_last(self, **values):
        self.rows[-1].update(values)
        self._save()

    def _save(self):
        # Rebuild the small table so mixed-part columns and numeric formatting
        # match the original end-of-experiment DataFrame export.
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            with NamedTemporaryFile(
                mode='w', encoding='utf-8', newline='',
                dir=self.output_path.parent, prefix=self.output_path.name + '.',
                suffix='.tmp', delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                pd.DataFrame(self.rows).to_csv(temporary_file, index=self.index)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, self.output_path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
