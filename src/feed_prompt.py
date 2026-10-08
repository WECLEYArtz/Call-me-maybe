from .parsing.function_definition_parsing import FuncDef
from typing import Generator

INIT_PROMPT_TEMPLATE: str = """
You are a function-calling assistant.
Call exactly one of the provided functions.


Rules:
- Pick the function whose purpose best matches the request.
- Pick names from prompts when appropriate.
- Pick values inside quotations without their quotations
- Generate integers and numbers after double dots
- Generate string after double quotes

Functions:
{FUNCTIONS}
"""


def generate_prompt_initialiser(funcdefs: list[FuncDef]) -> str:
    """Build the initial prompt from the available function definitions.

    Args:
        funcdefs: Function definitions to include in the prompt.

    Returns:
        The initial prompt passed to the language model.
    """
    functions_list_str: str = "\n".join([str(funcdef) for funcdef in funcdefs])
    init_prompt = INIT_PROMPT_TEMPLATE.format(FUNCTIONS=functions_list_str)
    return init_prompt


def entry_pieces_generator(
    function_defs: list[FuncDef],
) -> Generator[str, None, None]:
    """Yield JSON fragments used to start a function-call entry.

    Args:
        function_defs: Function definitions whose parameters are represented.

    Yields:
        JSON fragments for the generated parameter object.
    """

    yield '"parameters":{'
    for fd in function_defs:
        yield f'"{fd.name}":'
