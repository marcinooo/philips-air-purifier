import socket
import random
import json
import requests

from ._utils import aes_decrypt, encrypt, decrypt, filter_reviced_data, filter_requested_data
from .errors import ClientNotConnectedError, HostNotDefinedError


class PhilipsAirPurifier:

    def __init__(self, host=None):
        self.host = host
        self.session_key = None
        self.connected = False

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, value):
        if value is not None:
            self.__host = socket.gethostbyname(value)
        else:
            self.__host = None

    def connect(self, host=None):
        if host is not None:
            self.host = host
        if self.host is None:
            raise HostNotDefinedError('IP or DNS name should be provided to connect to device.')

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
        resp = requests.put('http://{0}/di/v1/products/0/security'.format(self.host), data=enc_body)
        resp = resp.content.decode('ascii')
        data = json.loads(resp)
        if 'key' not in data:
            print('The problem with connection. The url is probably invalid.')
        key = data['key']
        data_signed = int(data['hellman'], 16)
        new_enc_key = pow(data_signed, bits, moulus)
        new_enc_key_bytes = new_enc_key.to_bytes(128, byteorder='big')[:16]
        session_key = aes_decrypt(new_enc_key_bytes, bytes.fromhex(key))
        self.session_key = session_key[:16]
        self.connected = True
        return self

    def get(self, *parameters):
        if not self.connected:
            raise ClientNotConnectedError("Clinect was not connected to device.")
        resp = requests.get('http://{0}/di/v1/products/1/air'.format(self.host))
        resp = decrypt(self.session_key, resp.content)
        data = json.loads(resp)
        if parameters:
            data = filter_reviced_data(data, *parameters)
        return data

    def set(self, **parameters):
        if not self.connected:
            raise ClientNotConnectedError("Clinect was not connected to device.")
        data = filter_requested_data(parameters)
        enc_body = encrypt(self.session_key, **data)
        resp = requests.put('http://{0}/di/v1/products/1/air'.format(self.host), data=enc_body)
        resp = decrypt(self.session_key, resp.content)
        data = json.loads(resp)
        return data
            