from gtt.byte_formatting import ints_to_signed_shorts, hex_colors_to_bytes
from gtt.enums import BarDirection
from gtt import GttDisplay

from display.element import Element


class RpmBar(Element):
    """A bar across the top of the screen that serves as a tachometer"""

    def __init__(self, display: GttDisplay):
        self.display : GttDisplay = display
        self.total_height = 40
        self.bar_height = self.total_height // 2
        self.color = 'FFFFFF'
        self.id = display._pick_new_id()

        self._redraw_bar()

        spaces = ' ' * 8
        self.display.create_label(
            label_id='rpm_label',
            x_pos=0, y_pos=self.bar_height, width=self.display.width, height=self.total_height - self.bar_height,
            font_size=4,
            value=f'{spaces}1{spaces}2{spaces}3{spaces}4{spaces}5{spaces}6{spaces}7'
        )

    def _redraw_bar(self):
        """Redraws the bar over top of the old bar in order to change the color"""
        min_value = 0
        max_value = 7600
        bg_color = '000000'
        x_pos = 0
        y_pos = 0

        self.display._conn.write(
            bytes.fromhex('FE 67') +
            self.id.to_bytes(1, 'big') +
            ints_to_signed_shorts(min_value, max_value, x_pos, y_pos, self.display.width, self.bar_height) +
            hex_colors_to_bytes(self.color, bg_color) +
            BarDirection.LEFT_TO_RIGHT.to_bytes(1, 'big')
        )

    def update(self, rpm: int):
        """Displays the given RPM on the RPM bar with an appropriate color"""
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

        if new_color != self.color:
            self.color = new_color
            self._redraw_bar()

        self.display.update_bar_value(self.id, rpm)
