def main(arg):
    for key, config in arg.config.backend.items():
        if config["use"]:
            config["stage"].build()


__all__ = ["main"]
