import logging


class Simulation:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config

        self.logger.info("Simulation `gkeyll` initialized")

    def start(self):
        self.logger.info("START: Simulation:gkeyll")

        self.logger.info("STOP: Simulation:gkeyll")


__all__ = ["Simulation"]
