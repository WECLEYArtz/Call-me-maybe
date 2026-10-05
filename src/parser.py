import json
from pydantic import BaseModel, field_validator
import argparse


class FunctionCallingParserError(Exception):
    """Represent error when parsing function calling json file."""

    message: str = "Issue parsing function calling json file: "

    def __init__(self, detail: str):
        """Initialise error class.

        message: error message.
        """
        super().__init__(self.message + detail)


class Prompt(BaseModel):
    prompt: str

    @field_validator("prompt", mode="before")
    @classmethod
    def validate(cls, prompt_dict: dict[str, str]) -> str:
        if not "prompt" in prompt_dict:
            raise FunctionCallingParserError("Incorrect or missing prompt key")
        prompt = prompt_dict["prompt"]
        if not prompt.strip():
            raise FunctionCallingParserError("can't proccess textless prompt")
        return prompt


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


def raise_duplicate_keys(ordered_pairs):
    if len(ordered_pairs) > 1:
        raise FunctionCallingParserError(
            "\nTwo elements in dictionary is against the scheema,\n"
            + f"got: {[t[0] for t in ordered_pairs]}"
        )
    return {ordered_pairs[0][0]: ordered_pairs[0][1]}


def parse_inputs(path: str) -> list[str]:
    prompt_list: list[Prompt] = []
    with open(path) as f:
        file_data = json.load(f, object_pairs_hook=raise_duplicate_keys)
        if not isinstance(file_data, list):
            raise FunctionCallingParserError("Not a list")
        for e in file_data:
            print(e)
            prompt_list.append(Prompt(prompt=e))
    return [p.prompt for p in prompt_list]
