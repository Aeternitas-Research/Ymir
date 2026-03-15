import multiprocessing
import os
import subprocess
from pathlib import Path


class Gkeyll:
    def __init__(self, config):
        self.config = config
        self.root = Path(self.config["root"]).expanduser()

    def patch(self):
        pass

    def clean(self):
        pass

    def build(self):
        SUPERLU_INC_DIR = subprocess.run(
            "pkg-config --cflags-only-I superlu",
            capture_output=True,
            shell=True,
            text=True,
        ).stdout.strip()[2:]
        SUPERLU_LIB_DIR = subprocess.run(
            "pkg-config --libs-only-L superlu",
            capture_output=True,
            shell=True,
            text=True,
        ).stdout.strip()[2:]

        env = os.environ.copy()
        env["SUPERLU_INC_DIR"] = SUPERLU_INC_DIR
        env["SUPERLU_LIB_DIR"] = SUPERLU_LIB_DIR

        r = subprocess.run(
            f"./configure",
            shell=True,
            cwd=self.root,
            env=env,
        )
        if r.returncode:
            raise RuntimeError("[YMIR] FAIL: Gkeyll.build")

        n = multiprocessing.cpu_count()
        r = subprocess.run(
            f"make -j{n} -C {self.config["root"]} all", shell=True, env=env
        )
        if r.returncode:
            raise RuntimeError("[YMIR] FAIL: Gkeyll.build")

        print("[YMIR] DONE: Gkeyll.build")

    def test(self):
        pass

    def simulation(self):
        pass

    def report(self):
        pass


__all__ = ["Gkeyll"]
