from .BaseException import NuclinoBaseException


class NuclinoAPIException(NuclinoBaseException):
    """Base exception class for API errors"""
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.status_code}: {self.message}"
