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
    waiting_period = 110
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


def create_nw_usage_metric(period: str):
    if period not in ['current', 'daily']:
        # We should only allow current/daily metrics
        return None
    data = ri.get_traffic_total()
    total_up = round(float(data['sent']), 2)
    total_down = round(float(data['recv']), 2)
    down_metric = ci.create_prom_data('asus_total_traffic', str(total_down),
                                      [('type', 'down'),('state', period)])
    up_metric = ci.create_prom_data('asus_total_traffic', str(total_up),
                                    [('type', 'up'),('state', period)])
    metric_list = [down_metric, up_metric]
    return metric_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--bandwidth",
                        help="If we should check bandwidth or not",
                        required=False, default=False, action="store_true")
    parser.add_argument("--router",
                        help="If we should check other metrics from router",
                        required=False, default=False, action="store_true")
    parser.add_argument("--daily",
                        help="This adds a new metric for presenting the total traffic during the past 24 hours",
                        required=False, default=False, action="store_true")
    parser.add_argument("--target",
                        help="The target directory for scrape folder, without ending slash, e.g. /opt/scrape_dir",
                        required=True)
    args = parser.parse_args()

    if args.bandwidth:
        print('Running router bandwidth check')
        # Since the network usage is calculated by comparing total data sent/received between two timestamps,
        # run this separately

        network_usage = get_bw()
        network_usage_metric = ci.create_prom_data('asus_network_utilization', network_usage['up'], [('type', 'up')])
        network_usage_metric2 = ci.create_prom_data('asus_network_utilization', network_usage['down'],
                                                    [('type', 'down')])
        metrics_list = [network_usage_metric, network_usage_metric2]
        ci.store_metrics(metrics_list, args.target + '/asus_nw.prom')

    elif args.router:
        print('Running normal router check')
        # Retrieving data
        latency_google, host = ci.latency_point()
        latency_isp, isp_host = ci.latency_point('www.ownit.se')
        number_clients = len(ri.get_clients_info())
        wan_status = ri.get_status_wan()

        # Building metrics
        latency_metric = ci.create_prom_data('asus_latency', latency_google, [('host', host)])
        latency_metric_isp = ci.create_prom_data('asus_latency', latency_isp, [('host', isp_host)])
        client_metric = ci.create_prom_data('asus_connected_clients', number_clients)
        metric_wan = ci.create_prom_data('asus_wan_status', wan_status['status'])
        current_total = create_nw_usage_metric('current')

        # Create a list of metrics to store
        metrics_list = [latency_metric, latency_metric_isp, client_metric, metric_wan] + current_total

        ci.store_metrics(metrics_list, args.target + '/asus_metrics.prom')

    elif args.daily:
        print('Create metric with total traffic on router')
        daily_total = create_nw_usage_metric('daily')
        # metrics_list = [daily_total]
        ci.store_metrics(daily_total, args.target + '/asus_daily.prom')

    else:
        print('We need something to check. Aborting. Use --help for pointers')
        exit(0)
