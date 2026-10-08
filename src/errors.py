class JsonDuplication(Exception):
    """Represent a duplicate key found while parsing JSON."""

    message: str = "Issue parsing json file: Keys duplication: "

    def __init__(self, detail: str):
        """Initialize the exception with additional error details.

        Args:
            detail: Details describing the duplicated key.
        """
        super().__init__(self.message + detail)


class FunctionCallingParserError(Exception):
    """Represent an error when parsing a function-calling JSON file."""

    message: str = "Issue parsing function calling json file: "

    def __init__(self, detail: str):
        """Initialize the exception with additional error details.

        Args:
            detail: Details describing the parsing error.
        """
        super().__init__(self.message + detail)


class FunctionDefinitionParserError(Exception):
    """Represent an error when parsing a function-definition JSON file."""

    message: str = "Issue parsing function calling json file: "

    def __init__(self, detail: str):
        """Initialize the exception with additional error details.

        Args:
            detail: Details describing the parsing error.
        """
        super().__init__(self.message + detail)
