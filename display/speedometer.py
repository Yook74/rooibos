from gtt import GttDisplay
from gtt.enums import FontAlignHorizontal

from display.element import Element


class Speedometer(Element):
    """A digital speedometer"""

    def __init__(self, display: GttDisplay):
        super().__init__(display)

        self.display.create_label(
            'speedo', value='0',
            x_pos=200, y_pos=55, width=180, height=120,
            font_size=60, font_id='sans', horizontal_just=FontAlignHorizontal.RIGHT
        )

    def update(self, speed: float):
        self.display.update_label('speedo', f'{speed:.0f}')
