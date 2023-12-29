"""Module contains main client to control air purifier."""

import socket
import random
import json
import requests
from typing import Union

from ._utils import aes_decrypt, encrypt, decrypt, filter_response_data, filter_request_data
from .errors import ClientNotConnectedError, ParameterRequiredError


class AirPurifier:
    """
    Client to control Philips Air Purifier device.

    .. code:: python

        print(cdscs)


    """

    def __init__(self, host: str) -> None:
        self.host = host
        self.session_key = None
        self.is_connected = False

    @property
    def host(self) -> str:
        return self._host

    @host.setter
    def host(self, value: str) -> None:
        self._host = socket.gethostbyname(value)

    def connect(self, host: Union[str, None] = None) -> 'AirPurifier':
        """
        Connects air purifier client to device in local network.

        :param host: IP address or DNS name of air purifier device
        :return: self
        """

        if host is not None:
            self.host = host

        signed = int('A4D1CBD5C3FD34126765A442EFB99905F8104DD258AC507FD6406CFF14266D31266FEA1E5C41564B777E69'
                     '0F5504F213160217B4B01B886A5E91547F9E2749F4D7FBD7D3B9A92EE1909D0D2263F80A76A6A24C087A09'
                     '1F531DBF0A0169B6A28AD662A4D18E73AFA32D779D5918D08BC8858F4DCEF97C2A24855E6EEB22B3B2E5', 16)
        moulus = int('B10B8F96A080E01DDE92DE5EAE5D54EC52C99FBCFB06A3C69A6A9DCA52D23B616073E28675A23D189838EF'
                     '1E2EE652C013ECB4AEA906112324975C3CD49B83BFACCBDD7D90C4BD7098488E9C219A73724EFFD6FAE564'
                     '4738FAA31A4FF55BCCC0A151AF5F0DC8B4BD45BF37DF365C1A65E68CFDA76D4DA708DF1FB2BC2E4A4371', 16)

        bits = random.getrandbits(256)
        enc_key = pow(signed, bits, moulus)
        body = json.dumps({'diffie': hex(enc_key)[2:]})
        enc_body = body.encode('ascii')

        resp = requests.put(f'http://{self.host}/di/v1/products/0/security', data=enc_body)
        resp = resp.content.decode('ascii')
        data = json.loads(resp)

        if 'key' not in data:
            raise ClientNotConnectedError('Connection URL is probably invalid. Device is not supported.')

        key = data['key']
        data_signed = int(data['hellman'], 16)
        new_enc_key = pow(data_signed, bits, moulus)
        new_enc_key_bytes = new_enc_key.to_bytes(128, byteorder='big')[:16]
        session_key = aes_decrypt(new_enc_key_bytes, bytes.fromhex(key))

        self.session_key = session_key[:16]
        self.is_connected = True

        return self

    def get(self, *parameters: str) -> dict:
        """
        Reads information from device.

        :param parameters: list of information to return
        :return: requested information
        """

        if not self.is_connected:
            raise ClientNotConnectedError("Client was not connected to device.")

        resp = requests.get(f'http://{self.host}/di/v1/products/1/air')
        resp = decrypt(self.session_key, resp.content)
        data = json.loads(resp)

        if parameters:
            data = filter_response_data(data, *parameters)

        return data

    def set(self, **parameters: dict) -> dict:
        """
        Sets given parameters on device.

        :param parameters: dictionary of keys and values to set
        :return:
        """

        if not self.is_connected:
            raise ClientNotConnectedError("Clinect was not connected to device.")

        if not parameters:
            raise ParameterRequiredError('At least one parameter must be provided.')

        data = filter_request_data(parameters)
        enc_body = encrypt(self.session_key, **data)

        resp = requests.put(f'http://{self.host}/di/v1/products/1/air', data=enc_body)
        resp = decrypt(self.session_key, resp.content)
        data = json.loads(resp)

        return data
            