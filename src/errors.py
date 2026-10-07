class JsonDuplication(Exception):
    """Represent all sorts of parsing."""

    message: str = "Issue parsing json file: Keys duplication: "

    def __init__(self, detail: str):
        """Initialise error class.

        message: error message.
        """
        super().__init__(self.message + detail)


class FunctionCallingParserError(Exception):
    """Represent error when parsing function calling json file."""

    message: str = "Issue parsing function calling json file: "

    def __init__(self, detail: str):
        """Initialise error class.

        message: error message.
        """
        super().__init__(self.message + detail)


class FunctionDefinitionParserError(Exception):
    """Represent error when parsing function calling json file."""

    message: str = "Issue parsing function calling json file: "

    def __init__(self, detail: str):
        """Initialise error class.

        message: error message.
        """
        super().__init__(self.message + detail)
