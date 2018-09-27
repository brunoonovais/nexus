#!/usr/bin/env python

# Imports
from __future__ import print_function
from cli import cli, clid
from time import sleep
from datetime import datetime
import json
import os
import argparse

# Global Variables
date_and_time_start = datetime.now().strftime("%y%m%d_%H_%M_%S")
cmd_list = ['show proc cpu sort',
            'show proc cpu history',
            'show system resources',
            'show system internal mts buffers summary',
            'show system internal mts buffer detail',
            'show hardware internal cpu-mac inband stats',
            'show hardware internal cpu-mac inband counters',
            'show policy-map interface control-plane',
            'show hardware internal buffer info pkt-stats cpu',
            'show system internal pktmgr stat',
            'ethanalyzer local interface inband limit-captured-frames 30 write bootflash:n3k_highcpu_capture.pcap']
logfile = '/bootflash/n3k_highcpu_logs_{}.txt'.format(date_and_time_start)

def rename_pcap(date_and_time_cmd):
    os.system('mv /bootflash/n3k_highcpu_capture.pcap /bootflash/n3k_highcpu_capture_{}.pcap'.format(date_and_time_cmd))

def collect_cmds(cmd_list, f):
    for cmd in cmd_list:
        print('--- collecting', cmd)
        output = cli(cmd)
        date_and_time_cmd = datetime.now().strftime("%y%m%d_%H_%M_%S")
        f.write('|---- ' + cmd + ' - ' + date_and_time_cmd + ' ----|\n\n' + output + '\n\n')
        f.flush() # flusing so even if something bad happens while running it, we get the logs written to the file.

    # then call rename_pcap to rename filename to allow for multiple executions and captures not to be lost.
    rename_pcap(date_and_time_cmd)

def check_cpu():
    
    # below example using cli method
    # o = cli('show proc cpu | in "CPU util"').split(',')[2].strip().split(' ')[0].strip('%')
    # below example much better using clid method
    
    o = json.loads(clid('show proc cpu'))['idle_percent'].encode('UTF-8')
    return float(o)

def main():

    #### Argparse block ####
    parser = argparse.ArgumentParser()
    parser.add_argument("--sleep", '-s', type=float, default=10, help="How many seconds to wait before next CPU check")
    parser.add_argument("--idlethreshold", '-t', type=float, default=10, help="Idle threshold")
    arguments = parser.parse_args()
    #### End of Argparse block ####

    # Assigning variables
    sleep_time = arguments.sleep
    idle_threshold = arguments.idlethreshold

    with open(logfile, 'w') as f:
        print('-------- Starting --------\n')
        while True:
            idle_cpu_usage = check_cpu()
            print('- IDLE cpu usage: ', idle_cpu_usage)
            if idle_cpu_usage < idle_threshold:
                syslog_msg = 'CPU Usage is high! IDLE only at', str(idle_cpu_usage), 'collecting data'
                #syslog.syslog(2, syslog_msg)
                os.system('echo -e "[a123b234,1,3]{}" > /dev/ttyS2'.format(syslog_msg))
                print('-- collecting commands...')
                collect_cmds(cmd_list, f)

            sleep(sleep_time)

if __name__ == '__main__':
    main()
