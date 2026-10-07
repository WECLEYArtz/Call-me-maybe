from .parsing.input_parsing import Prompt
from numpy import argmax

import numpy as np

from .llm_sdk.llm_sdk import Small_LLM_Model
from .parsing.function_definition_parsing import FuncDef


def get_list_of_index(matrix: list[list[int]], i: int) -> list[int]:
    return [lst[i] for lst in matrix if len(lst) > i]


def get_slm_answers(
    prompts_list: list[Prompt],
    function_definitions: list[FuncDef],
    init_prompt: str,
) -> list[str]:
    model = Small_LLM_Model()

    #  /======== Sub Functions =========\
    def model_encode(string: str) -> list[int]:
        return model.encode(string)[0].tolist()

    def model_decode(tokkens: list[int]) -> str:
        return model.decode(tokkens)

    def get_func_tokkens_to_fd() -> dict[tuple[int, ...], FuncDef]:
        function_tokens: dict[tuple[int, ...], FuncDef] = {}
        for fd in function_definitions:
            function_tokens.update({tuple(model_encode(fd.name)): fd})
        return function_tokens

    def get_next_prediction(
        live_prompt: list[int], mask_targets: list[int]
    ) -> int:
        logits = np.array(model.get_logits_from_input_ids(live_prompt))
        if len(mask_targets):
            mask = np.full_like(logits, -np.inf)
            mask[mask_targets] = logits[mask_targets]
            return int(argmax(mask))
        else:
            return int(argmax(logits))

    def contrain_str(
        live_prompt: list[int], result_tokkens: list[int], tokken: int
    ) -> int | None:
        decoded = model_decode(tokken)

        if '"' == decoded:
            live_prompt.extend(tokken)
            return None

        tokken = model_encode(decoded.split('"')[0])
        live_prompt.extend(tokken)
        result_tokkens.extend(tokken)

        if '"' in decoded:
            return None

        return tokken

    def contrain_int(
        live_prompt: list[int], result_tokkens: list[int], tokken: int
    ) -> int | None:
        decoded = model_decode(tokken)
        if '"' in decoded:
            return None

        if not model_decode(result_tokkens + [tokken]).isdigit():
            return None

        live_prompt.append(tokken)
        result_tokkens.append(tokken)

        return tokken

    #  \======== Sub Functions =========/

    result_entries: list[str] = []

    initial_prompt_encoded = model_encode(init_prompt)
    func_tokkens_to_fd = get_func_tokkens_to_fd()
    longest_func_tokkens = max([len(t) for t in func_tokkens_to_fd.keys()])

    tokken_of_space = model_encode(" ")[0]  # To start every appending
    tokken_of_quote = model_encode('"')[0]  # To start every appending

    for prompt in prompts_list:
        # Prepare first message to our SLM
        print("[[ NEXT PROMPT: ]]", prompt)
        live_prmpt = initial_prompt_encoded.copy()

        # Insert first piece of the entry to all
        current_entry_str = prompt.entry_piece()  # entry start
        live_prmpt.extend(model_encode(current_entry_str))
        next_tokken: int = tokken_of_space  # Use just newline for fisrt append

        # Function prediction section
        result_func_tokkens: tuple[int, ...] = ()
        for i in range(0, longest_func_tokkens):
            live_prmpt.append(next_tokken)
            mask_target: list[int] = get_list_of_index(func_tokkens_to_fd, i)
            next_tokken = get_next_prediction(live_prmpt, mask_target)
            result_func_tokkens += (next_tokken,)
            if result_func_tokkens in func_tokkens_to_fd:
                break
        live_prmpt.append(next_tokken)
        # decode the result function name and append it to entry
        current_entry_str += (
            '"' + model_decode(list(result_func_tokkens)) + '"'
        )

        # make the parameters generator and start prediction based on them
        next_param_gen = func_tokkens_to_fd[
            result_func_tokkens
        ].next_param_piece_type()
        for piece, typing in next_param_gen:
            current_entry_str += piece
            live_prmpt.extend(model_encode(piece))

            next_tokken: int = tokken_of_space
            result_tokkens: list[int] = []

            if typing == "integer" or typing == "number":
                while 1:
                    if not contrain_int(
                        live_prmpt,
                        result_tokkens,
                        get_next_prediction(live_prmpt, []),
                    ):
                        break

            elif typing == "string":
                live_prmpt.append(tokken_of_quote)
                result_tokkens.append(tokken_of_quote)
                while 1:
                    if not contrain_str(
                        live_prmpt,
                        result_tokkens,
                        get_next_prediction(live_prmpt, []),
                    ):
                        live_prmpt.append(tokken_of_quote)
                        result_tokkens.append(tokken_of_quote)
                        break
            elif typing == "boolean":
                pass
                # BA9I BOOLEAN
            else:
                raise ValueError("Unexpected typing during constrained decode")
                result_tokkens.append(next_tokken)
            current_entry_str += model_decode(result_tokkens)

        # ...parameters to be constrained
        # Last step after the entry is closed with }

        print(current_entry_str + "}}")
        result_entries.append(current_entry_str + "}}")
    return result_entries
