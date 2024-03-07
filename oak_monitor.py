import argparse
import json
import os
import time

from router_info import RouterInfo
from common import CommonFunctions

ri = RouterInfo("192.168.2.1", "admin", os.environ.get('ROUTER_PWD'))
ci = CommonFunctions
metrics_directory = os.environ.get('SCRAPE_DIRECTORY')


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--bandwidth",
                        help="If we should check bandwidth or not",
                        required=False, default=False, action='store_true')
    parser.add_argument("--router",
                        help="If we should check other metrics from router",
                        required=False, default=False, action='store_true')
    args = parser.parse_args()
    date_format = '%Y%m%d_%H%M%S'
    current_time = time.strftime(date_format)

    if args.bandwidth:
        print('Running router bandwidth check')
        tmp_file = 'tmp_' + current_time + '_nw.prom'
        network_usage = get_bw()
        network_usage_metric = ci.create_prom_data('asus_network_utilization', network_usage['up'], [('type', 'up')])
        network_usage_metric2 = ci.create_prom_data('asus_network_utilization', network_usage['down'],
                                                    [('type', 'down')])
        ci.append_to_file(network_usage_metric, tmp_file)
        ci.append_to_file(network_usage_metric2, tmp_file)
        if metrics_directory:
            ci.copy_file(tmp_file, metrics_directory + 'asus_nw.prom')
        else:
            ci.copy_file(tmp_file, 'asus_nw.prom')
    elif args.router:
        print('Running normal router check')
        tmp_file = 'tmp_' + current_time + '_router.prom'
        latency = ci.latency_point()
        latency_metric = ci.create_prom_data('asus_latency', latency)
        number_clients = len(ri.get_clients_info())
        client_metric = ci.create_prom_data('asus_connected_clients', number_clients)
        ci.append_to_file(latency_metric, tmp_file)
        ci.append_to_file(client_metric, tmp_file)
        if metrics_directory:
            ci.copy_file(tmp_file, metrics_directory + 'asus_metrics.prom')
        else:
            ci.copy_file(tmp_file, 'asus_metrics.prom')
    else:
        print('We need something to check. Aborting. Use --help for pointers')
        exit(0)
