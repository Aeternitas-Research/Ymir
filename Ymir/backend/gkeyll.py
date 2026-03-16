import logging
import multiprocessing
import os
import subprocess
from pathlib import Path
from .tool import dispatch_process, check_patch, apply_patch


class Gkeyll:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.root = Path(self.config["root"]).expanduser()

    def patch(self, tag):
        self.logger.info(f"START: Gkeyll.patch ({tag})")

        if tag == "build.mpich":
            with (
                open("patch.gkeyll.out.txt", "wb") as file_output,
                open("patch.gkeyll.err.txt", "wb") as file_error,
            ):
                file_target = self.root / "gkeyll/lua/Comm/gkyl_mpi_macros.h"
                if not check_patch(file_target, "470ea4518"):
                    file_error.write(b"Invalid target hash. Stop.")
                    return

                process = apply_patch(
                    "gkeyll.build.mpich",
                    self.root,
                    file_output,
                    file_error,
                )

                process.wait()
                if process.returncode:
                    raise RuntimeError("[YMIR] FAIL: Gkeyll.patch")
        else:
            file_error.write(b"Invalid tag. Stop.")
            raise RuntimeError("[YMIR] FAIL: Gkeyll.patch")

        self.logger.info(f"STOP: Gkeyll.patch ({tag})")

    def clean(self):
        self.logger.info("START: Gkeyll.clean")

        # restore source files
        target = "gkeyll/lua/Comm/gkyl_mpi_macros.h"
        r = subprocess.run(
            f"git restore {target}",
            shell=True,
            cwd=self.root,
        )
        if r.returncode:
            raise RuntimeError("[YMIR] FAIL: Gkeyll.clean")

        # remove build
        with (
            open("clean.gkeyll.out.txt", "wb") as file_output,
            open("clean.gkeyll.err.txt", "wb") as file_error,
        ):
            n = multiprocessing.cpu_count()
            process = subprocess.Popen(
                f"make -j{n} -C {self.root} clean",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            dispatch_process(process, file_output, file_error)

            process.wait()
            if process.returncode:
                raise RuntimeError("[YMIR] FAIL: Gkeyll.clean")

        self.logger.info("STOP: Gkeyll.clean")

    def build(self):
        self.logger.info("START: Gkeyll.build")

        # MPI
        mpi_command = (
            subprocess.run(
                "mpicc -show",
                capture_output=True,
                shell=True,
                text=True,
            )
            .stdout.strip()
            .split(" ")
        )
        CONF_MPI_INC_DIR = [s for s in mpi_command if s[:2] == "-I"][0][2:]
        CONF_MPI_LIB_DIR = [s for s in mpi_command if s[:2] == "-L"][0][2:]

        if "mpich" in CONF_MPI_LIB_DIR:
            self.patch("build.mpich")

        # Lua
        CONF_LUA_INC_DIR = subprocess.run(
            "pkg-config --cflags-only-I luajit",
            capture_output=True,
            shell=True,
            text=True,
        ).stdout.strip()[2:]
        CONF_LUA_LIB_DIR = subprocess.run(
            "pkg-config --libs-only-L luajit",
            capture_output=True,
            shell=True,
            text=True,
        ).stdout.strip()[2:]

        # SuperLU
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

        prefix = self.root / "build/gkylsoft"

        with (
            open("build.gkeyll.out.txt", "wb") as file_output,
            open("build.gkeyll.err.txt", "wb") as file_error,
        ):
            option = [
                f"--prefix={prefix}",
                "--use-mpi=yes",
                f"--mpi-inc={CONF_MPI_INC_DIR}",
                f"--mpi-lib={CONF_MPI_LIB_DIR}",
                "--use-lua=yes",
                f"--lua-inc={CONF_LUA_INC_DIR}",
                f"--lua-lib={CONF_LUA_LIB_DIR}",
            ]
            process = subprocess.Popen(
                f"./configure {' '.join(option)}",
                shell=True,
                cwd=self.root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            dispatch_process(process, file_output, file_error)

            process.wait()
            if process.returncode:
                raise RuntimeError("[YMIR] FAIL: Gkeyll.build")

            n = multiprocessing.cpu_count()
            process = subprocess.Popen(
                f"make -j{n} -C {self.root} everything",
                shell=True,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            dispatch_process(process, file_output, file_error)

            process.wait()
            if process.returncode:
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
            open("test.gkeyll.out.txt", "wb") as file_output,
            open("test.gkeyll.err.txt", "wb") as file_error,
        ):
            process = subprocess.Popen(
                " && ".join(command),
                shell=True,
                cwd=self.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            dispatch_process(process, file_output, file_error)

            process.wait()
            if process.returncode:
                raise RuntimeError("[YMIR] FAIL: Gkeyll.test")

        self.logger.info("STOP: Gkeyll.test")

    def sim(self, name):
        pass

    def report(self):
        pass


__all__ = ["Gkeyll"]
