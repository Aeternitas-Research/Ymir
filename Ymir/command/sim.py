import logging


def main(arg):
    logger = logging.getLogger(__name__)

    key, case = arg.name.split(".")
    if not arg.config.backend[key]["use"]:
        logger.error("Backend is not available")
        raise RuntimeError("[YMIR] FAIL: command.sim")

    for case_config in arg.config.simulation["case"]:
        if (key, case) == (case_config["backend"], case_config["name"]):
            arg.config.backend[key]["stage"].sim(case_config)


__all__ = ["main"]
