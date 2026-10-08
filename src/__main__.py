import sys
import os

import json

from .parsing.arg_parsing import args_parser, Paths
from .parsing.input_parsing import parse_inputs, Prompt
from .parsing.function_definition_parsing import FuncDef, parse_func_def
from .errors import FunctionCallingParserError
from .feed_prompt import generate_prompt_initialiser
from .slm_comunication import get_slm_answers


def main() -> None:
    """Parse inputs, generate function calls, and save the results.

    Returns:
        None.
    """
    paths: Paths = args_parser()
    os.makedirs(os.path.dirname(paths.output), exist_ok=True)

    function_defs: list[FuncDef] = parse_func_def(paths.fun_def)
    prompts_list: list[Prompt] = parse_inputs(paths.input)
    init_prompt: str = generate_prompt_initialiser(function_defs)

    entries: list[dict] = get_slm_answers(
        prompts_list, function_defs, init_prompt
    )

    with open(paths.output, "w") as f:
        json.dump([e for e in entries], f, indent=4)


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
