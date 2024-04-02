import os
import socket
import shutil
import time


class CommonFunctions:

    @staticmethod
    def latency_point(host: str = 'www.google.com', port: int = 443, timeout: float = 5):
        """
        :rtype: Returns float if possible
        Calculate a latency point using sockets. If something bad happens the point returned is None
        """

        # Start a timer
        s_start = time.monotonic()

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
        s_runtime = (time.monotonic() - s_start) * 1000

        return round(float(s_runtime), 2), host

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
    def copy_file(source_file, target_file):
        shutil.copy(source_file, target_file)

    @staticmethod
    def write_line_to_file(text_string, target_file):
        with open(target_file, 'w') as file:
            file.write(text_string)

    @staticmethod
    def read_file(source_file):
        with open(source_file, 'r') as file:
            data = file.read()
            return data

    @staticmethod
    def store_metrics(metric_list: list, file_name):
        date_format = '%Y%m%d_%H%M%S'
        current_time = time.strftime(date_format)
        tmp_file = 'tmp_' + current_time + '.tmp'
        with open(tmp_file, 'a') as file:
            for line in metric_list:
                file.write(line + '\n')
        shutil.copy(tmp_file, file_name)
        os.remove(tmp_file)
