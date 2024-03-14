## OakMonitor

I live in a village in Sweden called Ekeby. Village is by in Swedish, and oak is ek in Swedish. 

Our WiFi is called FastOak (it used to be OakVillage but when upgrading to 5 GHz it was renamed)

The purpose of this project is to monitor network utilization, and possibly in the future also electricity
utilization

### AsusRouterMonitor

One day I got an idea that it would be interesting to see how much we actually use our Internet connection.

With more and more connected devices, movie streaming and gaming it could be nice to see how we utilize it.

Having an ASUS router, in the web UI there was possibility to see number of devices with their assigned IP.
But, their network analysis which sounded far more interesting required activation with some rather sneaky
license agreements.

Clearly, there must be some way to get this data any way, and a googling lead me to a 
[Medium article](https://itnext.io/monitor-your-asus-router-in-python-171693465fc1) talking
about how a guy found out by using network inspector that there existed CGI calls that could be used to get 
the required information. That repository is here; https://github.com/lmeulen/AsusRouterMonitor

So, I have to give a lot of credits to Leo van der Meulen for providing this important step.

### From a single point in time to a historical view

Running the script got me a lot of interesting data, but it is only for a specific point in time.

At work, I have previously setup monitoring of a website using Prometheus, Node exporter and Grafana. I wanted
to both refresh my knowledge, but also wanted to visually follow the data.

Metrics in Prometheus are named using lowercase letters and underscore as separator.

For easy distinguishing, labels can be added, making the number of metrics needed to be lower.

    my_awesome_metric{environment="dev",state="running"} 4

With node exporter, a directory can be scanned for files ending with .prom

Running the oak_monitor.py with arguments, different areas can be monitored and a prom file is generated in the 
specified folder

    python3 oak_monitor.py --router --target /run/node_exporter
    python3 oak_monitor.py --bandwidth --target /run/node_exporter

## Visualizing the data

Adding these commands to a cron job on a Raspberry Pi running Prometheus and Grafana

By connecting the Prometheus metrics to Grafana it was possible to visualize the data, and to see trends.

A nice feature of the Prometheus/Node exporter tool is the possibility to add custom metrics in an easy way.

## Tibber exporter

I started playing around with GraphQL queries that could be used to retrieve information about my
electricity consumption and price, as it could be a good addition to the dashboard.

However, I realized that I didn't have to reinvent the wheel completely, as I discovered a Python script that
starts a node exporter containing all the necessary information for me here; 
https://github.com/Pelleplutt/tibber-exporter

Actually, as of this writing the main branch class was outdated due to API changes on Tibber so it didn't work.
But an open PR lead me to a WIP development that solved the problem for me. 

This is the version I grabbed.
https://github.com/Pelleplutt/tibber-exporter/blob/new-api-202212/tibber-exporter.py
commit https://github.com/Pelleplutt/tibber-exporter/commit/09ac13d782658bbe5e4676b64bee9cfbeac95b0a

