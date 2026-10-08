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

    #  \======== Sub Functions =========/

    result_entries: list[str] = []

    initial_prompt_encoded = model_encode(init_prompt)
    func_tokkens_to_fd = get_func_tokkens_to_fd()
    longest_func_tokkens = max([len(t) for t in func_tokkens_to_fd.keys()])

    tokken_of_space = model_encode(" ")[0]  # To start every appending
    tokken_of_quote = model_encode('"')[0]  # To start every appending
    tokken_of_true = model_encode("true")[0]  # To start every appending
    tokken_of_false = model_encode("false")[0]  # To start every appending
    tokkens_of_digits = model_encode("0123456789")

    for prompt in prompts_list:
        print(prompt)
        # Prepare first message to our SLM
        live_prmpt = initial_prompt_encoded.copy()

        # Insert first piece of the entry to all
        current_entry_str = prompt.entry_piece()  # entry start
        live_prmpt.extend(model_encode(current_entry_str))
        next_tokken: int = tokken_of_quote  # Use just newline for fisrt append

        # Function prediction section
        result_func_tokkens: tuple[int, ...] = ()
        for i in range(0, longest_func_tokkens):
            live_prmpt.append(next_tokken)
            mask_target: list[int] = get_list_of_index(func_tokkens_to_fd, i)
            next_tokken = get_next_prediction(live_prmpt, mask_target)
            result_func_tokkens += (next_tokken,)
            if result_func_tokkens in func_tokkens_to_fd:
                break
        live_prmpt.extend([next_tokken, tokken_of_quote])
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
                    tokken = get_next_prediction(live_prmpt, [])
                    if tokken not in tokkens_of_digits:
                        break
                    live_prmpt.append(tokken)
                    result_tokkens.append(tokken)
                if (
                    typing == "number"
                    and (decode := model_decode(result_tokkens)).isdigit()
                ):
                    result_tokkens = model_encode(str(float(int(decode))))

            elif typing == "string":
                live_prmpt.append(tokken_of_quote)
                result_tokkens.append(tokken_of_quote)
                while 1:
                    tokken = get_next_prediction(live_prmpt, [])
                    print("Prediction:", model_decode(tokken))
                    decoded = model_decode(tokken)
                    if (quote_index := decoded.find('"')) != -1:
                        tokken = model_encode(decoded[0 : quote_index + 1])[0]
                    live_prmpt.append(tokken)
                    result_tokkens.append(tokken)
                    if '"' in decoded:
                        break
            elif typing == "boolean":
                bool_tokken = get_next_prediction(
                    live_prmpt, [tokken_of_true, tokken_of_false]
                )
                live_prmpt.append(bool_tokken)
                result_tokkens.append(bool_tokken)
            else:
                raise ValueError("Unexpected typing during constrained decode")
                result_tokkens.append(next_tokken)
            current_entry_str += model_decode(result_tokkens)
        result_entries.append(current_entry_str + "}}")
        print(result_entries[-1])
    return result_entries
