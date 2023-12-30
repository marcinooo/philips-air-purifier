from philips_air_purifier_ac2889 import AirPurifier


HOST = '192.168.1.21'

philips_air_purifier = AirPurifier(host=HOST, no_proxy=HOST).connect()

data = philips_air_purifier.network()
print(data)
