from .parsing.function_definition_parsing import FuncDef
from typing import Generator

INIT_PROMPT_TEMPLATE: str = """
You are a function-calling assistant.
Call exactly one of the provided functions.


Rules:
- Pick the function whose purpose best matches the request.
- Use only parameters defined in the schema.
- Copy values from the request exactly. Do not guess missing required values.
- If no function fits, reply in plain text with no tool call.

Functions:
{FUNCTIONS}
"""


def generate_prompt_initialiser(funcdefs: list[FuncDef]):
    functions_list_str: str = "\n".join([str(funcdef) for funcdef in funcdefs])
    init_prompt = INIT_PROMPT_TEMPLATE.format(FUNCTIONS=functions_list_str)
    return init_prompt


def entry_pieces_generator(
    function_defs: list[FuncDef],
) -> Generator[str, None, None]:
    """Yield every key from the entry, containing all the modified elements.

    The entry contains the prompt and prameters
    when all prompts and parameters ae used,
    a double and curly braket is yielded
    """

    yield '"parameters":{'
    for fd in function_defs:
        yield f'"{fd.name}":'
