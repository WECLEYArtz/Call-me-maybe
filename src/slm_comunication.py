from .parsing.input_parsing import Prompt
from numpy import argmax

import numpy as np

from llm_sdk import Small_LLM_Model  # type: ignore
from .parsing.function_definition_parsing import FuncDef


class Entry:
    """Represent a generated function call."""

    prompt: str
    name: str
    parameters: dict[str, str | int] = {}

    def make(self) -> dict[str, str | dict[str, str | int]]:
        """Return the entry in the output JSON format.

        Returns:
            A dictionary containing the prompt, function name, and parameters.
        """
        return {
            "prompt": self.prompt,
            "name": self.name,
            "parameters": self.parameters,
        }


def get_list_of_index(matrix: list[list[int]], i: int) -> list[int]:
    """Return values at index ``i`` from rows containing that index.

    Args:
        matrix: Rows from which values should be selected.
        i: Index to read from each row.

    Returns:
        Values found at the requested index.
    """
    return [lst[i] for lst in matrix if len(lst) > i]


def get_slm_answers(
    prompts_list: list[Prompt],
    function_definitions: list[FuncDef],
    init_prompt: str,
) -> list[dict]:
    """Generate structured function calls for the supplied prompts.

    Args:
        prompts_list: Prompts to convert into function calls.
        function_definitions: Functions that the model may select.
        init_prompt: Prompt describing the available functions.

    Returns:
        Generated function-call dictionaries in input order.
    """
    model = Small_LLM_Model()

    #  /======== Sub Functions =========\
    def model_encode(string: str) -> list[int]:
        """Encode text and return its token IDs as a plain list.

        Args:
            string: Text to encode.

        Returns:
            The encoded token IDs.
        """
        return list(i for i in model.encode(string)[0].tolist())

    def model_decode(tokkens: list[int]) -> str:
        """Decode a list of token IDs into text.

        Args:
            tokkens: Token IDs to decode.

        Returns:
            The decoded text.
        """
        return str(model.decode(tokkens))

    def get_func_tokkens_to_fd() -> dict[tuple[int, ...], FuncDef]:
        """Map each encoded function name to its function definition.

        Returns:
            A lookup table keyed by function-name token sequences.
        """
        function_tokens: dict[tuple[int, ...], FuncDef] = {}
        for fd in function_definitions:
            function_tokens.update({tuple(model_encode(fd.name)): fd})
        return function_tokens

    def get_next_prediction(
        live_prompt: list[int], mask_targets: list[int]
    ) -> int:
        """Return the highest-logit token from the allowed targets.

        Args:
            live_prompt: Token IDs already generated for the current prompt.
            mask_targets: Token IDs allowed for the next prediction.

        Returns:
            The selected next token ID.
        """
        logits = np.array(model.get_logits_from_input_ids(live_prompt))
        if len(mask_targets):
            mask = np.full_like(logits, -np.inf)
            mask[mask_targets] = logits[mask_targets]
            return int(argmax(mask))
        else:
            return int(argmax(logits))

    #  \======== Sub Functions =========/

    result_entries: list[dict] = []

    initial_prompt_encoded = model_encode(init_prompt)
    func_tokkens_to_fd = get_func_tokkens_to_fd()
    func_tokkens_matrix = [list(t) for t in func_tokkens_to_fd.keys()]
    longest_func_tokkens: int = max(
        [len(t) for t in func_tokkens_to_fd.keys()]
    )

    tokken_of_space = model_encode(" ")[0]  # To start every appending
    tokken_of_quote = model_encode('"')[0]  # To start every appending
    tokken_of_true = model_encode("true")[0]  # To start every appending
    tokken_of_false = model_encode("false")[0]  # To start every appending
    tokkens_of_digits = model_encode("0123456789")

    for prompt in prompts_list:
        print(prompt)
        # Prepare first message to our SLM
        entry = {
            "prompt": "",
            "name": "",
            "parameters": dict(),
        }

        Entry()
        live_prmpt = initial_prompt_encoded.copy()

        # Insert first piece of the entry to all
        entry["prompt"] = prompt.prompt
        live_prmpt.extend(model_encode(prompt.entry_piece()))

        # Function prediction section
        result_func_tokkens: tuple[int, ...] = ()
        for i in range(0, longest_func_tokkens):
            next_tokken: int = get_next_prediction(
                live_prmpt, get_list_of_index(func_tokkens_matrix, i)
            )
            result_func_tokkens += (next_tokken,)
            live_prmpt.append(next_tokken)
            if result_func_tokkens in func_tokkens_to_fd:
                break
        live_prmpt.append(tokken_of_quote)
        entry["name"] = model_decode(list(result_func_tokkens))

        # make the parameters generator and start prediction based on them
        next_param_generator = func_tokkens_to_fd[
            result_func_tokkens
        ].next_param()
        for name, piece, typing in next_param_generator:
            live_prmpt.extend(model_encode(piece))

            next_tokken = tokken_of_space
            result_value: str | int | float
            if typing == "integer" or typing == "number":
                result_tokkens: list[int] = []
                while True:
                    tokken = get_next_prediction(live_prmpt, [])
                    if tokken not in tokkens_of_digits:
                        break
                    live_prmpt.append(tokken)
                    result_tokkens.append(tokken)

                result_value = int(model_decode(result_tokkens))
                if typing == "number":
                    result_value = float(result_value)

            elif typing == "string":
                live_prmpt.append(tokken_of_quote)
                result_tokkens = []
                while True:
                    tokken = get_next_prediction(live_prmpt, [])
                    decoded = model_decode([tokken])

                    quote_index = decoded.find('"')
                    if quote_index == 0:
                        live_prmpt.append(tokken_of_quote)
                        break
                    if quote_index != -1:
                        tokken = model_encode(decoded[0:quote_index])[0]
                    result_tokkens.append(tokken)
                    live_prmpt.append(tokken)
                    if '"' in decoded:
                        live_prmpt.append(tokken_of_quote)
                        break
                result_value = model_decode(result_tokkens)
            elif typing == "boolean":
                result_bool_token = get_next_prediction(
                    live_prmpt, [tokken_of_true, tokken_of_false]
                )
                result_value = model_decode([result_bool_token])
            assert isinstance(entry["parameters"], dict)
            entry["parameters"].update({name: result_value})
        result_entries.append(entry)
        print(result_entries[-1])
    return result_entries
