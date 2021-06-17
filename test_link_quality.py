import json

from drivers.exceptions import FailedChecksum
from drivers.ecm import Ecm


def get_checksum_failure_ratio(ecm: Ecm, num_samples=10):
    num_failures = 0
    for sample_num in range(num_samples):
        try:
            ecm.get_live_data_params()
        except FailedChecksum:
            num_failures += 1

    return num_failures / num_samples


def test_quality(ecm: Ecm):
    while True:
        failure_ratio = get_checksum_failure_ratio(ecm)
        print(f'{failure_ratio:.1%}')


if __name__ == '__main__':
    with open('drivers/live_data.json') as json_file:
        live_data_dict = json.load(json_file)

    ecm = Ecm('/dev/ttyUSB0', live_data_dict)
    ecm.open_conn()

    test_quality(ecm)

    ecm.close_conn()
