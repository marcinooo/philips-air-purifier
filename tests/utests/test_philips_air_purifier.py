import unittest
import json
from unittest.mock import patch, Mock
from ddt import ddt, data, unpack

from philips_air_purifier import PhilipsAirPurifier
from philips_air_purifier._utils import filter_requested_data
from philips_air_purifier.errors import ParameterValueError, ParameterNotRecognizedError
from philips_air_purifier import ALLOWED_PARAMETERS_TO_SET


@ddt
class TestAirPurifier(unittest.TestCase):
    
    def setUp(self):
        self.philips_air_purifier = PhilipsAirPurifier(host='192.168.1.21')
        self.philips_air_purifier.connected = True
        self.session_key = b'\x9a!\xeaOa\xbf3\xe9\x01\xa8\x1fS]\x0b\xd6\xad'

    @data(
        ( 
            b'{"hellman":"74b287a8cf17541ceb8f0bdb796e5dccddf6b87ad401d153533536af3bce2455c8c8a15b07'
            b'e85f83ae5bcc13552f6eb7eff168940d5af80871c3b348dfcbd047050f30a107374731a7a1033e725a4d05'
            b'b7a770cabea3924dbf68e95dec6c54d18ac205c46d9670ba3f5dd75117735b9f05bef7d1f25df2f88f15e9'
            b'72c4ce9182","key":"b5e2c4a35af01c3e4351d9f24c13f7297389192347ba1526a8c029552539d3a5"}',
            42660447339810945252419664584000420784060651262356283027534236696752827231401,
            b'\x9a!\xeaOa\xbf3\xe9\x01\xa8\x1fS]\x0b\xd6\xad'
        ),
    )
    @unpack
    @patch('random.getrandbits')
    @patch('requests.put')
    def test_philips_air_purifier_connect_procedure(self, put_requests_data, bits, session_key, 
                                                    mock_put, mock_getrandbits):
        self.philips_air_purifier.connected = False
        mock_put.return_value = self._mock_response(content=put_requests_data)
        mock_getrandbits.return_value = bits
        self.philips_air_purifier.connect()
        self.assertEqual(self.philips_air_purifier.session_key, session_key)
        self.assertEqual(self.philips_air_purifier.connected, True)

    @data(
        (
            None, 
            b'Bm3hvm2fTmxoSWXldbkwyAlLEoQm/RXDmQf3YcG451eZ/WiaRBrRfnwaVTCzyg5jdSDRZK4fJra/XHC52SmPmQ'
            b'iiEfNnHmR+qBzuvE0i3NzhuQQbYFZJaepj6D0t70wQjqosF+utrAHL2+Ecvu8jNXX91IgUZZHeFP3+KE+UDTA=',
            {'om': '0', 'pwr': '0', 'cl': False, 'aqil': 50, 'uil': '1', 'dt': 0, 'dtrs': 0, 
             'mode': 'A', 'pm25': 5, 'iaql': 2, 'aqit': 0, 'ddp': '1', 'err': 193},
        ),
        (
            [], 
            b'Bm3hvm2fTmxoSWXldbkwyAlLEoQm/RXDmQf3YcG451eZ/WiaRBrRfnwaVTCzyg5jdSDRZK4fJra/XHC52SmPmQ'
            b'iiEfNnHmR+qBzuvE0i3NzhuQQbYFZJaepj6D0t70wQjqosF+utrAHL2+Ecvu8jNXX91IgUZZHeFP3+KE+UDTA=',
            {'om': '0', 'pwr': '0', 'cl': False, 'aqil': 50, 'uil': '1', 'dt': 0, 'dtrs': 0, 
             'mode': 'A', 'pm25': 5, 'iaql': 2, 'aqit': 0, 'ddp': '1', 'err': 193},
        ),
        (
            ['pwr'], 
            b'WQTVglfzx3QgGe12t3/vp3dDETRF+y5j6cSV9PFRU/H807UFG53TFJQ6svMGcX3fnjblFFf4UoGEqc8JJ6svNl'
            b'KliV7dvo/NGvC6DkWqMLB9I5G181lOWy5FVqFAIg+nYJVEQrSTXs+BBg9Zu/XQZfsEkYtYYrX/kIYx3s3TwgQ=',
            {'pwr': '0'},
        ),
        (
            ['mode', 'pm25'], 
            b'kzSvc/UvLcCNJAoiwJNQX7U2Al2MN95dMEQzrxvC8Pccvddc6sY90h7OVXS+rPRBf51tKSxmtcuOyo+6eZhBan'
            b'HTNVgBslRblATZknR098OM2mvXiYaY0LS70D/nzlcWhT8vB0grLGJWwHii+danT0HXpENFuLdWpYW0bw4bAFk=',
            {'mode': 'A', 'pm25': 8},
        ),
        (
            ['om', 'pwr', 'cl', 'aqil', 'uil', 'dt', 'dtrs', 'mode', 'pm25', 'iaql', 'aqit', 'ddp', 'err'], 
            b'6blRtD8SfuMlKGx4H4DHcAQ00WDLBLpSD4SrSG4JkHhKNS/cd34DkTkVIUPZ3ffVTfmriEbecQvgtHj7MuI1P/'
            b'PeX02OI2gtZBruZjleHTQxBbyt+pihXmxTkhtyEtZrXANkKk5NdRzjSxL8fNbj2rzzYJ0utANVA8sXidwWQLY=',
            {'om': '0', 'pwr': '0', 'cl': False, 'aqil': 50, 'uil': '1', 'dt': 0, 'dtrs': 0, 
             'mode': 'A', 'pm25': 8, 'iaql': 2, 'aqit': 0, 'ddp': '1', 'err': 193},
        ),
    )
    @unpack
    @patch('requests.get')
    def test_get_data_from_air_purifier(self, parameters, recv_data, decoded_data, mock_get):
        mock_get.return_value = self._mock_response(content=recv_data)
        self.philips_air_purifier.session_key = self.session_key
        if isinstance(parameters, list):
            response_data = self.philips_air_purifier.get(*parameters)
        else:
            response_data = self.philips_air_purifier.get()
        self.assertEqual(response_data, decoded_data)

    @data(
        (
            {'pwr':'1'}, 
            b'dEbVcp5KebREQVf0CdRmiYOjNPrwov3jv/V5YUWrgUB0HGu4X+2RzYF0bphte2bxgy2LUHSrkmXFrFqRiHbnkH'
            b'FPbmOb+Wh1Bys440qmtaHxyiNZPuhR6hhzBayck2scWsHB8pKu+beszJix5IWOhcjJJXjZQIg75+9o/+i2X9U=',
            {'om': '1', 'pwr': '1', 'cl': False, 'aqil': 50, 'uil': '1', 'dt': 0, 'dtrs': 0, 
             'mode': 'A', 'pm25': 5, 'iaql': 2, 'aqit': 0, 'ddp': '1', 'err': 193},
        ),
        (
            {'om': '1', 'uil': '1', 'mode': 'A', 'pwr': '0'}, 
            b'eKXePLOALZpwUVpP1XLpf+WIgTFwkHPA83Hf6Uw/iP3aXwPlGO6WBeasmYRivS24OEP28n3yh69AgzyZ7dl9qw'
            b'mw5EIyhJNhqvLUlfMOijFeFG6k2qE666qDAQieJ2Dfaq/Qf0wgt1hTIAmPhFabnUh+k1OtMebXIZ5IGgk9GXI=',
            {'om': '0', 'pwr': '0', 'cl': False, 'aqil': 50, 'uil': '1', 'dt': 0, 'dtrs': 0, 
             'mode': 'A', 'pm25': 3, 'iaql': 1, 'aqit': 0, 'ddp': '1', 'err': 193},
        ),
    )
    @unpack
    @patch('requests.put')
    def test_set_parameters_in_air_purifier(self, parameters, recv_data, decoded_data, mock_put):
        mock_put.return_value = self._mock_response(content=recv_data)
        self.philips_air_purifier.session_key = self.session_key
        response_data = self.philips_air_purifier.set(**parameters)
        self.assertEqual(response_data, decoded_data)

    def tearDown(self):
        pass

    def _mock_response(self, status=200, content={}):
        mock_resp = Mock()
        mock_resp.status_code = status
        mock_resp.content = content
        return mock_resp


