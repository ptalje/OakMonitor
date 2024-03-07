import os
from router_info import RouterInfo

if __name__ == "__main__":
    ri = RouterInfo("192.168.2.1", "admin", os.environ['ROUTER_PWD'])
    print("Uptime    : " + str(ri.get_uptime()))
    print("Uptime    : " + str(ri.get_uptime_secs()))
    print("Memory    : " + str(ri.get_memory_usage()))
    print("CPU       : " + str(ri.get_cpu_usage()))
    print("Data      : " + str(ri.get_traffic_total()))
    print("Bandwidth : " + str(ri.get_traffic()))
    print("WAN       : " + str(ri.get_status_wan()))
    print("Online    : " + str(ri.is_wan_online()))
    print("Settings  : " + str(ri.get_settings()))
    print("IP addr   : " + str(ri.get_lan_ip_address()))
    print("Netmask   : " + str(ri.get_lan_netmask()))
    print("Gateway   : " + str(ri.get_lan_gateway()))
    print("Clients   : " + str(ri.get_clients_fullinfo()))
    print("Clients   : " + str(ri.get_clients_info()))
    print("Client   : " + str(ri.get_client_info('B8:2C:A0:5F:37:52')))
    print("DHCP      : " + str(ri.get_dhcp_list()))
    print("Online    : " + str(ri.get_online_clients()))
