# coding: utf-8

from setuptools import setup, find_packages

NAME = "aops-diana"
VERSION = "1.1.0"

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
    'scipy',
    'adtk'
]

setup(
    name=NAME,
    version=VERSION,
    description="aops-diana",
    install_requires=REQUIRES,
    packages=find_packages(),
    data_files=[
        ('/etc/aops', ['conf/diana.ini', 'conf/diana_hosts.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/ai_template1.json', 'conf/algorithm/ai_template2.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/tpcc_intelligent.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/mysql_intelligent.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/lvs_intelligent.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/lvs_network_error_tree.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/mysql_network_error_tree.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/tpcc_network_error_tree.json']),
        ('/usr/lib/systemd/system', ['aops-diana.service'])
    ],
    entry_points={
        'console_scripts': ['aops-diana=diana.manage:main']
    },
    zip_safe=False
)