@ddt
class TestFilterRequestedData(unittest.TestCase):

    @data(
        {'pwrr': None},
        {'Om': None},
        {'aqqqqil': None},
        {'blow': None},
        {'split': None},
        {'': None},
        {1: None},
    )
    def test_invalid_parameters_names(self, name):
        error_message = "Unrecoginized '{}' parameter. Allowed parameters: pwr, om, aqil, uil, ddp, mode".format(
            list(name.keys())[0]
        )
        self.assertRaisesRegex(ParameterNotRecognizedError, error_message, filter_requested_data, name)

    @data(
        {'pwr': '0'},
        {'pwr': '1'},
        {'om': '1'},
        {'om': '2'},
        {'om': '3'},
        {'om': 's'},
        {'aqil': 1},
        {'aqil': 100},
        {'aqil': 50},
        {'uil': '0'},
        {'uil': '1'},
        {'ddp': '0'},
        {'ddp': '1'},
        {'mode': 'A'},
        {'mode': 'P'},
        {'mode': 'B'},
    )
    def test_valid_parameters_values(self, parameters):
        filtered_parameters = filter_requested_data(parameters)
        self.assertEqual(filtered_parameters, parameters)

    @data(
        {'pwr': 'a'},
        {'pwr': '2'},
        {'pwr': 1},
    )
    def test_invalid_pwr_parameter_values(self, parameters):
        error_message = "Value '{}' is not allowed.\n{}".format(
            list(parameters.values())[0], ALLOWED_PARAMETERS_TO_SET['pwr']['help']
        )
        self.assertRaisesRegex(ParameterValueError, error_message, filter_requested_data, parameters)

    @data(
        {'om': '-1'},
        {'om': 'F'},
        {'om': 1},
    )
    def test_invalid_om_parameter_values(self, parameters):
        error_message = "Value '{}' is not allowed.\n{}".format(
            list(parameters.values())[0], ALLOWED_PARAMETERS_TO_SET['om']['help']
        )
        self.assertRaisesRegex(ParameterValueError, error_message, filter_requested_data, parameters)

    @data(
        {'aqil': 0},
        {'aqil': 101},
        {'aqil': -5},
        {'aqil': 120},
    )
    def test_invalid_aqil_parameter_values(self, parameters):
        error_message = "Value '{}' is not allowed.\n{}".format(
            list(parameters.values())[0], ALLOWED_PARAMETERS_TO_SET['aqil']['help']
        )
        self.assertRaisesRegex(ParameterValueError, error_message, filter_requested_data, parameters)

    @data(
        {'uil': 0},
        {'uil': '-1'},
        {'uil': 'D'},
    )
    def test_invalid_uil_parameter_values(self, parameters):
        error_message = "Value '{}' is not allowed.\n{}".format(
            list(parameters.values())[0], ALLOWED_PARAMETERS_TO_SET['uil']['help']
        )
        self.assertRaisesRegex(ParameterValueError, error_message, filter_requested_data, parameters)
    
    @data(
        {'ddp': 0},
        {'ddp': '-2'},
        {'ddp': '3'},
    )
    def test_invalid_ddp_parameter_values(self, parameters):
        error_message = "Value '{}' is not allowed.\n{}".format(
            list(parameters.values())[0], ALLOWED_PARAMETERS_TO_SET['ddp']['help']
        )
        self.assertRaisesRegex(ParameterValueError, error_message, filter_requested_data, parameters)

    @data(
        {'mode': 'C'},
        {'mode': 'i'},
        {'mode': 'a'},
        {'mode': -1},
    )
    def test_invalid_aqil_parameter_values(self, parameters):
        error_message = "Value '{}' is not allowed.\n{}".format(
            list(parameters.values())[0], ALLOWED_PARAMETERS_TO_SET['mode']['help']
        )
        self.assertRaisesRegex(ParameterValueError, error_message, filter_requested_data, parameters)
