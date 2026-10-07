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
    entries: list[str] = []

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
        mask = np.full_like(logits, -np.inf)
        mask[mask_targets] = logits[mask_targets]
        return int(argmax(mask))

    initial_prompt_encoded = model_encode(init_prompt)
    func_tokkens_to_fd = get_func_tokkens_to_fd()
    longest_func_tokkens = max([len(t) for t in func_tokkens_to_fd.keys()])
    space_tokken = model_encode(" ")[0]

    for prompt in prompts_list:
        # Prepare first message to our SLM
        print(prompt)
        live_prompt = initial_prompt_encoded

        # Insert first piece of the entry to all
        current_entry_str = prompt.entry_piece()  # entry start
        live_prompt.extend(model_encode(current_entry_str))
        mask_target: list[int] = get_list_of_index(func_tokkens_to_fd, i)
        next_tokken: int = space_tokken  # Use just newline for fisrt append

        # Function prediction section
        result_func_tokkens: tuple[int, ...] = ()
        for i in range(0, longest_func_tokkens):
            live_prompt.append(next_tokken)
            next_tokken = get_next_prediction(live_prompt, mask_target)
            result_func_tokkens += (next_tokken,)
            if result_func_tokkens in func_tokkens_to_fd:
                break
        live_prompt.append(next_tokken)
        # decode the result function name and add it to entry
        current_entry_str += model_decode(list(result_func_tokkens))
        print(current_entry_str)

        # make the parameters generator and start prediction based on them
        next_param_gen = func_tokkens_to_fd[result_func_tokkens].next_param()
        for next_param in next_param_gen:
            current_entry_str += next_param
            next_tokken: int = space_tokken
            result_value_tokkens: list[int]
            while 1:
                live_prompt.extend(model_encode(next_param))
                next_tokken = get_next_prediction(live_prompt)
                result_value_tokkens.append(next_tokken)

        # ...parameters to be constrained
        # Last step after the entry is closed with }
        entries.append(current_entry_str)
    return entries
