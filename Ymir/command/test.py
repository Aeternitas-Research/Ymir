def main(arg):
    for key, config in arg.config.backend.items():
        if config["use"]:
            config["backend"].test()


__all__ = ["main"]
