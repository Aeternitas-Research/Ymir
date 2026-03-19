import logging


class Simulation:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config

        self.logger.info("Simulation `hermes3` initialized")

    def start(self):
        self.logger.info("START: Simulation:hermes3")

        self.logger.info("STOP: Simulation:hermes3")


__all__ = ["Simulation"]
