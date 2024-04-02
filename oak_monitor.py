import argparse
import os
import time

from router_info import RouterInfo
from common import CommonFunctions

ri = RouterInfo("192.168.2.1", "admin", os.environ.get('ROUTER_PWD'))
ci = CommonFunctions
daily_rx_counter = "daily_counter_rx.tmp"
daily_tx_counter = "daily_counter_tx.tmp"


def get_bw():
    # Calculate the average transfer speed by getting transfer data between two events
    # {'sent': '12033.441837310791', 'recv': '1560.4690246582031'}
    waiting_period = 110
    traffic_before = ri.get_traffic_total()
    time.sleep(waiting_period)
    traffic_after = ri.get_traffic_total()
    sent_data = float(traffic_after['sent']) - float(traffic_before['sent'])
    recv_data = float(traffic_after['recv']) - float(traffic_before['recv'])

    rx_data = max(0.0, recv_data)
    tx_data = max(0.0, sent_data)
    update_current_nw_usage(tx_data, rx_data)

    # Calculate avg send/recv speed. In case recv/sent values are reset during period, do not return negative speed
    avg_send_speed = round(float(sent_data / waiting_period), 2)
    avg_recv_speed = round(float(recv_data / waiting_period), 2)

    return {"up": max(0.0, avg_send_speed), "down": max(0.0, avg_recv_speed)}


def update_current_nw_usage(up_value, down_value):
    current_up = ci.read_file(args.target + '/' + daily_tx_counter)
    current_down = ci.read_file(args.target + '/' + daily_rx_counter)
    new_up = round(float(current_up) + float(up_value), 2)
    new_down = round(float(current_down) + float(down_value), 2)
    ci.write_line_to_file(str(new_up), args.target + '/' + daily_tx_counter)
    ci.write_line_to_file(str(new_down), args.target + '/' + daily_rx_counter)


def usage_metrics_builder():
    current_up = ci.read_file(args.target + '/' + daily_tx_counter)
    current_down = ci.read_file(args.target + '/' + daily_rx_counter)
    daily_up_metric = ci.create_prom_data('asus_daily_usage', current_up, [('type', 'up')])
    daily_down_metric = ci.create_prom_data('asus_daily_usage', current_down,[('type', 'down')])
    metrics_builder = [daily_up_metric, daily_down_metric]
    return metrics_builder


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--bandwidth",
                        help="If we should check bandwidth or not",
                        required=False, default=False, action="store_true")
    parser.add_argument("--router",
                        help="If we should check other metrics from router",
                        required=False, default=False, action="store_true")
    parser.add_argument("--reset",
                        help="This restores the daily network usage counter",
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
        usage_metrics = usage_metrics_builder()
        metrics_list = [network_usage_metric, network_usage_metric2] + usage_metrics
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

        # Create a list of metrics to store
        metrics_list = [latency_metric, latency_metric_isp, client_metric, metric_wan]

        ci.store_metrics(metrics_list, args.target + '/asus_metrics.prom')

    elif args.reset:
        print('Resetting daily counter')
        ci.write_line_to_file('0.0', args.target + '/' + daily_rx_counter)
        ci.write_line_to_file('0.0', args.target + '/' + daily_tx_counter)

    else:
        print('We need something to check. Aborting. Use --help for pointers')
        exit(0)
