import argparse
import json
import os
import time

from router_info import RouterInfo
from common import CommonFunctions

ri = RouterInfo("192.168.2.1", "admin", os.environ.get('ROUTER_PWD'))
ci = CommonFunctions


def get_bw():
    # Calculate the average transfer speed by getting transfer data between two events
    # {'sent': '12033.441837310791', 'recv': '1560.4690246582031'}
    waiting_period = 40
    traffic_before = ri.get_traffic_total()
    time.sleep(waiting_period)
    traffic_after = ri.get_traffic_total()
    sent_data = float(traffic_after['sent']) - float(traffic_before['sent'])
    recv_data = float(traffic_after['recv']) - float(traffic_before['recv'])
    # print('Received data during period (Mb): {}'.format(recv_data))
    # print('Sent data during period (Mb): {}'.format(sent_data))
    avg_send_speed = round(float(sent_data / waiting_period), 2)
    avg_recv_speed = round(float(recv_data / waiting_period), 2)
    # print('Average send speed (Mb/s): {}'.format(avg_send_speed))
    # print('Average recv speed (Mb/s): {}'.format(avg_recv_speed))
    return {"up": avg_send_speed, "down": avg_recv_speed}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--bandwidth",
                        help="If we should check bandwidth or not",
                        required=False, default=False, action='store_true')
    parser.add_argument("--router",
                        help="If we should check other metrics from router",
                        required=False, default=False, action='store_true')
    parser.add_argument("--target",
                        help="The target directory for scrape folder, without ending slash, e.g. /opt/scrape_dir",
                        required=True)
    args = parser.parse_args()

    if args.bandwidth:
        print('Running router bandwidth check')
        network_usage = get_bw()
        network_usage_metric = ci.create_prom_data('asus_network_utilization', network_usage['up'], [('type', 'up')])
        network_usage_metric2 = ci.create_prom_data('asus_network_utilization', network_usage['down'],
                                                    [('type', 'down')])
        metrics_list = [network_usage_metric, network_usage_metric2]
        ci.store_metrics(metrics_list, args.target + '/asus_nw.prom')

    elif args.router:
        print('Running normal router check')
        latency = ci.latency_point()
        latency_metric = ci.create_prom_data('asus_latency', latency)
        number_clients = len(ri.get_clients_info())
        client_metric = ci.create_prom_data('asus_connected_clients', number_clients)
        metrics_list = [latency_metric, client_metric]
        ci.store_metrics(metrics_list, args.target + '/asus_metrics.prom')

    else:
        print('We need something to check. Aborting. Use --help for pointers')
        exit(0)
