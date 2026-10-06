import json
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator
from pydantic_core import PydanticCustomError


class FunctionCallingParserError(Exception):
    """Represent error when parsing function calling json file."""

    message: str = "Issue parsing function calling json file: "

    def __init__(self, detail: str):
        """Initialise error class.

        message: error message.
        """
        super().__init__(self.message + detail)


class Prompt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str

    @field_validator("prompt", mode="after")
    @classmethod
    def validate(cls, prompt: str) -> str:
        if not prompt.strip():
            raise FunctionCallingParserError("Empty prompt")
        return prompt


def raise_duplicate_keys(ordered_pairs):
    d = {}
    for k, v in ordered_pairs:
        if k in d:
            raise FunctionCallingParserError("Detected key duplication")
        d[k] = v
    return d


def parse_inputs(path: str) -> list[str]:
    prompt_list: list[Prompt] = []
    with open(path) as f:
        try:
            file_data = json.load(f, object_pairs_hook=raise_duplicate_keys)
            if not isinstance(file_data, list):
                raise FunctionCallingParserError("Not a list")

            for e in file_data:
                prompt_list.append(Prompt.model_validate(e))
                print(prompt_list[-1])
        except ValidationError:
            raise PydanticCustomError("Validation Error", "Invalid input file format")
    return [p.prompt for p in prompt_list]
