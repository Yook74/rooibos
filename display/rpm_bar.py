from gtt.byte_formatting import ints_to_signed_shorts, hex_colors_to_bytes
from gtt.enums import BarDirection
from gtt import GttDisplay

from display.element import Element

MAX_RPM = 7600


class RpmBar(Element):
    """A bar across the top of the screen that serves as a tachometer"""

    def __init__(self, display: GttDisplay):
        self.display : GttDisplay = display
        self.total_height = 40
        self.bar_height = self.total_height // 2
        self.color = 'FFFFFF'
        self.id = display._pick_new_id()

        self._redraw_bar()

        label_width = 15
        for label_int in range(1, 8):
            x_pos = round((self.display.width / MAX_RPM) * label_int * 1000) - label_width // 2
            self.display.create_label(
                label_id=f'rpm_label_{label_int}',
                x_pos=x_pos, y_pos=self.bar_height, width=label_width, height=self.total_height - self.bar_height,
                font_size=10, font_id='sans',
                value=str(label_int)
            )

    def _redraw_bar(self):
        """Redraws the bar over top of the old bar in order to change the color"""
        bg_color = '000000'
        x_pos = 0
        y_pos = 0

        self.display._conn.write(
            bytes.fromhex('FE 67') +
            self.id.to_bytes(1, 'big') +
            ints_to_signed_shorts(0, MAX_RPM, x_pos, y_pos, self.display.width, self.bar_height) +
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
