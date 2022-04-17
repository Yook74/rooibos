from datetime import datetime

from gtt import GttDisplay

from display.element import Element


class Clock(Element):
    """A digital clock"""

    def __init__(self, display: GttDisplay):
        self.display: GttDisplay = display

        self.display.create_label(
            'clock', x_pos=0, y_pos=45, width=80, height=35, font_size=14, font_id='sans',
        )
        self.update(datetime.now())

    def update(self, time: datetime):
        """Sets the displayed time to the given value
        :param time: usually datetime.datetime.now()
        """
        self.display.update_label(
            'clock',
            time.strftime('%H:%M')
        )
