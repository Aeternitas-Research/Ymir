import sys
import threading


def tee(stream, file):
    for line in stream:
        sys.stdout.buffer.write(line)
        sys.stdout.buffer.flush()
        file.write(line)
    file.flush()


def dispatch_process(process, output, error):
    thread = [
        threading.Thread(target=tee, args=(process.stdout, output)),
        threading.Thread(target=tee, args=(process.stderr, error)),
    ]
    for t in thread:
        t.start()
    for t in thread:
        t.join()


__all__ = ["dispatch_process"]
