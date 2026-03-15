import logging
import argparse
from .config import Config
from .version import get_version


def main():
    parser = argparse.ArgumentParser(
        prog="ymir",
        description="",
        epilog="",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-i", "--input", help="set input file", default="ymir.toml")

    subparser = parser.add_subparsers(dest="command", help="commands")
    parser_info = subparser.add_parser("info", help="show general info")
    parser_build = subparser.add_parser("build", help="build backend")
    parser_test = subparser.add_parser("test", help="run tests")

    parser_info.add_argument(
        "-v", "--verbose", action="store_true", help="show verbose info"
    )

    arg = parser.parse_args()
    arg.config = Config(arg.input)

    logging.basicConfig(
        filename="ymir.log",
        format="%(asctime)s [%(levelname)s:%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )

    logger = logging.getLogger(__name__)
    logger.info("START: main")

    if not arg.command:
        parser.print_help()
    elif arg.command == "info":
        print(f"Ymir {get_version()}")

        from .command import info

        info.main(arg)
    elif arg.command == "build":
        from .command import build

        build.main(arg)
    elif arg.command == "test":
        from .command import test

        test.main(arg)

    logger.info("STOP: main")


__all__ = ["main"]
