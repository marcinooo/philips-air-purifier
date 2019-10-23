import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(current_dir), 'src'))

from philips_air_purifier import PhilipsAirPurifier


HOST = '192.168.1.21'

philips_air_purifier = PhilipsAirPurifier().connect()
data = philips_air_purifier.get()
print('Your air conditions:\n', data, '\n')

print('Power on device...')
philips_air_purifier.set(pwr='1')

print('Setting speed...')

if isinstance(data['om'], int) and int(data['om']) <= 2:
    new_speed = str(int(data['om']) + 1)
    print('Increasing device speed from {} to {}...'.format(data['om'], new_speed))
    philips_air_purifier.set(mode='M', om=new_speed)
else:
    print('Decreasing device speed from {} to 1...'.format(data['om']))
    philips_air_purifier.set(mode='M', om='1')
