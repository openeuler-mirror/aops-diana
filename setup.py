# coding: utf-8

from setuptools import setup, find_packages

NAME = "aops-diana"
VERSION = "2.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    'marshmallow>=3.13.0',
    'Flask',
    'Flask-RESTful',
    'Flask-APScheduler',
    'numpy',
    'pandas',
    'prometheus_api_client',
    'setuptools',
    'requests',
    'SQLAlchemy',
    'PyMySQL',
    'scipy'
]

setup(
    name=NAME,
    version=VERSION,
    description="aops-diana",
    install_requires=REQUIRES,
    packages=find_packages(),
    data_files=[
        ('/etc/aops', ['conf/diana.ini', 'conf/diana_hosts.json']),
        ('/usr/lib/systemd/system', ['aops-diana.service'])
    ],
    entry_points={
        'console_scripts': ['aops-diana=diana.manage:main']
    },
    zip_safe=False
)
