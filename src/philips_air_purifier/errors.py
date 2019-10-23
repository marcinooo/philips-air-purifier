
class HostNotDefinedError(Exception):
    """Indicates that host to connect was not defined."""


class ClientNotConnectedError(Exception):
    """Indicates that client was not connected with device."""


class ParameterNotRecognizedError(Exception):
    """Indicates that parameter cannot be set in device because is not allowed."""


class ParameterValueError(Exception):
    """Indicates that value of parameter is not allowed."""


class ParameterRequiredError(Exception):
    """Indicates that parameter is required to set in device."""


class ResponseDecodingError(Exception):
    """Indicates that recived data cannot be decoded."""
