import logging
import multiprocessing
import os
import subprocess
from pathlib import Path
from .tool import dispatch_process, check_patch, apply_patch


class Hermes3:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.root = Path(self.config["root"]).expanduser()

    def patch(self, tag):
        self.logger.info(f"START: Hermes3.patch ({tag})")

        if tag == "build.python":
            with (
                open("patch.hermes3.out.txt", "wb") as file_output,
                open("patch.hermes3.err.txt", "wb") as file_error,
            ):
                file_target = self.root / "CMakeLists.txt"
                if not check_patch(file_target, "eda7acae"):
                    file_error.write(b"Invalid target hash. Stop.")
                    return

                process = apply_patch(
                    "hermes3.build.python",
                    self.root,
                    file_output,
                    file_error,
                )

                process.wait()
                if process.returncode:
                    raise RuntimeError("[YMIR] FAIL: Hermes3.patch")
        else:
            file_error.write(b"Invalid tag. Stop.")
            raise RuntimeError("[YMIR] FAIL: Hermes3.patch")

        self.logger.info(f"STOP: Hermes3.patch ({tag})")

    def clean(self):
        self.logger.info("START: Hermes3.clean")

        # restore source files
        target = "CMakeLists.txt"
        r = subprocess.run(
            f"git restore {target}",
            shell=True,
            cwd=self.root,
        )
        if r.returncode:
            raise RuntimeError("[YMIR] FAIL: Hermes3.clean")

        # remove build
        with (
            open("clean.hermes3.out.txt", "wb") as file_output,
            open("clean.hermes3.err.txt", "wb") as file_error,
        ):
            exe = self.find_build_exe()
            process = subprocess.Popen(
                f"{exe} -C {self.root}/build clean",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            dispatch_process(process, file_output, file_error)

            process.wait()
            if process.returncode:
                raise RuntimeError("[YMIR] FAIL: Hermes3.clean")

        self.logger.info("STOP: Hermes3.clean")

    def build(self):
        self.logger.info("START: Hermes3.build")

        self.patch("build.python")

        env = os.environ.copy()

        compiler = {
            "cpp": self.config["toolchain"]["cpp"]["compiler"],
        }
        prefix = Path(self.config["install"]["prefix"]).expanduser()

        with (
            open("build.hermes3.out.txt", "wb") as file_output,
            open("build.hermes3.err.txt", "wb") as file_error,
        ):
            flag_generator = ""
            if self.config["toolchain"]["cmake"]["generator"] == "ninja":
                flag_generator = "-GNinja"

            option = " ".join(
                [
                    "-S .",
                    "-B build",
                    flag_generator,
                    f"-DCMAKE_CXX_COMPILER={compiler["cpp"]}",
                    f"-DCMAKE_INSTALL_PREFIX={prefix}",
                    "-DBOUT_DOWNLOAD_SUNDIALS=ON",
                ]
            )
            process = subprocess.Popen(
                f"cmake {option}",
                shell=True,
                cwd=self.root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            dispatch_process(process, file_output, file_error)

            process.wait()
            if process.returncode:
                raise RuntimeError("[YMIR] FAIL: Hermes3.build")

            exe = self.find_build_exe()
            target = " ".join(["all", "install"])
            process = subprocess.Popen(
                f"{exe} -C {self.root}/build {target}",
                shell=True,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            dispatch_process(process, file_output, file_error)

            process.wait()
            if process.returncode:
                raise RuntimeError("[YMIR] FAIL: Hermes3.build")

        self.logger.info("STOP: Hermes3.build")

    def test(self):
        self.logger.info("START: Hermes3.test")

        with (
            open("test.hermes3.out.txt", "wb") as file_output,
            open("test.hermes3.err.txt", "wb") as file_error,
        ):
            process = subprocess.Popen(
                "ctest --test-dir build || true",
                shell=True,
                cwd=self.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            dispatch_process(process, file_output, file_error)

            process.wait()
            if process.returncode:
                raise RuntimeError("[YMIR] FAIL: Hermes3.test")

        self.logger.info("STOP: Hermes3.test")

    def sim(self, name):
        pass

    def report(self):
        pass

    def find_build_exe(self):
        n = multiprocessing.cpu_count()
        exe = f"make -j{n}"
        if self.config["toolchain"]["cmake"]["generator"] == "ninja":
            exe = "ninja"

        return exe


__all__ = ["Hermes3"]
