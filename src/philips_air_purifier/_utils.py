
import json
import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

from  .errors import ParameterNotRecognizedError, ParameterValueError, ParameterRequiredError


def aes_decrypt(key, data):
    iv = bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(data)


def decrypt(key, data):
    try:
        payload = base64.b64decode(data)
    except binascii.Error:
        raise ResponseDecodingError("Problem with decoding recived data. Try again.")
    data = aes_decrypt(key, payload)
    # response starts with 2 random bytes, exclude them
    response = unpad(data, 16, style='pkcs7')[2:]
    return response.decode('ascii')


def encrypt(key, **kwargs):
    # add two random bytes in front of the body
    data = 'AA' + json.dumps(kwargs)
    data = pad(bytearray(data, 'ascii'), 16, style='pkcs7')
    iv = bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data_enc = cipher.encrypt(data)
    return base64.b64encode(data_enc)


def filter_reviced_data(data, *parameters):
    result = {}
    for parameter in parameters:
        if parameter in data:
            result[parameter] = data[parameter]
    return result


def filter_requested_data(parameters):
    if not parameters:
        raise ParameterRequiredError('At least one parameter must be provided.')
    for key, value in parameters.items():
        if key in ALLOWED_PARAMETERS_TO_SET:
            if value in ALLOWED_PARAMETERS_TO_SET[key]['values']:
                continue
            message = "Value '{}' is not allowed.\n{}".format(value, ALLOWED_PARAMETERS_TO_SET[key]['help'])
            raise ParameterValueError(message)
        message = "Unrecoginized '{}' parameter. Allowed parameters: {}".format(
            key, ', '.join(ALLOWED_PARAMETERS_TO_SET.keys())
        )
        raise ParameterNotRecognizedError(message)
    return parameters


ALLOWED_PARAMETERS_TO_SET = {
    'pwr': {
        'values': ['0', '1'],
        'help': "'pwr' parameter turn on device if is set to '1' or turn off if it set to '0'",
    },
    'om': {
        'values': ['1', '2', '3', 's'],
        'help': "'om' parameter controls speed. Allowed values: '0', '1', '2', '3', 's'.",
    },
    'aqil': {
        'values': list(range(1, 101)),
        'help': "'aqil' parameter controls light brightness.",
    },
    'uil': {
        'values': ['0', '1'],
        'help': "'uil' parameter turn on device's display if it is set to '1' or turn off if it set to '0'",
    },
    'ddp': {
        'values': ['0', '1'],
        'help': "'ddp' parameter controls pollution display modes. It should be set to '0' for pm25 or '1' for IAI.",
    },
    # TODO: Check allowed values
    # 'pm25': {
    #     'values': ['0', '1'],
    #     'help': "'uil' parameter turn on device's display if is set to '1' or turn off if it set to '0'",
    # },
    # TODO: Check allowed values
    # 'iaql': {
    #     'values': ['0', '1'],
    #     'help': "'uil' parameter turn on device's display if is set to '1' or turn off if it set to '0'",
    # },
    'mode': {
        'values': ['P', 'A', 'M', 'B'],
        'help': "'mode' parameter controls device's mode. \n"
        "It should be set to 'A' for anti-allergen mode, 'B' for antivirus mode, "
        "'P' for anti-pollution mode, 'M' for manual mode.",
    },
}
