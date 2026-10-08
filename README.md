*This project has been created as part of the 42 curriculum by ahmounsi.*

# Call Me Maybe

## Description

Call Me Maybe is a Python project that converts natural-language requests
into structured function calls with typed arguments. It uses the
`Qwen/Qwen3-0.6B` language model and constrained decoding to select one
function from the supplied definitions and generate its arguments.

The program does not execute the selected function. It reads function
definitions and prompts from JSON files, generates one function call for each
prompt, and writes the results to a JSON array. Constrained decoding restricts
the model's next-token choices so the generated function name and parameter
values follow the available definitions instead of relying on free-form JSON
generation.

## Instructions

The project requires Python 3.10 or newer and `uv`. The first execution also
requires enough disk space and network access to download the
`Qwen/Qwen3-0.6B` model.

Install the dependencies from the repository root:

```bash
uv sync
```

The project can then be run with:

```bash
uv run python -m src
```

The default input files are
`data/input/functions_definition.json` and
`data/input/function_calling_tests.json`. The default output file is
`data/output/function_calling_results.json`; its parent directory is created
when the program starts.

The command-line options are:

```text
--functions_definition <path>
--input <path>
--output <path>
```

The Makefile provides equivalent shortcuts:

```bash
make install
make run
make lint
make clean
```

Input definitions contain a function `name`, a `description`, typed
`parameters`, and a typed `returns` value:

```json
[
  {
    "name": "fn_add_numbers",
    "description": "Add two numbers together and return their sum.",
    "parameters": {
      "a": {"type": "number"},
      "b": {"type": "number"}
    },
    "returns": {"type": "number"}
  }
]
```

Input prompts are JSON objects containing a `prompt` string:

```json
[
  {"prompt": "What is the sum of 2 and 3?"}
]
```

## Resources

- [Python documentation](https://docs.python.org/3/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [NumPy documentation](https://numpy.org/doc/)
- [PyTorch documentation](https://pytorch.org/docs/)
- [Hugging Face Transformers documentation](https://huggingface.co/docs/transformers/)
- [Qwen3 model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Introduction to tensors](https://towardsdatascience.com/what-is-a-tensor-in-deep-learning-6dedd95d6507/)

AI was used to review the README against the subject requirements, identify
missing PEP 257 docstrings, and improve the clarity of technical
documentation. It was not used as a substitute for understanding the
implementation: the algorithm, design decisions, error handling, and output
format were checked against the source code and the project subject.

## Algorithm explanation

The program first parses and validates the function definitions and prompts
with Pydantic. Duplicate JSON keys are rejected while loading input files.
The available function descriptions are then assembled into an initial prompt
for the local language model.

For each prompt, the model receives the initial prompt and a JSON prefix. The
program encodes every available function name and stores its token sequence.
During function selection, it examines the model logits one token at a time
and masks every token that cannot continue one of the known function-name
sequences. The highest-logit token among the valid choices is appended to the
live prompt until a complete known function name has been produced.

The selected function's parameters are generated according to their declared
types. Integer and number parameters accept digit tokens, boolean parameters
are restricted to `true` and `false`, and string parameters are generated
until the closing quote is selected. The generated tokens are decoded and
stored with the original prompt and selected function name. This is
constrained decoding because the model is not merely asked to produce valid
JSON; invalid next tokens are actively excluded from the logits at each
constrained step.

## Design decisions

- Pydantic models validate external JSON and reject unknown or malformed
  fields before generation begins.
- Function selection is performed by the language model using the supplied
  descriptions, rather than by keyword matching or a hard-coded heuristic.
- The implementation uses the public `llm_sdk` methods, including model
  encoding, decoding, and logit access.
- Function names are matched as token sequences, which supports names that
  tokenize to different numbers of tokens.
- The model is loaded once per program run and reused for all prompts.
- Prompts are processed in input order, keeping output order deterministic.
- The output schema follows the subject: each entry contains exactly
  `prompt`, `name`, and `parameters`.

## Performance analysis

Constrained decoding improves structural reliability by preventing unknown
function names and invalid type-specific tokens from being selected. The
resulting output is intended to be 100% parseable JSON and to remain
consistent with the supplied function definitions.

The trade-off is speed. Because the model is evaluated repeatedly while
selecting tokens, constrained generation is slower than unrestricted
generation. The model is initialized only once, which avoids repeating its
loading cost for every prompt. Runtime and memory usage depend primarily on
the model device, the number of prompts, and the length of the generated
values; CPU execution is slower than GPU execution.

The project target is at least 90% accuracy for function selection and
argument extraction, valid JSON for every output entry, and completion of the
provided tests in under five minutes on standard hardware.

## Challenges faced

The main challenge was obtaining reliable structured output from a small
language model. Prompting alone can produce malformed JSON, invalid function
names, missing quotes, or values with the wrong type.

The solution was to inspect next-token logits and constrain them according to
the known function-name token sequences and parameter types. String generation
required additional care because the decoder must recognize a closing quote
without including it in the returned value. Input validation and explicit
error reporting also make malformed files and missing paths easier to
diagnose without silently producing an invalid result.

## Testing strategy

The supplied test file covers addition, greetings, string reversal, square
roots, and regular-expression substitution. The complete pipeline can be
tested with:

```bash
uv run python -m src
```

After execution, the output file should be valid JSON. Each entry should
contain the original `prompt`, a function `name` from the definitions file,
and a `parameters` object whose keys and value types match that function's
schema.

The project checks code quality with:

```bash
make lint
```

Additional validation should use custom paths and malformed or missing input
files, duplicate JSON keys, empty prompts, ambiguous prompts, large numbers,
special characters, wrong types, and functions with multiple parameters.
The correction criteria also require checking that all outputs are parseable,
that function selection and argument extraction exceed 90% accuracy, and
that repeated runs remain reliable.

## Example usage

Run the default demonstration:

```bash
uv run python -m src
```

Run the program with custom input and output paths:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calls.json
```

For an input prompt such as:

```json
{"prompt": "What is the sum of 2 and 3?"}
```

the corresponding output has this form:

```json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": {"a": 2.0, "b": 3.0}
  }
]
```
