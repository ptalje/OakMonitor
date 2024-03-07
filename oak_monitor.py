import argparse
import json
import os
import requests
import re
from datetime import datetime
import time

import subprocess
from router_info import RouterInfo
from common import CommonFunctions

ri = RouterInfo("192.168.2.1", "admin", os.environ['ROUTER_PWD'])
ci = CommonFunctions


def get_bw():
    # Calculate the average speed during 3*2 second bursts with a delay between
    # {"speed": {"tx": 2.54, "rx": 5.68}, "total": {"sent": 3757.051513671875, "recv": 6012.16898727417}}
    total_up = 0
    total_down = 0
    for i in range(3):
        transfer_data = ri.get_traffic()
        json_obj = json.loads(transfer_data)
        up_rate = round(json_obj['speed']['tx'], 2)
        down_rate = round(json_obj['speed']['rx'], 2)
        total_up += up_rate
        total_down += down_rate
        if i != 2:
            time.sleep(20)
    avg_up = round(total_up/3, 2)
    avg_down = round(total_down/3, 2)
    return {"up": avg_up, "down": avg_down}


#cl = ci.create_prom_data('asus_number_clients', 15)
#print(cl)

#cl2 = ci.create_prom_data('bogus', 100, [('key', 'value'), ('key2', 'value2')])
#print(cl2)





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--bandwidth",
                        help="If we should check bandwidth or not", required=False, default=False, action='store_true')
    parser.add_argument("--router",
                        help="If we should check other metrics from router", required=False, default=False, action='store_true')

    args = parser.parse_args()

    if args.bandwidth:
        print('We should check bandwidth')
        date_format = '%Y%m%d_%H%M%S'
        current_time = time.strftime(date_format)
        tmp_file = 'tmp_' + current_time + '_nw.prom'
        network_usage = get_bw()
        network_usage_metric = ci.create_prom_data('asus_network_utilization', network_usage['up'], [('type', 'up')])
        network_usage_metric2 = ci.create_prom_data('asus_network_utilization', network_usage['down'],
                                                    [('type', 'down')])
        ci.append_to_file(network_usage_metric, tmp_file)
        ci.append_to_file(network_usage_metric2, tmp_file)
        ci.copy_file(tmp_file, 'asus_nw.prom')

    elif args.router:
        print('We should do normal')
        latency = ci.latency_point()
        print(latency)
        number_clients = len(ri.get_clients_info())
        print(number_clients)
    else:
        print('We need something to check. Aborting. Use --help for pointers')
        exit(0)
