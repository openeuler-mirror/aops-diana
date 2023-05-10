#coding:utf-8
import requests, json
import sys
import time,datetime
import schedule 
import random
from functools import partial
import paramiko
import threading
import logging
import re

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


def get_node_name(fault_node):
    node_name = {
            '1': 'tpcc',
            '2': 'mysqlA',
            '3': 'mysqlB',
            '4': 'lvs',
            '5': 'aops'
            }
    
    return node_name[fault_node]


def get_fault_type_name(fault_type):
    fault_type_name = {
            '1': 'interrupt',
            '2': 'delay',
            '3': 'reorder',
            '4': 'detached'
            }
    
    return fault_type_name[fault_type]


def chaos_inject_network(host, port, params, time_out, fault_node, fault_type):
    
    url = 'http://' + host +':' + str(port) + '/chaosblade'
    response = requests.get(url, params=params)
    inject_time = datetime.datetime.now()
    inject_timestamp = int(inject_time.timestamp())
    inject_time_format = datetime.datetime.strftime(inject_time, "%Y-%m-%d %H:%M:%S")
    success = json.loads(response.text).get('success')
    
    if not success:
        logging.error("inject_time_format + ' inject unsuccessfully...")
        print(inject_time_format + ' inject unsuccessfully...')
        sys.exit(0)
    
    inject_end_time = inject_time + datetime.timedelta(seconds = time_out)
    inject_end_timestamp = int(inject_end_time.timestamp())
    
    file_name = CONFIG['fault_inject_file']

    try:
        file_handle = open(file_name, mode='a+')
        file_handle.write(
            '' + str(inject_timestamp) + ' ' + str(inject_end_timestamp) + ' ' + 'node' + ' ' + get_node_name(
                str(fault_node)) + ' ' + get_fault_type_name(str(fault_type)) + '\n')
        file_handle.close()
    except PermissionError:
        pass

    result = json.loads(response.text).get('result')
    print(inject_time_format + ' inject network fault ' + get_fault_type_name(str(fault_type)) + ' in ' + get_node_name(str(fault_node)) + ' successfully...')
    print(params)
    print(result)
    logging.info(inject_time_format + ' inject network fault ' + get_fault_type_name(str(fault_type)) + ' in ' + get_node_name(str(fault_node)) + ' successfully...')
    logging.info(params)
    logging.info(result)


def ssh_cmd(target_host, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=target_host, username='USERNAME', password='PASSWORD')
    try:
        c = ""
        for c in cmd:
            stdin, stdout, stderr = client.exec_command(c)
    except Exception as e:
        print(e)
        logging.info(e)
        if '-F' in c:
            print('iptables fault cancel unsuccessfully...')
            logging.error('iptables fault cancel unsuccessfully...')
        else:
            print('iptables fault inject unsuccessfully...')
            logging.error('iptables fault inject unsuccessfully...')
        sys.exit(0)
    client.close()


def check_mysql_running(mysql_ip):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # check if mysql is running by 'ipvsadm -ln' on lvs
    lvs_ip = CONFIG['lvs']['ip']
    client.connect(hostname=lvs_ip, username='USERNAME', password='PASSWORD')
    mysql_status_check_cmd = 'ipvsadm -ln'
    stdin, stdout, stderr = client.exec_command(mysql_status_check_cmd)
    
    mysql_status_info = stdout.read().decode('utf-8')
    print(mysql_status_info)
    info_list = str(mysql_status_info).split('->')
    current_active_conn = 0
    for info in info_list:
        if info.find(mysql_ip)!=-1:
            nums = [int(s) for s in re.findall(r'\b\d+\b', info)]
            current_active_conn = nums[6]
            continue

    if current_active_conn == 0:
        return False
    return True


