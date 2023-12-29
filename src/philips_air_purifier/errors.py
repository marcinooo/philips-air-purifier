"""Module contains errors."""


class AirPurifierError(Exception):
    """Base library error."""


class ClientNotConnectedError(AirPurifierError):
    """Indicates that client was not connected with device."""


class ParameterNotRecognizedError(AirPurifierError):
    """Indicates that parameter cannot be set or read."""


class ParameterValueError(AirPurifierError):
    """Indicates that value of parameter is not allowed."""


class ParameterRequiredError(AirPurifierError):
    """Indicates that parameter is required to set in device."""


class ResponseDecodingError(AirPurifierError):
    """Indicates that received data cannot be decoded."""
