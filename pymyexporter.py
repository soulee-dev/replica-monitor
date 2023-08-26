import requests
from typing import Dict, Union
from typing import List


class PyMyExporter:
    def __init__(self, host: str, port: int):
        self._exporter_url = f"http://{host}:{port}/metrics"

    def _get_metrics_text(self) -> str:
        response = requests.get(self._exporter_url)
        return response.text

    def _parse_metric_line(self, line: str) -> Dict[str, Union[str, Dict[str, str], float]]:
        if '{' not in line:
            metric_name, value = line.split(' ', 1)
            labels = {}
        else:
            # Splitting the line to get the metric name, labels, and value
            metric_name, rest = line.split('{', 1)
            labels_part, value = rest.split('}', 1)

            # Parsing the labels
            labels = {}
            for label in labels_part.split(','):
                key, value_str = label.split('=', 1)
                # Removing quotes from the label value
                value_str = value_str.strip('"')
                labels[key] = value_str

        value = float(value.strip())

        return {
            "metric_name": metric_name,
            "labels": labels,
            "value": value
        }

    def get_metrics(self) -> List[Dict[str, Union[str, Dict[str, str], float]]]:
        metrics_text = self._get_metrics_text()
        parsed_data = [self._parse_metric_line(line) for line in metrics_text.splitlines() if line and not line.startswith("#")]
        return parsed_data
