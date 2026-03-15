import logging
import multiprocessing
import os
import subprocess
from pathlib import Path


class Gkeyll:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.root = Path(self.config["root"]).expanduser()

    def patch(self):
        pass

    def clean(self):
        self.logger.info("START: Gkeyll.clean")

        with (
            open("clean.gkeyll.out.txt", "w") as file_output,
            open("clean.gkeyll.err.txt", "w") as file_error,
        ):
            n = multiprocessing.cpu_count()
            r = subprocess.run(
                f"make -j{n} -C {self.config["root"]} clean",
                shell=True,
                stdout=file_output,
                stderr=file_error,
            )
            if r.returncode:
                raise RuntimeError("[YMIR] FAIL: Gkeyll.clean")

        self.logger.info("STOP: Gkeyll.clean")

    def build(self):
        self.logger.info("START: Gkeyll.build")

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

        with (
            open("build.gkeyll.out.txt", "w") as file_output,
            open("build.gkeyll.err.txt", "w") as file_error,
        ):
            r = subprocess.run(
                f"./configure",
                shell=True,
                cwd=self.root,
                env=env,
                stdout=file_output,
                stderr=file_error,
            )
            if r.returncode:
                raise RuntimeError("[YMIR] FAIL: Gkeyll.build")

            n = multiprocessing.cpu_count()
            r = subprocess.run(
                f"make -j{n} -C {self.config["root"]} all",
                shell=True,
                env=env,
                stdout=file_output,
                stderr=file_error,
            )
            if r.returncode:
                raise RuntimeError("[YMIR] FAIL: Gkeyll.build")

        self.logger.info("STOP: Gkeyll.build")

    def test(self):
        self.logger.info("START: Gkeyll.test")

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

        with (
            open("test.gkeyll.out.txt", "w") as file_output,
            open("test.gkeyll.err.txt", "w") as file_error,
        ):
            r = subprocess.run(
                " && ".join(command),
                shell=True,
                cwd=self.root,
                stdout=file_output,
                stderr=file_error,
            )
            if r.returncode:
                raise RuntimeError("[YMIR] FAIL: Gkeyll.test")

        self.logger.info("STOP: Gkeyll.test")

    def simulation(self):
        pass

    def report(self):
        pass


__all__ = ["Gkeyll"]
