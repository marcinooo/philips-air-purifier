import os
from setuptools import find_packages, setup


def read(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path: str) -> str:
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError('Unable to find version string.')


setup(
    name='philips_air_purifier',
    version=get_version('src/philips_air_purifier/__init__.py'),
    description='A simple client to control the Philips AC2889 air purifier.',
    author='Marcin Wachacki',
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages(
        where='src',
        exclude=['tests*', 'examples*'],
    ),
    install_requires=[
        'requests'
    ],
    py_modules=['philips_air_purifier'],
)
