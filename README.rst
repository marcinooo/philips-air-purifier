===============================
Philips Air Purifier Controller
===============================

:Author: marcinooo
:Tags: philips air purifier, python, client, api

:abstract: 

    A simple client to control the Philips AC2889 air purifier.

.. contents ::


Description
===========

The package is a simple interface for controlling the Philips AC2889 air purifier. It allows read parameters and set parameters.

Philips AC2889:

.. image:: philips_air_purifier_ac2889.png
    :alt: Philips AC2889
    :scale: 20%

|

Installation
============

Install from PyPi:

``pip install philips-air-purifier-ac2889``

Install from github:

``$ pip install git+https://github.com/marcinooo/philips-air-purifier.git``

|

Usage
=====

Simple example:

.. code:: python

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


List of all allowed parameters you can find in dictionary: 

.. code:: python

    import pprint
    from philips_air_purifier import ALLOWED_PARAMETERS


    pprint.pprint(ALLOWED_PARAMETERS)


See __examples__ directory :grinning:.

.. note::

    Some parameters must be set together:

    - setting speed in manual mode: ``philips_air_purifier.set(mode='M', om='2')``

    - setting manual with speed: ``philips_air_purifier.set(mode='M', om='s')``


|

License
=======

license_ (MIT)

.. _license: https://github.com/marcinooo/philips-air-purifier/blob/master/LICENSE.txt

