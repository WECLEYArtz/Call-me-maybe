from pydantic import BaseModel, Field

class FunctionDefinitionReturn(BaseModel):
    pass


class FunctionDefinitionReturn(BaseModel):
    name: str


class FunctionDefinitionParameters(BaseModel):
    parameters: list[]

class FunctionDefinition(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters:FunctionDefinitionParameter
    returns:FunctionDefinitionReturn


def parse_func_def(path: str) -> dict[str,any]:
    try:
        with open(path) as f:

