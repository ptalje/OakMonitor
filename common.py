import os
import socket
import shutil
from time import sleep, monotonic


class CommonFunctions:

    @staticmethod
    def latency_point(host: str = 'www.google.com', port: int = 443, timeout: float = 5):
        '''
        :rtype: Returns float if possible
        Calculate a latency point using sockets. If something bad happens the point returned is None
        '''

        # Start a timer
        s_start = monotonic()

        # Try to Connect
        try:
            s = socket.create_connection((host, port), timeout=timeout)
            s.shutdown(socket.SHUT_RD)

        # If something bad happens, the latency_point is None
        except socket.timeout:
            pass
            return None
        except OSError:
            pass
            return None

        # Stop Timer
        s_runtime = (monotonic() - s_start) * 1000

        return round(float(s_runtime), 2)

    @staticmethod
    def create_prom_data(metric_identifier, metric_value, labels: list = None):
        """
        :param metric_identifier:
        :param metric_value:
        :param labels:
        :return:
        with labels: my_custom_metric{type="inside"} 1
        without labels: my_custom_metric 4
        """

        if not labels:
            output_string = str(metric_identifier) + ' ' + str(metric_value)
        else:
            metric_strings = []
            for idx, values in enumerate(labels):
                metric_label = values[0] + '=\"' + values[1] + '\"'
                metric_strings.append(metric_label)
            content = (','.join(metric_strings))
            metric_labels = '{' + content + '}'
            output_string = str(metric_identifier) + metric_labels + ' ' + str(metric_value)
        return output_string

    @staticmethod
    def append_to_file(prom_data, file_name):
        with open(file_name, 'a') as file:
            l1 = prom_data + "\n"
            file.writelines(l1)

    @staticmethod
    def write_to_file(prom_data, file_name):
        with open(file_name, 'w') as file:
            file.writelines(prom_data)

    @staticmethod
    def copy_file(source_file, target_file):
        shutil.copy(source_file, target_file)