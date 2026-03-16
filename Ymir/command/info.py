def main(arg):
    print(f"Input: {arg.input}")

    if not arg.verbose:
        return

    print("Backend:")
    for key, config in arg.config.backend.items():
        if config["use"]:
            print(f"  {key:>7}: {config["version"]}")


__all__ = ["main"]
