from numpy import argmax
from collections import defaultdict

import numpy as np

from llm_sdk.llm_sdk import Small_LLM_Model
from .feed_prompt import entry_pieces_generator
from .parsing.function_definition_parsing import FuncDef
import sys


def get_list_of_index(matrix: list[list[int]], i: int) -> list[int]:
    return [lst[i] for lst in matrix if len(lst) > i]


def get_slm_answers(
    prompts_list: list[str], function_defs: list[FuncDef], init_prompt: str
) -> list[str]:
    model = Small_LLM_Model()
    entries: list[str] = []

    def model_encode(string: str) -> list[int]:
        return model.encode(string)[0].tolist()

    def model_decode(tokkens: list[int]) -> str:
        return model.decode(tokkens)

    def get_function_tokens() -> dict[tuple[int, ...], str]:
        function_tokens: dict[tuple[int, ...], str] = defaultdict(str)
        for name in [fd.name for fd in function_defs]:
            function_tokens[tuple(model_encode(name))] = name
        return function_tokens

    initial_prompt_encoded = model_encode(init_prompt)
    func_tokens_names = get_function_tokens()
    longest_func_tokkens = max([len(t) for t in func_tokens_names.keys()])
    newline_tokken = model_encode(" ")[0]

    print(func_tokens_names)
    # For every prompt
    for prompt in prompts_list:
        entry_pieces_gen = entry_pieces_generator(prompt, function_defs)

        # Prepare first message to our SLM
        current_entry_str = next(entry_pieces_gen)  # strings
        live_prompt_tokkens = initial_prompt_encoded
        live_prompt_tokkens.extend(model_encode(current_entry_str))

        print(model_decode(live_prompt_tokkens))

        _function_tokkens: tuple[int, ...] = ()
        next_tokken: int = newline_tokken
        for i in range(0, longest_func_tokkens):
            live_prompt_tokkens.append(next_tokken)

            logits = np.array(
                model.get_logits_from_input_ids(live_prompt_tokkens)
            )
            mask = np.full_like(logits, -np.inf)
            mask_targets = get_list_of_index(func_tokens_names, i)
            mask[mask_targets] = logits[mask_targets]
            next_tokken = int(argmax(mask))
            _function_tokkens += (next_tokken,)
            print(model_decode(_function_tokkens))

            if _function_tokkens in func_tokens_names:
                break
        sys.exit(1)
        entries.append(current_entry_str)
    return entries
