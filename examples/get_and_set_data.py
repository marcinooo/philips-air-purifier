from philips_air_purifier_ac2889 import AirPurifier


philips_air_purifier = AirPurifier(host='192.168.1.21').connect()

data = philips_air_purifier.get()
print(data)

print('Power on...')
philips_air_purifier.set(pwr='1')  # power on

if isinstance(data['om'], int) and int(data['om']) <= 2:
    new_speed = str(int(data['om']) + 1)
    print(f'Increasing device speed from {data["om"]} to {new_speed}...')

else:
    new_speed = '1'
    print(f'Decreasing device speed from {data["om"]} to {new_speed}...')

philips_air_purifier.set(mode='M', om=new_speed)
