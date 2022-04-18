from gtt import GttDisplay

from display.element import Element


class GearIndicator(Element):
    """A digital speedometer"""

    def __init__(self, display: GttDisplay):
        super().__init__(display)

        self.display.create_label(
            'gear_label', value='Gear',
            x_pos=120, y_pos=60, width=40, height=30,
            font_size=10, font_id='sans'
        )

        self.display.create_label(
            'gear', value='0',
            x_pos=106, y_pos=80, width=60, height=80,
            font_size=40, font_id='sans'
        )

    def update(self, speed: float, rpm: float):
        gear = 5  # TODO actually calculate

        self.display.update_label('gear', str(gear))

