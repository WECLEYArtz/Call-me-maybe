import argparse


class Paths:
    def __init__(
        self,
        fun_def: str = "data/input/functions_definition.json",
        input: str = "data/input/function_calling_tests.json",
        output: str = "data/output/function_calls.json",
    ):
        self.fun_def: str = fun_def
        self.input: str = input
        self.output: str = output


def args_parser() -> Paths:
    paths = Paths()
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("--functions_definition", default=paths.fun_def)
    _ = parser.add_argument("--input", default=paths.input)
    _ = parser.add_argument("--output", default=paths.output)
    args = parser.parse_args()

    return Paths(
        args.functions_definition,
        args.input,
        args.output,
    )
