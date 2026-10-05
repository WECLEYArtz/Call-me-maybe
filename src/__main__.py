from json import JSONDecodeError
from src.parser import (
    args_parser,
    parse_inputs,
    FunctionCallingParserError,
    Paths,
)
import sys

# TODO: remove nested import later


def main() -> None:
    """
    Main function for the whole pipline.
    ...
    """
    paths: Paths = args_parser()
    prompts_list = parse_inputs(paths.input)


if __name__ == "__main__":
    RED = "\033[31m"
    RESET = "\033[0m"
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(RED + "program Forcefully stopped, exiting..." + RESET)
    except FunctionCallingParserError as e:
        sys.exit(RED + str(e) + RESET)
    except Exception as e:
        sys.exit(RED + f"[{e.__class__.__name__}]: " + str(e) + RESET)
