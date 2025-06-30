class DocumentClosedException(Exception):
    """
    Exception to be raised when the document is closed.
    """

    def __init__(self, message: str):
        super().__init__(message)
