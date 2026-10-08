import argparse


class Paths:
    """Store input, function-definition, and output paths."""

    def __init__(
        self,
        fun_def: str = "data/input/functions_definition.json",
        input: str = "data/input/function_calling_tests.json",
        output: str = "data/output/function_calling_results.json",
    ):
        """Initialize paths with defaults or custom values.

        Args:
            fun_def: Path to the function definitions JSON file.
            input: Path to the prompts JSON file.
            output: Path for the generated results JSON file.
        """
        self.fun_def: str = fun_def
        self.input: str = input
        self.output: str = output


def args_parser() -> Paths:
    """Parse command-line paths and return them as a ``Paths`` object.

    Returns:
        The paths selected through command-line arguments.
    """
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