def check_tpcc_status(tpcc_ip):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=tpcc_ip, username='USERNAME', password='PASSWORD')
    try:
        # wait for the state to stabilize
        time.sleep(30)

        # monitor whether the log file changes within 1 minute
        log_file = CONFIG['tpcc']['benchmarksql']['log_file']
        log_info_cmd = 'cat ' + log_file + ' | tail -n 10'
        stdin, stdout, stderr = client.exec_command(log_info_cmd)
        first_content = stdout.read().decode('utf-8')
        print(first_content)
        print("monitor the log for 1 minutes...")
        logging.info(first_content)
        logging.info("monitor the log for 1 minutes...")
        time.sleep(60)

        stdin, stdout, stderr = client.exec_command(log_info_cmd)
        second_content = stdout.read().decode('utf-8')
        print(second_content)
        logging.info(second_content)
        
        # if the content is inconsistent, there is no need to restart tpcc
        if first_content!=second_content:
            print('60 seconds ago and current is not the same')
            logging.info('60 seconds ago and current is not the same')
            # tpcc not restarted
            return False
        else:
            print('60 seconds ago and current is the same')
            logging.info('60 seconds ago and current is the same')          

        # kill tpcc related progress
        print('the tpcc service has stuck and is restarting...')
        logging.info('the tpcc service has stuck and is restarting...')
        kill_run_sh_cmd1 = "ps -ef | grep runBenchmark | grep -v 'grep' | awk '{print $2}' | xargs kill -9"
        stdin, stdout, stderr = client.exec_command(kill_run_sh_cmd1)
        print(stdout.read().decode('utf-8'))
        logging.info(stdout.read().decode('utf-8'))

        kill_all_proc_cmd2 = "ps -ef | grep mysql | grep -v grep | grep -v run_mysql.sh | awk '{print $2}' | xargs kill -9"
        stdin, stdout, stderr = client.exec_command(kill_all_proc_cmd2)
        print(stdout.read().decode('utf-8'))
        print("wait 30 seconds...")
        logging.info(stdout.read().decode('utf-8'))
        logging.info("wait 30 seconds...")
        time.sleep(30)

        again_run_cmd = 'cd '+ CONFIG['tpcc']['benchmarksql']['run_filedir'] + ' && ls && nohup bash '+ CONFIG['tpcc']['benchmarksql']['run_cmd'] + ' & \n'
        invoke = client.invoke_shell()
        invoke.send(again_run_cmd)
        time.sleep(2)
        stdin, stdout, stderr = client.exec_command('ps -ef | grep runBench')
        print(stdout.read().decode('utf-8'))
        print('the tpcc has restarted, please check whether the process is running normally...')
        logging.info(stdout.read().decode('utf-8'))
        logging.info('the tpcc has restarted, please check whether the process is running normally...')

    except Exception as e:
        print('client check out error')
        logging.error('client check out error')
        sys.exit(0)

    client.close()
    # tpcc restarted
    return True


def iptables_fault(target_host, cmd, fault_node, fault_type, time_out, check_tpcc=False):
    ssh_cmd(target_host, cmd)
     
    file_name = CONFIG['fault_inject_file']
    inject_time = datetime.datetime.now()
    inject_timestamp = int(inject_time.timestamp())
    inject_time_format = datetime.datetime.strftime(inject_time, "%Y-%m-%d %H:%M:%S")
    inject_end_time = inject_time + datetime.timedelta(seconds = time_out)
    inject_end_timestamp = int(inject_end_time.timestamp())
    try:
        file_handle = open(file_name, mode='a+')
        file_handle.write(
            '' + str(inject_timestamp) + ' ' + str(inject_end_timestamp) + ' ' + 'node' + ' ' + get_node_name(
                str(fault_node)) + ' ' + get_fault_type_name(str(fault_type)) + '\n')
        file_handle.close()
    except PermissionError:
        pass

    print(inject_time_format + ' iptables inject network fault ' + get_fault_type_name(str(fault_type)) + ' in ' + get_node_name(str(fault_node)) + ' successfully...')
    logging.info(inject_time_format + ' iptables inject network fault ' + get_fault_type_name(str(fault_type)) + ' in ' + get_node_name(str(fault_node)) + ' successfully...')
    params = {'cmd': ' '.join(cmd) + ' --time-out ' + str(time_out)}
    print(params)
    logging.info(params)
    time.sleep(time_out)

    ssh_cmd(target_host, ['iptables -F'])
    

