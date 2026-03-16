import logging
import multiprocessing
import os
import subprocess
from pathlib import Path
from .tool import dispatch_process, check_patch, apply_patch


class GACODE:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.root = Path(self.config["root"]).expanduser()

        self.logger.info("Backend `gacode` initialized")

    def patch(self, tag):
        self.logger.info(f"START: GACODE.patch ({tag})")

        with (
            open("patch.gacode.out.txt", "wb") as file_output,
            open("patch.gacode.err.txt", "wb") as file_error,
        ):
            if tag == "build.gyro":
                process = apply_patch(
                    "gacode.build.gyro",
                    self.root,
                    file_output,
                    file_error,
                )
                process.wait()
                if process.returncode:
                    self.logger.warning(f"Patch `{tag}` not applied")
                    raise RuntimeError("[YMIR] FAIL: GACODE.patch")
            elif tag == "build.fftw":
                file_target = self.root / "platform/build/make.inc.GFORTRAN_OSX_BREW"
                if not check_patch(file_target, "78755cae"):
                    self.logger.warning(f"Patch `{tag}` not applied")
                    file_error.write(b"Invalid target hash. Stop.")
                    return

                process = apply_patch(
                    "gacode.build.fftw",
                    self.root,
                    file_output,
                    file_error,
                )
                process.wait()
                if process.returncode:
                    self.logger.warning(f"Patch `{tag}` not applied")
                    raise RuntimeError("[YMIR] FAIL: GACODE.patch")
            elif tag == "build.mpich":
                file_target = self.root / "platform/exec/exec.GFORTRAN_OSX_BREW"
                if not check_patch(file_target, "7f4520a2"):
                    self.logger.warning(f"Patch `{tag}` not applied")
                    file_error.write(b"Invalid target hash. Stop.")
                    return

                process = apply_patch(
                    "gacode.build.mpich",
                    self.root,
                    file_output,
                    file_error,
                )
                process.wait()
                if process.returncode:
                    self.logger.warning(f"Patch `{tag}` not applied")
                    raise RuntimeError("[YMIR] FAIL: GACODE.patch")

            else:
                self.logger.error("Invalid tag")
                file_error.write(b"Invalid tag. Stop.")
                raise RuntimeError("[YMIR] FAIL: GACODE.patch")

            self.logger.info(f"Patch `{tag}` applied")

        self.logger.info(f"STOP: GACODE.patch ({tag})")

    def clean(self):
        self.logger.info("START: GACODE.clean")

        # restore source files
        target_list = [
            "platform/build/make.inc.GFORTRAN_OSX_BREW",
            "platform/exec/exec.GFORTRAN_OSX_BREW",
        ]
        for target in target_list:
            r = subprocess.run(
                f"git restore {target}",
                shell=True,
                cwd=self.root,
            )
            if r.returncode:
                self.logger.error(f"Target {target} not restored")
                raise RuntimeError("[YMIR] FAIL: Gkeyll.clean")

            self.logger.info(f"Target {target} restored")

        # remove untracked files
        r = subprocess.run(
            f"git clean -f",
            shell=True,
            cwd=self.root,
        )
        if r.returncode:
            self.logger.error(f"Untracked files are not removed")
            raise RuntimeError("[YMIR] FAIL: Gkeyll.clean")

        env = self.setup_env()

        # remove build
        with (
            open("clean.gacode.out.txt", "wb") as file_output,
            open("clean.gacode.err.txt", "wb") as file_error,
        ):
            n = multiprocessing.cpu_count()
            process = subprocess.Popen(
                f"make -j{n} -C {self.root} clean",
                shell=True,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            dispatch_process(process, file_output, file_error)
            process.wait()
            if process.returncode:
                self.logger.error("Stage `clean` failed")
                raise RuntimeError("[YMIR] FAIL: GACODE.clean")

        self.logger.info("STOP: GACODE.clean")

    def build(self):
        self.logger.info("START: GACODE.build")

        env = self.setup_env()

        if env["GACODE_PLATFORM"] == "GFORTRAN_OSX_BREW":
            self.patch("build.gyro")
            self.patch("build.fftw")

        if self.config["toolchain"]["mpi"]["type"] == "mpich":
            self.patch("build.mpich")

        with (
            open("build.gacode.out.txt", "wb") as file_output,
            open("build.gacode.err.txt", "wb") as file_error,
        ):
            # build
            for target in ("", "le3", "gyro"):
                process = subprocess.Popen(
                    f"make -j1 -C {self.root / target} all",
                    shell=True,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                dispatch_process(process, file_output, file_error)
                process.wait()
                if process.returncode:
                    self.logger.error("Stage `build.build` failed")
                    raise RuntimeError("[YMIR] FAIL: GACODE.build")

        self.logger.info("STOP: GACODE.build")

    def test(self):
        self.logger.info("START: GACODE.test")

        env = self.setup_env()

        command = [
            "tglf -n 4 -r",
            "neo -n 4 -nomp 2 -r",
            "cgyro -n 4 -nomp 2 -r",
            "gyro -n 4 -nomp 2 -r",
            "tgyro -n 4 -nomp 2 -r",
        ]
        command = [f"echo && {c} || true" for c in command]
        command = " && ".join(command)

        with (
            open("test.gacode.out.txt", "wb") as file_output,
            open("test.gacode.err.txt", "wb") as file_error,
        ):
            process = subprocess.Popen(
                command,
                shell=True,
                env=env,
                cwd=self.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            dispatch_process(process, file_output, file_error)
            process.wait()
            if process.returncode:
                self.logger.error("Stage `test` failed")
                raise RuntimeError("[YMIR] FAIL: GACODE.test")

        self.logger.info("STOP: GACODE.test")

    def sim(self, sim_config):
        self.logger.info(f"START: GACODE.sim ({sim_config["name"]})")

        self.logger.info(f"STOP: GACODE.sim ({sim_config["name"]})")

    def report(self):
        self.logger.info("START: GACODE.report")

        self.logger.info("STOP: GACODE.report")

    def setup_env(self):
        env = os.environ.copy()
        env["GACODE_ROOT"] = str(self.root)
        for key, value in self.config["env"].items():
            env[key] = value

        for module in (
            "tgyro",
            "gyro",
            "cgyro",
            "xgyro",
            "neo",
            "vgen",
            "tglf",
            "le3",
            "profiles_gen",
            "shared",
            "qlgyro",
        ):
            env["PATH"] = f"{env['GACODE_ROOT']}/{module}/bin:{env['PATH']}"

        for module in ("f2py", "f2py/pygacode"):
            env["PYTHONPATH"] = f"{env['GACODE_ROOT']}/{module}:{env['PATH']}"

        return env
