import time

from gtt import GttDisplay
from gtt.enums import *


class RooibosDisplay(GttDisplay):
    def __init__(self, port: str):
        super().__init__(port)

        self._high_rpm = False

        self._init_rpm_bar()

    def _init_rpm_bar(self, fg_color='0000FF'):
        total_height = 36
        bar_height = round(total_height * .6666)
        label_height = total_height - bar_height

        self.create_plain_bar(
            bar_id='rpm_bar', value=0, max_value=7600,
            x_pos=0, y_pos=0, width=self.width, height=bar_height,
            fg_color_hex=fg_color,
            direction=BarDirection.LEFT_TO_RIGHT
        )

        spaces = ' ' * 5
        self.create_label(
            label_id='rpm_label',
            x_pos=0, y_pos=bar_height, width=self.width, height=label_height,
            font_size=label_height - 2,
            value=f'{spaces}1{spaces}2{spaces}3{spaces}4{spaces}5{spaces}6{spaces}7'
        )

    def update_rpm(self, rpm: int):
        def redraw_bars(rpm_bar_color: str):
            self._conn.write(bytes.fromhex('FE 6B'))  # clear all bargraphs
            self._init_fuel_bar()
            self._init_rpm_bar(rpm_bar_color)

        if rpm >= 7000:
            if not self._high_rpm:
                redraw_bars(rpm_bar_color='FF0000')

            self._high_rpm = True
        else:
            if self._high_rpm:
                redraw_bars(rpm_bar_color='0000FF')

            self._high_rpm = False

        self.update_bar_value('rpm_bar', rpm)


if __name__ == '__main__':
    d = RooibosDisplay('COM20')
    rpms = list(range(1500, 7300, 300)) + list(range(7300, 3000, -750))

    for rpm in rpms:
        d.update_rpm(rpm)
        time.sleep(0.05)