def inject_iptables_and_check_tpcc(target_host, fault_cmd, fault_node, fault_type, time_out, tpcc_ip):
    tpcc_ip = CONFIG['tpcc']['ip']

    t1 = threading.Thread(target=iptables_fault, args=(target_host, fault_cmd, fault_node, fault_type, time_out, True))
    # after injecting the fault, if the client is in the stop access state, restart the tpcc
    t2 = threading.Thread(target=check_tpcc_status, args=(tpcc_ip,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()


def random_network_fault_params_for_tpcc(target_host, blade_port, fault_type=None):
    
    interface = CONFIG['tpcc']['interface']
    exclude_ip = CONFIG['aops']['ip']

    time_local = random.uniform(150,200)
    time_out = random.randrange(120,180)
    percent = random.randrange(15, 20)
    offset = random.uniform(0,100)
    correlation = random.randint(0, 100)
    gap = random.randint(1, 5)

    interrupt_params = {'cmd':'create network loss --percent 100 --interface %s  --timeout %s  --exclude-ip %s' % \
        (interface, time_out, exclude_ip) }
    delay_params = {'cmd':'create network delay --time %s --offset %s --interface %s   --timeout %s --exclude-ip %s' % \
         (time_local, offset, interface, time_out, exclude_ip) }
    reorder_params = {'cmd':'create network reorder --correlation %s --percent %s --gap %s  --interface %s  --timeout %s --exclude-ip %s' % \
         (correlation, percent, gap, interface, time_out, exclude_ip) }

    params = [interrupt_params, delay_params, reorder_params]
    if fault_type is None:
        fault_type = random.choice([1, 2, 3])
    fault_node = 1
    
    choosed_params = params[fault_type-1]
    chaos_inject_network(target_host, blade_port, choosed_params, time_out, fault_node, fault_type)


def random_network_fault_params_for_mysqlA(target_host, blade_port, fault_type=None):
    is_mysql_running = check_mysql_running(target_host)

    if is_mysql_running is False:
        print('the active connection on the current mysql host is 0, please inject fault to another mysql host...')
        logging.info('the active connection is 0, please inject fault to another mysql host...')
        return
    
    interface = CONFIG['mysqlA']['interface']
    exclude_ip = CONFIG['aops']['ip']

    time_local = random.uniform(150,200)
    time_out = random.randrange(180,240)
    percent = random.randrange(15, 20)
    offset = random.uniform(0,100)
    correlation = random.randint(0, 100)
    gap = random.randint(1, 5)

    interrupt_params = {'cmd':'create network loss --percent 100 --interface %s  --timeout %s --exclude-ip %s' % \
         (interface, time_out, exclude_ip) }
    delay_params = {'cmd':'create network delay --time %s --offset %s --interface %s   --timeout %s --exclude-ip %s' % \
        (time_local, offset, interface, time_out, exclude_ip) }
    reorder_params = {'cmd':'create network reorder --correlation %s --percent %s --gap %s --interface %s --timeout %s --exclude-ip %s' % \
        (correlation, percent, gap, interface, time_out, exclude_ip) }

    params = [interrupt_params, delay_params, reorder_params]
    if fault_type is None:
        fault_type = random.choice([1, 2, 3])
    
    fault_node = 2
    choosed_params = params[fault_type-1]
    if fault_type in [2, 3]:
        chaos_inject_network(target_host, blade_port, choosed_params, time_out, fault_node, fault_type)
    else:
        lvs_ip = CONFIG['lvs']['ip']
        fault_cmd = 'iptables -I INPUT -s ' + lvs_ip + ' -j DROP'
        fault_cmd = [fault_cmd]
        tpcc_ip = CONFIG['tpcc']['ip']
        inject_iptables_and_check_tpcc(target_host, fault_cmd, fault_node, fault_type, time_out, tpcc_ip)
        
        # after eliminating the fault, if tpcc is in the normal access state, it is normal
        print("check tpcc...")
        logging.info("check tpcc...")
        result = check_tpcc_status(tpcc_ip)
        
        # the log content is inconsistent, indicating that tpcc is already in a normal access state
        if result == False:
            print("tpcc is normal")
            logging.info("tpcc is normal")
        else :
            print("tpcc does not return to the normal state, has restarted...")
            logging.info("tpcc does not return to the normal state, has restarted...")


def random_network_fault_params_for_mysqlB(target_host, blade_port, fault_type=None):
    # check mysqlB is running
    is_mysql_running = check_mysql_running(target_host)
    if is_mysql_running is False:
        print('the active connection on the current mysql host is 0, please inject fault to another mysql host...')
        logging.info('the active connection is 0, please inject fault to another mysql host...')
        return
    
    interface = CONFIG['mysqlB']['interface']
    exclude_ip = CONFIG['aops']['ip']

    time_local = random.uniform(150,200)
    time_out = random.randrange(180,240)
    percent = random.randrange(15, 20)
    offset = random.uniform(0,100)
    correlation = random.randint(0, 100)
    gap = random.randint(1, 5)
    
    interrupt_params = {'cmd':'create network loss --percent 100 --interface %s  --timeout %s --exclude-ip %s' % \
         (interface, time_out, exclude_ip) }
    delay_params = {'cmd':'create network delay --time %s --offset %s --interface %s   --timeout %s --exclude-ip %s' % \
         (time_local, offset, interface, time_out, exclude_ip) }
    reorder_params = {'cmd':'create network reorder --correlation %s --percent %s --gap %s --interface %s --timeout %s --exclude-ip %s' % \
         (correlation, percent, gap, interface, time_out, exclude_ip) }
    
    params = [interrupt_params, delay_params, reorder_params]
    if fault_type is None:
        fault_type = random.choice([1, 2, 3])
 
    choosed_params = params[fault_type-1]
    fault_node = 3
    if fault_type in [2, 3]:
        chaos_inject_network(target_host, blade_port, choosed_params, time_out, fault_node, fault_type)
    else:
        lvs_ip = CONFIG['lvs']['ip']
        fault_cmd = 'iptables -I INPUT -s ' + lvs_ip + ' -j DROP'
        fault_cmd = [fault_cmd]
        tpcc_ip = CONFIG['tpcc']['ip']
        inject_iptables_and_check_tpcc(target_host, fault_cmd, fault_node, fault_type, time_out, tpcc_ip)
        
        # after eliminating the fault, if tpcc is in the normal access state, it is normal
        print("check tpcc...")
        logging.info("check tpcc...")
        result = check_tpcc_status(tpcc_ip)
        # the log content is inconsistent, indicating that tpcc is already in a normal access state
        if result == False:
            print("tpcc is normal")
            logging.info("tpcc is normal")
        else :
            print("tpcc does not return to the normal state, has restarted...")
            logging.info("tpcc does not return to the normal state, has restarted...")


def random_network_fault_params_for_lvs(target_host, blade_port, fault_type=None):
    
    interface = CONFIG['lvs']['interface']
    exclude_ip = CONFIG['aops']['ip']

    local_port = 3306
    time_local = random.uniform(150,200)
    time_out = random.randrange(180,240)
    percent = random.randrange(15, 20)
    offset = random.uniform(0,100)
    correlation = random.randint(0, 100)
    gap = random.randint(1, 5)
    
    interrupt_params = {'cmd':'create network loss --percent 100 --interface %s  --local-port %s --timeout %s' % \
         (interface, local_port, time_out) }
    delay_params = {'cmd':'create network delay --time %s --offset %s --interface %s   --timeout %s --exclude-ip %s' % \
         (time_local, offset, interface, time_out, exclude_ip) }
    reorder_params = {'cmd':'create network reorder --correlation %s --percent %s --gap %s --interface %s --timeout %s --exclude-ip %s' % \
         (correlation, percent, gap, interface, time_out, exclude_ip) }
    
    params = [interrupt_params, delay_params, reorder_params]
    if fault_type is None:
        fault_type = random.choice([1, 2, 3])
   
    choosed_params = params[fault_type-1]
    fault_node = 4
    if fault_type in [2, 3]:
        chaos_inject_network(target_host, blade_port, choosed_params, time_out, fault_node, fault_type)
    else:
        mysqlA_ip = CONFIG['mysqlA']['ip']
        mysqlB_ip = CONFIG['mysqlB']['ip']
        tpcc_ip = CONFIG['tpcc']['ip']
        fault_cmd = [
                'iptables -I INPUT -s ' + mysqlA_ip + ' -j DROP',
                'iptables -I INPUT -s ' + mysqlB_ip + ' -j DROP',
                'iptables -I INPUT -s ' + tpcc_ip + ' -j DROP'
                ]
        iptables_fault(target_host, fault_cmd, fault_node, fault_type, time_out)


def random_network_fault_params_for_aops(target_host, blade_port):
    
    time_out = random.randrange(180,240)

    # monitor host
    tpcc_ip = CONFIG['tpcc']['ip']
    mysqlA_ip = CONFIG['mysqlA']['ip']
    mysqlB_ip = CONFIG['mysqlB']['ip']
    lvs_ip = CONFIG['lvs']['ip']
    
    tpcc_fault_cmd = 'iptables -I INPUT -s ' + tpcc_ip + ' -j DROP'
    tpcc_fault_cmd = [tpcc_fault_cmd]
    mysqlA_fault_cmd = 'iptables -I INPUT -s ' + mysqlA_ip + ' -j DROP'
    mysqlA_fault_cmd = [mysqlA_fault_cmd]
    mysqlB_fault_cmd = 'iptables -I INPUT -s ' + mysqlB_ip + ' -j DROP'
    mysqlB_fault_cmd = [mysqlB_fault_cmd]
    lvs_fault_cmd = 'iptables -I INPUT -s ' + lvs_ip + ' -j DROP'
    lvs_fault_cmd = [lvs_fault_cmd]
    
    fault_type = 4
    
    fault_node = random.choice([1,2,3,4])
    
    cmds = [tpcc_fault_cmd, mysqlA_fault_cmd, mysqlB_fault_cmd, lvs_fault_cmd]
    fault_cmd = cmds[fault_node-1]

    iptables_fault(target_host, fault_cmd, fault_node, fault_type, time_out)

def random_fault():
    tpcc_host = CONFIG['tpcc']['ip']
    tpcc_chaosblade_port = CONFIG['tpcc']['chaosblade_port']
    mysqlA_host = CONFIG['mysqlA']['ip']
    mysqlA_chaosblade_port = CONFIG['mysqlA']['chaosblade_port']
    mysqlB_host = CONFIG['mysqlB']['ip']
    mysqlB_chaosblade_port = CONFIG['mysqlB']['chaosblade_port']
    lvs_host = CONFIG['lvs']['ip']
    lvs_chaosblade_port = CONFIG['lvs']['chaosblade_port']
    aops_host = CONFIG['aops']['ip']
    aops_chaosblade_port = CONFIG['aops']['chaosblade_port']
    
    fun = [
            partial(random_network_fault_params_for_tpcc, tpcc_host, tpcc_chaosblade_port),
            partial(random_network_fault_params_for_mysqlA, mysqlA_host, mysqlA_chaosblade_port),
            partial(random_network_fault_params_for_mysqlB, mysqlB_host, mysqlB_chaosblade_port),
            partial(random_network_fault_params_for_lvs, lvs_host, lvs_chaosblade_port),
            partial(random_network_fault_params_for_aops, aops_host, aops_chaosblade_port)
            ]
    random.choice(fun)()


def single_fault(fault_node, fault_type):
    tpcc_host = CONFIG['tpcc']['ip']
    tpcc_chaosblade_port = CONFIG['tpcc']['chaosblade_port']
    mysqlA_host = CONFIG['mysqlA']['ip']
    mysqlA_chaosblade_port = CONFIG['mysqlA']['chaosblade_port']
    mysqlB_host = CONFIG['mysqlB']['ip']
    mysqlB_chaosblade_port = CONFIG['mysqlB']['chaosblade_port']
    lvs_host = CONFIG['lvs']['ip']
    lvs_chaosblade_port = CONFIG['lvs']['chaosblade_port']
    aops_host = CONFIG['aops']['ip']
    aops_chaosblade_port = CONFIG['aops']['chaosblade_port']

    if fault_node == 'tpcc':
        random_network_fault_params_for_tpcc(tpcc_host, tpcc_chaosblade_port, fault_type)
    elif fault_node == 'mysqlA':
        random_network_fault_params_for_mysqlA(mysqlA_host, mysqlA_chaosblade_port, fault_type)
    elif fault_node == 'mysqlB':
        random_network_fault_params_for_mysqlB(mysqlB_host, mysqlB_chaosblade_port, fault_type)
    elif fault_node == 'lvs':
        random_network_fault_params_for_lvs(lvs_host, lvs_chaosblade_port, fault_type)
    elif fault_node == 'aops':
        random_network_fault_params_for_aops(aops_host, aops_chaosblade_port)


def main():
    """
    inject a specific fault on a specific node
    e.g.
    python3 fault_inject.py tpcc 3 single

    inject a specific fault on a specific node cyclically
    e.g.
    python3 fault_inject.py tpcc 3 cycle

    inject a random fault on a random node cyclically
    e.g.
    python3 fault_inject.py all all cycle
    """
    log_filename = CONFIG['fault_inject_log']
    logging.basicConfig(
            filename=log_filename,
            filemode='a',
            level=logging.INFO)
    if len(sys.argv) != 4:
        print('input error!')
        logging.error('input error!')
        return

    argv_list = sys.argv
    fault_node = argv_list[1]
    if argv_list[2].isdigit():
        fault_type = int(argv_list[2])
    mode = argv_list[3]
    if argv_list[1] == 'all' and argv_list[2] == 'all' and mode == 'cycle':
        schedule.every(10).to(15).minutes.do(random_fault)
        while True:
            schedule.run_pending()
    elif mode == 'cycle':
        schedule.every(10).to(15).minutes.do(single_fault, fault_node, fault_type)
        while True:
            schedule.run_pending()
    elif mode == 'single':
        single_fault(fault_node, fault_type)
    else:
        print('mode error')
        logging.error('mode error')

if __name__ == "__main__":
    main()