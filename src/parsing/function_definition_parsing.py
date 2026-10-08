from typing import Generator
import json

from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator, ValidationError
from pydantic_core import PydanticCustomError
from ..errors import FunctionDefinitionParserError
from ..parsing.duplicates_watcher import duplicates_watcher

CONTROL_FLOW = {"if", "else", "for", "while", "break", "continue", "return"}


class FunDefType(BaseModel):
    """Describe one supported parameter or return type."""

    model_config = ConfigDict(extra="forbid")
    type: Literal["string", "number", "integer", "boolean"]


class FuncDef(BaseModel):
    """Validate and represent one callable function definition."""

    model_config = ConfigDict(extra="forbid")
    name: str
    description: str
    parameters: dict[str, FunDefType]
    returns: FunDefType

    @field_validator("name", mode="after")
    @classmethod
    def validator(cls, name: str) -> str:
        """Validate that a function name is usable.

        Args:
            name: Function name to validate.

        Returns:
            The normalized function name.

        Raises:
            FunctionDefinitionParserError: If the name is invalid.
        """
        if (name := name.strip()) == "":
            raise FunctionDefinitionParserError(f"Empty function name, {name}")
        if not name.isidentifier():
            raise FunctionDefinitionParserError(
                f"Function name is an identifier, {name}"
            )
        if name in CONTROL_FLOW:
            raise FunctionDefinitionParserError(
                f"Function name is an control flow, {name}"
            )
        return name

    def __str__(self) -> str:
        """Return a readable description for the initial model prompt.

        Returns:
            A formatted description of the function definition.
        """
        return f"""- {self.name}
            Description: {self.description}
            Parameters: {[f"{k} ({v.type})"
            for k,v in self.parameters.items()]}
            Return: {self.returns.type}
        """

    def next_param(self) -> Generator[tuple[str, str, str], None, None]:
        """Yield parameter names, JSON fragments, and declared types.

        Yields:
            Tuples containing a parameter name, JSON fragment, and type name.
        """
        param_names = list(self.parameters.keys())
        param_type = [t.type for t in list(self.parameters.values())]
        yield (
            param_names[0],
            f',"parameters":{{"{param_names[0]}":',
            param_type[0],
        )
        for i in range(1, len(param_names)):
            yield (param_names[i], f',"{param_names[i]}":', param_type[i])


class FunctionDefinitions(BaseModel):
    """Validate the top-level function-definition list."""

    model_config = ConfigDict(extra="forbid")
    definitions: list[FuncDef]


def parse_func_def(path: str) -> list[FuncDef]:
    """Load and validate function definitions from a JSON file.

    Args:
        path: Path to the function definitions JSON file.

    Returns:
        The validated function definitions.

    Raises:
        FunctionDefinitionParserError: If a definition cannot be parsed.
    """
    try:
        with open(path) as f:
            file_data = json.load(f, object_pairs_hook=duplicates_watcher)
        return FunctionDefinitions(definitions=file_data).definitions
    except ValidationError:
        raise PydanticCustomError(
            "Validation Error", "Invalid input file format"
        )
