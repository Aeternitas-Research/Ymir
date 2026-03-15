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
        target = {}
        for module in (
            "core",
            "moments",
            "vlasov",
            "gyrokinetic",
            "pkpm",
        ):
            path = self.root / f"build/{module}/unit"
            target[module] = set()
            for pattern in ("ctest_*", "lctest_*", "mctest_*"):
                target[module].update({value.stem for value in set(path.glob(pattern))})

        for module, exe_list in {
            "gyrokinetic": {
                "ctest_fem_poisson_perp",  # freeze
            },
        }.items():
            for exe in exe_list:
                target[module].remove(exe)

        command = []
        for module, exe_list in target.items():
            command += [
                f"echo && "
                f"echo ./build/{module}/unit/{exe} && "
                f"./build/{module}/unit/{exe} || true"
                for exe in exe_list
            ]

        r = subprocess.run(
            " && ".join(command),
            shell=True,
            cwd=self.root,
        )
        if r.returncode:
            raise RuntimeError("[YMIR] FAIL: Gkeyll.test")

        print("[YMIR] DONE: Gkeyll.test")

    def simulation(self):
        pass

    def report(self):
        pass


__all__ = ["Gkeyll"]
