import json
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator
from pydantic_core import PydanticCustomError
from ..errors import FunctionCallingParserError
from .duplicates_watcher import duplicates_watcher


class Prompt(BaseModel):
    """Validate and represent one natural-language prompt."""

    model_config = ConfigDict(extra="forbid")
    prompt: str

    @field_validator("prompt", mode="after")
    @classmethod
    def validator(cls, prompt: str) -> str:
        """Reject prompts that contain only whitespace.

        Args:
            prompt: Prompt text to validate.

        Returns:
            The validated prompt text.

        Raises:
            FunctionCallingParserError: If the prompt is empty.
        """
        if not prompt.strip():
            raise FunctionCallingParserError("Empty prompt")
        return prompt

    def entry_piece(self) -> str:
        """Return the JSON fragment for a generated entry.

        Returns:
            The beginning of the JSON function-call representation.
        """
        return f'{{"prompt":{json.dumps(self.prompt)},"name":"'


class Prompts(BaseModel):
    """Validate the top-level list of input prompts."""

    inputs: list[Prompt]


def parse_inputs(path: str) -> list[Prompt]:
    """Load and validate prompts from a JSON file.

    Args:
        path: Path to the prompts JSON file.

    Returns:
        The validated prompts.

    Raises:
        FunctionCallingParserError: If the input data is invalid.
    """
    with open(path) as f:
        try:
            file_data = json.load(f, object_pairs_hook=duplicates_watcher)
            return Prompts(inputs=file_data).inputs
        except ValidationError:
            raise PydanticCustomError(
                "Validation Error", "Invalid input file format"
            )
