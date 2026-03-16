import logging


def main(arg):
    logger = logging.getLogger(__name__)

    key, case = arg.name.split(".")
    if arg.config.backend[key]["use"]:
        arg.config.backend[key]["stage"].sim(case)
    else:
        logger.error("Backend is not available")
        raise RuntimeError("[YMIR] FAIL: command.sim")


__all__ = ["main"]
