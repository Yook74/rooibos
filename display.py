import time

from gtt import GttDisplay
from gtt.enums import *
from gtt.exceptions import IdConflictError


class RooibosDisplay(GttDisplay):
    def __init__(self, port: str):
        super().__init__(port)
        self.clear_screen()

        self._rpm_color = '00FF00'

        self._init_rpm_bar()

    def _init_rpm_bar(self, fg_color='0000FF'):
        total_height = 40
        bar_height = round(total_height * .5)
        label_height = total_height - bar_height

        self.create_plain_bar(
            bar_id='rpm_bar', value=0, max_value=7600,
            x_pos=0, y_pos=0, width=self.width, height=bar_height,
            fg_color_hex=fg_color,
            direction=BarDirection.LEFT_TO_RIGHT
        )

        spaces = ' ' * 8
        try:
            self.create_label(
                label_id='rpm_label',
                x_pos=0, y_pos=bar_height, width=self.width, height=label_height,
                font_size=4,
                value=f'{spaces}1{spaces}2{spaces}3{spaces}4{spaces}5{spaces}6{spaces}7'
            )
        except IdConflictError:
            pass

    def update_rpm(self, rpm: int):
        def redraw_bars(rpm_bar_color: str):
            self._conn.write(bytes.fromhex('FE 6B'))  # clear all bargraphs
            self.ids_in_use.remove(self._id_map['rpm_bar'])
            del self._id_map['rpm_bar']
            # self._init_fuel_bar()
            self._init_rpm_bar(rpm_bar_color)

        new_color = 'FF0000'
        color_breakpoints = {
            800: '0000FF',
            1700: '00FF00',
            6000: 'FFFF00',
            7100: 'FF0000',
        }

        for breakp, color in color_breakpoints.items():
            if rpm > breakp:
                new_color = color

        if new_color != self._rpm_color:
            redraw_bars(new_color)
            self._rpm_color = new_color

        self.update_bar_value('rpm_bar', rpm)


if __name__ == '__main__':
    d = RooibosDisplay('/dev/ttyUSB0')
    rpms = list(range(300, 1000, 50)) + list(range(1000, 7300, 300)) + list(range(7300, 2500, -750))

    for rpm in rpms:
        d.update_rpm(rpm)
        time.sleep(0.05)
