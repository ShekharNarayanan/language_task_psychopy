"""Mirror task output, including native-library messages, to a per-run log."""

import codecs
import os
from pathlib import Path
import subprocess
import sys


_OUTPUT_ENV = 'LANGUAGE_TASK_LOGGED_OUTPUT'


def log_task_console(output_path):
    """Run the task in a child with captured stdout/stderr; return its CSV path.

    The launcher copies the child's combined output to the console and log.
    Only the child returns from this function, before importing task libraries.
    Sharing the CSV path keeps its timestamp identical to the log's timestamp.
    """
    inherited_path = os.environ.pop(_OUTPUT_ENV, None)
    if inherited_path is not None:
        return Path(inherited_path)

    output_path = Path(output_path).resolve()
    log_path = output_path.parent.parent / 'logs' / output_path.with_suffix('.log').name
    log_path.parent.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment[_OUTPUT_ENV] = str(output_path)
    environment['PYTHONIOENCODING'] = 'utf-8'
    environment['PYTHONUNBUFFERED'] = '1'

    # Preserve script/module invocation and interpreter flags. Pipes capture
    # native writes as well as print(), warnings, logging, and tracebacks.
    command = [sys.executable, *sys.orig_argv[1:]]
    decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
    console = getattr(sys.stdout, 'buffer', None)
    with log_path.open('wb') as log_file:
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=environment,
        ) as process:
            while True:
                try:
                    chunk = process.stdout.read1(8192)
                    if not chunk:
                        break
                    log_file.write(chunk)
                    log_file.flush()
                    if console is not None:
                        console.write(chunk)
                        console.flush()
                    else:
                        sys.stdout.write(decoder.decode(chunk))
                        sys.stdout.flush()
                except KeyboardInterrupt:
                    # Ctrl+C also reaches the child. Keep draining its output
                    # so its traceback and shutdown messages reach the log.
                    continue
            if console is None:
                sys.stdout.write(decoder.decode(b'', final=True))
                sys.stdout.flush()
            return_code = process.wait()
    raise SystemExit(return_code)
