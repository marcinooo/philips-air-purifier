"""
Library to control Philips AC2889 air purifier.
"""

from ._air_purifier import AirPurifier
from ._utils import ALLOWED_PARAMETERS
from . import errors


__author__ = 'marcinooo'
__maintainer__ = 'marcinooo'
__version__ = '2.0.0'


__all__ = [
    'AirPurifier',
    'ALLOWED_PARAMETERS',
    'errors',
]
