#!/usr/bin/env python

from __future__ import print_function
from cisco import cli
import re

def check_scenario(value_and_code):

    print('CONCLUSION:')

    if value_and_code['raid_value_active'] == 'no failure'\
      and (value_and_code['raid_value_standby'] == 'mirror flash failed'
      or value_and_code['raid_value_standby'] == 'primary flash failed'):
        print(' Scenario C')
    elif (value_and_code['raid_value_active'] == 'primary flash failed'
      or value_and_code['raid_value_standby'] == 'mirror flash failed')\
      and value_and_code['raid_value_standby'] == 'no failure':
        print(' Scenario D')
    elif (value_and_code['raid_value_active'] == 'primary flash failed'
      or value_and_code['raid_value_active'] == 'mirror flash failed')\
      and (value_and_code['raid_value_standby'] == 'primary flash failed'
      or value_and_code['raid_value_standby'] == 'mirror flash failed'):
        print(' Scenario E')
    elif value_and_code['raid_value_active'] == 'both flash failed'\
      and value_and_code['raid_value_standby'] == 'no failure':
        print(' Scenario F')
    elif value_and_code['raid_value_active'] == 'no failure'\
      and value_and_code['raid_value_standby'] == 'both flash failed':
        print(' Scenario G')
    elif value_and_code['raid_value_active'] == 'both flash failed'\
      and (value_and_code['raid_value_standby'] == 'primary flash failed'
      or value_and_code['raid_value_standby'] == 'mirror flash failed'):
        print(' Scenario H')
    elif (value_and_code['raid_value_active'] == 'primary flash failed'
      or value_and_code['raid_value_active'] == 'mirror flash failed')\
      and value_and_code['raid_value_standby'] == 'both flash failed':
        print(' Scenario I')
    elif value_and_code['raid_value_active'] == 'both flash failed'\
      and value_and_code['raid_value_standby'] == 'both flash failed':
        print(' Scenario J')
    else:
        print(' No applicable scenario. Great!')

    url="https://www.cisco.com/c/en/us/support/docs/switches/nexus-7000-series-switches/200540-Nexus-7000-Supervisor-2-2E-Compact-Flash.html"
    print('Check the following for more information\n {}'.format(url))


def check_failure_code(raid_value_active, raid_value_standby):
    value_and_code = {}

    # debug only. put manual values and run in any n7k to test.
    #raid_value_active = '0xe1'
    #raid_value_standby = '0xd2'

    if raid_value_active == '0xf0':
        value_and_code['raid_value_active'] = 'no failure'
    elif raid_value_active == '0xe1':
        value_and_code['raid_value_active'] = 'primary flash failed'
    elif raid_value_active == '0xd2':
        value_and_code['raid_value_active'] = 'mirror flash failed'
    elif raid_value_active == '0xc3':
        value_and_code['raid_value_active'] = 'both flash failed'
    else:
        value_and_code['raid_value_active'] = 'no failure'

    if raid_value_standby == '0xf0':
        value_and_code['raid_value_standby'] = 'no failure'
    elif raid_value_standby == '0xe1':
        value_and_code['raid_value_standby'] = 'primary flash failed'
    elif raid_value_standby == '0xd2':
        value_and_code['raid_value_standby'] = 'mirror flash failed'
    elif raid_value_standby == '0xc3':
        value_and_code['raid_value_standby'] = 'both flash failed'
    else:
        value_and_code['raid_value_standby'] = 'no failure'

    print(value_and_code)
    check_scenario(value_and_code)


def check_raid(active_slot_number, standby_slot_number):

    raid_output_active = cli("slot {} show system internal raid | grep \"RAID data from CMOS\"".format(active_slot_number))
    for line in raid_output_active.splitlines():
        if re.search(r'RAID data from CMOS', line):
            raid_value_active = line.split(' ')[6]

    raid_output_standby = cli("slot {} show system internal raid | grep \"RAID data from CMOS\"".format(standby_slot_number))
    for line in raid_output_standby.splitlines():
        if re.search(r'RAID data from CMOS', line):
            raid_value_standby = line.split(' ')[6]

    print('RAID results:\n slot {} = {}\n slot {} = {}'\
          .format(active_slot_number, raid_value_active, standby_slot_number, raid_value_standby))

    check_failure_code(raid_value_active, raid_value_standby)


def check_diag(active_slot_number, standby_slot_number):

    diag_output_active = cli("show diagnostic result module {} | include \" CompactFlash\"".format(active_slot_number))
    diag_result_active = diag_output_active.split(' ')[3].rstrip()
    diag_output_standby = cli("show diagnostic result module {} | include \" CompactFlash\"".format(standby_slot_number))
    diag_result_standby = diag_output_standby.split(' ')[3].rstrip()

    print('Diag results:\n slot {} = {}\n slot {} = {}'\
          .format(active_slot_number, diag_result_active, standby_slot_number, diag_result_standby))

    check_raid(active_slot_number, standby_slot_number)


def check_slot_numbers():
    active_slot_number = cli("show module | in active")
    active_slot_number = active_slot_number.strip(' ')[0]
    standby_slot_number = cli("show module | in standby")
    standby_slot_number = standby_slot_number.strip(' ')[0]

    return (active_slot_number, standby_slot_number)


def main():

    active_slot_number, standby_slot_number = check_slot_numbers()
    check_diag(active_slot_number, standby_slot_number)


if __name__ == '__main__':
    main()
