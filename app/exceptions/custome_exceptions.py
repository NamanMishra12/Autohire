class DuplicateResumeException(Exception):
    """Raised when a duplicate resume is uploaded."""

    def __init__(self, message: str = "This resume has already been uploaded."):
        self.message = message
        super().__init__(self.message)


class UnsupportedFileTypeException(Exception):
    """Raised when an unsupported file is uploaded."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class FileTooLargeException(Exception):
    """Raised when uploaded file exceeds allowed size."""

    def __init__(self, message: str = "File exceeds maximum allowed size."):
        self.message = message
        super().__init__(self.message)


class ResumeNotFoundException(Exception):
    """Raised when a requested resume does not exist."""

    def __init__(self, message: str = "Resume not found."):
        self.message = message
        super().__init__(self.message)

class UnauthorizedException(Exception):
    def __init__(self, message: str = "Unauthorized."):
        self.message = message
        super().__init__(self.message)


class InvalidCredentialsException(Exception):
    def __init__(self, message: str = "Invalid email or password."):
        self.message = message
        super().__init__(self.message)