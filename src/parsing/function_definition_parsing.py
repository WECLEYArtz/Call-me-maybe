from typing import Generator
import json

from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator, ValidationError
from pydantic_core import PydanticCustomError
from ..errors import FunctionDefinitionParserError
from ..parsing.duplicates_watcher import duplicates_watcher

CONTROL_FLOW = {"if", "else", "for", "while", "break", "continue", "return"}


class FunDefType(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["string", "number", "integer", "boolean"]


class FuncDef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    description: str
    parameters: dict[str, FunDefType]
    returns: FunDefType

    @field_validator("name", mode="after")
    @classmethod
    def validator(cls, name: str) -> str:
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

    def __str__(self):
        return f"""- {self.name}
            Description: {self.description}
            Parameters: {[f"{k} ({v.type})"
            for k,v in self.parameters.items()]}
            Return: {self.returns.type}
        """

    def next_param_piece_type(self) -> Generator[tuple[str, str], None, None]:
        param_names = list(self.parameters.keys())
        param_type = [t.type for t in list(self.parameters.values())]
        yield (f',"parameters":{{"{param_names[0]}":', param_type[0])
        for i in range(1, len(param_names)):
            yield (f',"{param_names[i]}":', param_type[i])


class FunctionDefinitions(BaseModel):
    model_config = ConfigDict(extra="forbid")
    definitions: list[FuncDef]


def parse_func_def(path: str) -> list[FuncDef]:
    try:
        with open(path) as f:
            file_data = json.load(f, object_pairs_hook=duplicates_watcher)
        return FunctionDefinitions(definitions=file_data).definitions
    except ValidationError:
        raise PydanticCustomError(
            "Validation Error", "Invalid input file format"
        )
