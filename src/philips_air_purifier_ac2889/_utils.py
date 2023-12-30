"""Module contains utils for air purifier package."""

import json
import base64
import binascii
from typing import Dict
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

from .errors import ParameterNotRecognizedError, ParameterValueError, ResponseDecodingError


ALLOWED_PARAMETERS = {
    'pwr': {
        'values': ['0', '1'],
        'help': '"pwr" parameter turn on device if is set to "1" or turn off if it set to "0".',
    },
    'om': {
        'values': ['1', '2', '3', 's'],
        'help': '"om" parameter controls speed. Allowed values: "1", "2", "3", "s".',
    },
    'aqil': {
        'values': list(range(1, 101)),
        'help': '"aqil" parameter controls light brightness.',
    },
    'uil': {
        'values': ['0', '1'],
        'help': '"uil" parameter turn on device\'s display if it is set to "1" or turn off if it set to "0".',
    },
    'ddp': {
        'values': ['0', '1'],
        'help': '"ddp" parameter controls pollution display modes. It should be set to "0" for pm25 or "1" for IAI.',
    },
    # TODO: Check allowed values
    # 'pm25': {
    #     'values': ['0', '1'],
    #     'help': '"uil" parameter turn on device\'s display if is set to "1" or turn off if it set to "0"',
    # },
    # TODO: Check allowed values
    # 'iaql': {
    #     'values': ['0', '1'],
    #     'help': '"uil" parameter turn on device\'s display if is set to "1" or turn off if it set to "0"',
    # },
    'mode': {
        'values': ['P', 'A', 'M', 'B'],
        'help': '"mode" parameter controls device\'s mode. Set to "A" for anti-allergen mode, '
                '"B" for antivirus mode, "P" for anti-pollution mode, "M" for manual mode.',
    },
}


def aes_decrypt(key: bytes, data: bytes) -> bytes:
    """
    Decrypts data by given key.

    :param key: key required to decrypt data
    :param data: data to decrypt
    :return: decrypted data
    """

    return AES.new(key, AES.MODE_CBC, bytes(16)).decrypt(data)


def aes_encrypt(key: bytes, data: bytes) -> bytes:
    """
    Encrypt values by given key.

    :param key: key required to encrypt data
    :param data: data to encrypt
    :return: encrypted data
    """

    return AES.new(key, AES.MODE_CBC, bytes(16)).encrypt(data)


def decrypt(key: bytes, data: bytes) -> str:
    """
    Decrypts data by given key. Removes additional padding from data.

    :param key: key required to decrypt data
    :param data: data to decrypt
    :return: decrypted data
    """

    try:
        payload = base64.b64decode(data)
    except binascii.Error:
        raise ResponseDecodingError("Response cannot be decoded. Reconnect to device and try again.")

    data = aes_decrypt(key, payload)
    response = unpad(data, 16, style='pkcs7')[2:]  # response starts with 2 random bytes, exclude them

    return response.decode('ascii')


def encrypt(key: bytes, data: Dict[str, object]) -> bytes:
    """
    Encrypt data with additional padding by given key.

    :param key: key required to encrypt data
    :param data: data to encrypt
    :return: encrypted data
    """

    data = 'AA' + json.dumps(data)  # add two random bytes in front of the body
    data = pad(bytearray(data, 'ascii'), 16, style='pkcs7')
    data_enc = aes_encrypt(key, data)

    return base64.b64encode(data_enc)


def filter_response_data(data: Dict, *parameters: str) -> Dict:
    """
    Cuts requested by user parameters from http response.

    :param data: response data
    :param parameters: keys to cut
    :return: response with only required parameters
    """

    try:
        result = {parameter: data[parameter] for parameter in parameters}
    except KeyError as error:
        raise ParameterNotRecognizedError(f'Unknown parameter "{error}". '
                                          f'Allowed parameters: {", ".join(ALLOWED_PARAMETERS.keys())}')

    return result


def filter_request_data(parameters: Dict) -> Dict:
    """
    Checks if requested parameters can be set to given values.

    :param parameters: dictionary of keys and values to set in device
    :return: passed as argument dictionary if it valid
    """

    for key, value in parameters.items():

        if key not in ALLOWED_PARAMETERS:
            raise ParameterNotRecognizedError(f'Unknown parameter "{key}". '
                                              f'Allowed parameters: {", ".join(ALLOWED_PARAMETERS.keys())}')
        if value not in ALLOWED_PARAMETERS[key]['values']:
            raise ParameterValueError(f'Value "{value}" is not allowed. {ALLOWED_PARAMETERS[key]["help"]}')

    return parameters
