import json
import curses
import time

from drivers.ecm import Ecm

PARAMETERS = {
    'engine_rpm': 'RPM',
    'throttle_position': 'Throttle',
    'vehicle_speed_mph': 'Speed',
    'battery_voltage': 'Battery Voltage',
    'engine_temperature': 'Engine Temp',
    'air_temperature': 'Air Temp'
}


def display_live_data(stdscr):
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    stdscr.clear()

    while True:
        param_dict = ecm.get_live_data_params(*PARAMETERS.keys())

        for idx, param_name, in enumerate(param_dict):
            display_name = PARAMETERS[param_name]
            format_str = '{:' + live_data_dict[param_name]['format_string'] + '}'
            units = live_data_dict[param_name]['units']

            param_value = param_dict[param_name]
            param_value = format_str.format(param_value)

            stdscr.addstr(idx, 0, f'{display_name}: {param_value} {units}', curses.color_pair(1))

        stdscr.refresh()
        time.sleep(0.03)


if __name__ == '__main__':
    with open('drivers/live_data.json') as json_file:
        live_data_dict = json.load(json_file)

    ecm = Ecm('/dev/ttyUSB0', live_data_dict)
    ecm.open_conn()

    curses.wrapper(display_live_data)

    ecm.close_conn()