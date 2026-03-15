import copy
import subprocess
import tomllib
from pathlib import Path

BACKEND = (
    "gkeyll",
    "hermes3",
)


def find_git_version(root):
    git_hash = subprocess.run(
        "git log --pretty=format:'%H' -n 1",
        capture_output=True,
        shell=True,
        cwd=root.expanduser(),
        text=True,
    ).stdout.strip()
    git_date = subprocess.run(
        "git show -s --format=%cd --date=short",
        capture_output=True,
        shell=True,
        cwd=root.expanduser(),
        text=True,
    ).stdout.strip()
    return git_hash, git_date


def find_version(handle, root):
    if handle == "gkeyll":
        git_hash, git_date = find_git_version(root)
        return f"{git_hash} [{git_date}]"
    else:
        return "unknown"


def get_backend(handle, config):
    if handle == "gkeyll":
        from .backend.gkeyll import Gkeyll

        return Gkeyll(config)
    else:
        return None


class Config:
    def __init__(self, file_name):
        with open(file_name, "rb") as file:
            self.raw = tomllib.load(file)

        backend_config = {
            "use": False,
            "root": "",
            "version": "",
            "stage": None,
        }
        self.backend = {key: copy.copy(backend_config) for key in BACKEND}

        for key, value in self.raw["backend"]["use"].items():
            if key in BACKEND:
                self.backend[key]["use"] = value
        for key, config in self.raw["backend"]["config"].items():
            if key in BACKEND:
                self.backend[key]["root"] = Path(config["root"])
                self.backend[key]["version"] = find_version(
                    key, self.backend[key]["root"]
                )
                self.backend[key]["stage"] = get_backend(key, config)


__all__ = ["Config"]
