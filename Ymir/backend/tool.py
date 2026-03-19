import sys
import subprocess
from pathlib import Path
import threading


def tee(stream, file):
    for line in stream:
        sys.stdout.buffer.write(line)
        sys.stdout.buffer.flush()
        file.write(line)
    file.flush()


def dispatch_process(process, output, error):
    thread = [
        threading.Thread(
            target=tee,
            args=(process.stdout, output),
        ),
        threading.Thread(
            target=tee,
            args=(process.stderr, error),
        ),
    ]
    for t in thread:
        t.start()
    for t in thread:
        t.join()


def check_patch(target, target_hash):
    git_hash = subprocess.run(
        f"git hash-object -- {target}",
        capture_output=True,
        shell=True,
        text=True,
    ).stdout.strip()
    n = len(target_hash)

    return git_hash[:n] == target_hash


def apply_patch(handle, root, output, error):
    file = Path(__file__).parent / "patch" / f"{handle}.patch"

    process = subprocess.Popen(
        f"git apply {file}",
        shell=True,
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    dispatch_process(process, output, error)

    return process


__all__ = ["dispatch_process", "check_patch", "apply_patch"]
