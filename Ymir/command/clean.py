def main(arg):
    for key, config in arg.config.backend.items():
        if config["use"]:
            config["backend"].clean()


__all__ = ["main"]
