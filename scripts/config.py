#coding:utf-8
CONFIG = {
        'tpcc': {
            'ip': '172.168.193.208',
            'interface': 'enp1s0',
            'chaosblade_port': 7070,
            'benchmarksql': {
                'run_filedir': '/home/wgg/software/benchmarksql5.0-for-mysql/run/',
                'run_cmd': '/home/wgg/software/benchmarksql5.0-for-mysql/run/runBenchmark.sh props.conf > /home/wgg/software/benchmarksql5.0-for-mysql/run/run.log',
                'log_file': '/home/wgg/software/benchmarksql5.0-for-mysql/run/run.log'
                }
            },
        'mysqlA': {
            'ip': '172.168.108.236',
            'interface': 'enp1s0',
            'chaosblade_port': 7070
            },
        'mysqlB': {
            'ip': '172.168.108.112',
            'interface': 'enp1s0',
            'chaosblade_port': 7070
            },
        'VIP': '172.168.108.134',
        'lvs': {
            'ip': '172.168.108.111',
            'interface': 'enp1s0',
            'chaosblade_port': 7070
            },
        'aops': {
            'ip': '172.168.201.40',
            'interface': 'enp1s0',
            'chaosblade_port': 7070
            },
        'fault_inject_file': './test_fault_inject_recording.txt',
        'fault_inject_log': './test_fault_inject_recording.log'
        }
