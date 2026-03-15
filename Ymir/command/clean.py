def main(arg):
    for key, config in arg.config.backend.items():
        if config["use"]:
            config["stage"].clean()


__all__ = ["main"]
