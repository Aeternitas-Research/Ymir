import logging


class Simulation:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config

        self.logger.info("Simulation `gacode` initialized")

    def start(self):
        self.logger.info("START: Simulation:gacode")

        self.logger.info("STOP: Simulation:gacode")


__all__ = ["Simulation"]
