# coding: utf-8

from setuptools import setup, find_packages

NAME = "aops-diana"
VERSION = "1.3.0"

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
    'adtk',
]

setup(
    name=NAME,
    version=VERSION,
    description="aops-diana",
    install_requires=REQUIRES,
    packages=find_packages(),
    data_files=[
        ('/etc/aops', ['conf/diana.ini', 'conf/diana_hosts.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/ai_template1.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/tpcc_intelligent.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/mysql_intelligent.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/lvs_intelligent.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/lvs_network_error_tree.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/mysql_network_error_tree.json']),
        ('/etc/aops/algorithm', ['conf/algorithm/tpcc_network_error_tree.json']),
        (
            '/etc/aops/algorithm/intelligent/tpcc',
            ['conf/model/intelligent/tpcc/rule1_gala_gopher_net_tcp_retrans_segs'],
        ),
        ('/etc/aops/algorithm/intelligent/tpcc', ['conf/model/intelligent/tpcc/rule1_gala_gopher_cpu_net_rx']),
        ('/etc/aops/algorithm/intelligent/tpcc', ['conf/model/intelligent/tpcc/rule2_gala_gopher_nic_tc_backlog']),
        (
            '/etc/aops/algorithm/intelligent/mysql',
            ['conf/model/intelligent/mysql/rule1_gala_gopher_net_tcp_curr_estab'],
        ),
        ('/etc/aops/algorithm/intelligent/mysql', ['conf/model/intelligent/mysql/rule1_gala_gopher_cpu_net_rx']),
        ('/etc/aops/algorithm/intelligent/mysql', ['conf/model/intelligent/mysql/rule2_gala_gopher_nic_tc_backlog']),
        ('/etc/aops/algorithm/intelligent/mysql', ['conf/model/intelligent/mysql/rule2_gala_gopher_nic_rx_packets']),
        ('/etc/aops/algorithm/intelligent/lvs', ['conf/model/intelligent/lvs/rule1_gala_gopher_nic_rx_packets']),
        ('/etc/aops/algorithm/intelligent/lvs', ['conf/model/intelligent/lvs/rule1_gala_gopher_cpu_net_rx']),
        ('/etc/aops/algorithm/intelligent/lvs', ['conf/model/intelligent/lvs/rule2_gala_gopher_nic_tc_backlog']),
        ('/usr/lib/systemd/system', ['aops-diana.service']),
        ("/opt/aops/database", ["database/diana.sql"]),
    ],
    scripts=['aops-diana'],
    zip_safe=False,
)
