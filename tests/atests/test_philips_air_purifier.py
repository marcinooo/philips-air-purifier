import os
import sys
import unittest
import time
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'src'))

from philips_air_purifier import PhilipsAirPurifier
from philips_air_purifier import ALLOWED_PARAMETERS_TO_SET


class TestAirPurifier(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger(__name__)
        logging.basicConfig(format='[%(asctime)s]%(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', 
                            level=logging.INFO)

        cls.host = '192.168.1.21'
        cls.philips_air_purifier = PhilipsAirPurifier(host=cls.host).connect()
        _ = cls.philips_air_purifier.set(pwr='1')
        time.sleep(5)

    def test_get_data_from_philips_air_purifier(self):
        self._log_info_from_test_case('Getting device data...')
        data = self.philips_air_purifier.get()
        required_parameters = ['om', 'pwr', 'cl', 'aqil', 'uil', 'dt', 'dtrs', 
                               'mode', 'pm25', 'iaql', 'aqit', 'ddp', 'err']
        for parameter in required_parameters:
            self.assertIn(parameter, data)

    def test_set_speed(self):
        self._log_info_from_test_case('Switching device in anti-pollution mode...')
        speeds = ALLOWED_PARAMETERS_TO_SET['om']['values']
        for speed in speeds:
            self._log_info_from_test_case('Setting speed to {}...'.format(speed))
            data = self.philips_air_purifier.set(mode='M', om=speed)
            time.sleep(7)
            self.assertEqual(data['om'], speed)

    def test_turn_off_on_display(self):
        self._log_info_from_test_case('Setting display off...')
        data = self.philips_air_purifier.set(uil='0')
        self.assertEqual(data['uil'], '0')
        time.sleep(2)
        self._log_info_from_test_case('Setting display on...')
        data = self.philips_air_purifier.set(uil='1')
        self.assertEqual(data['uil'], '1')
        time.sleep(2)

    def test_set_pollution_display_mode(self):
        self._log_info_from_test_case('Setting IAI pollution display mode...')
        data = self.philips_air_purifier.set(ddp='1')
        self.assertEqual(data['ddp'], '1')
        time.sleep(5)
        self._log_info_from_test_case('Setting pm25 pollution display mode...')
        data = self.philips_air_purifier.set(ddp='0')
        self.assertEqual(data['ddp'], '0')
        time.sleep(5)

    def test_device_mode(self):
        self._log_info_from_test_case('Setting anti-allergen mode...')
        data = self.philips_air_purifier.set(mode='A')
        self.assertEqual(data['mode'], 'A')
        time.sleep(5)
        self._log_info_from_test_case('Setting anti-pollution mode...')
        data = self.philips_air_purifier.set(mode='P')
        self.assertEqual(data['mode'], 'P')
        time.sleep(5)
        self._log_info_from_test_case('Setting antivirus mode...')
        data = self.philips_air_purifier.set(mode='B')
        self.assertEqual(data['mode'], 'B')
        time.sleep(5)
        self._log_info_from_test_case('Setting manual mode...')
        data = self.philips_air_purifier.set(mode='M', om='s')
        self.assertEqual(data['mode'], 'M')
        time.sleep(5)

    def _log_info_from_test_case(self, msg):
        self.logger.info('[{}] {}'.format(self.id(), msg))

    @classmethod
    def tearDownClass(cls):
        _ = cls.philips_air_purifier.set(pwr='0')
