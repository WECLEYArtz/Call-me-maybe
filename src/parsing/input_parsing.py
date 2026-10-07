import json
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator
from pydantic_core import PydanticCustomError
from src.errors import FunctionCallingParserError
from src.parsing.duplicates_watcher import duplicates_watcher


class Prompt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str

    @field_validator("prompt", mode="after")
    @classmethod
    def validator(cls, prompt: str) -> str:
        if not prompt.strip():
            raise FunctionCallingParserError("Empty prompt")
        return prompt


class Prompts(BaseModel):
    inputs: list[Prompt]


def parse_inputs(path: str) -> list[str]:
    with open(path) as f:
        try:
            file_data = json.load(f, object_pairs_hook=duplicates_watcher)
            return [p.prompt for p in Prompts(inputs=file_data).inputs]
        except ValidationError:
            raise PydanticCustomError(
                "Validation Error", "Invalid input file format"
            )
