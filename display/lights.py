import time

from gtt import GttDisplay

from display.element import Element


class TurnIndicator(Element):
    """A left or right blinking arrow"""

    def __init__(self, display: GttDisplay):
        super().__init__(display)

        self.x_pos = 330
        self.y_pos = 80
        self.width = 65
        self.height = 41
        self.blink_duration = 0.5  # length in seconds of half of a blink cycle
        self.blink_schedule = None  # a time in the future when we should display or hide the arrow
        self.blink_blanked = False  # if the arrow is blinking, is it in the blank part of the blink or the visible part
        self.last_state = None

        display.load_bitmap('left_turn', 'rooibos_assets/left_turn.bmp')
        display.load_bitmap('right_turn', 'rooibos_assets/right_turn.bmp')
        display.set_bitmap_transparency('left_turn', 'FFFFFF')
        display.set_bitmap_transparency('right_turn', 'FFFFFF')

    def hide_bitmap(self):
        self.display.set_drawing_color('000000')
        self.display.draw_rectangle(self.x_pos, self.y_pos, self.width, self.height, fill=True)

    def show_bitmap(self, left_right: str):
        self.display.display_bitmap(f'{left_right}_turn', self.x_pos, self.y_pos)

    def update(self, right_turn=False, left_turn=False):
        """Can be used to display the left or right turn signals which will blink.
        Even if you're not changing the state of the arrows, you should call this method
        because otherwise the blinking will not work.
        """
        if right_turn:
            new_state = 'right'
        elif left_turn:
            new_state = 'left'
        else:
            new_state = None

        time_to_blink = self.blink_schedule is not None and self.blink_schedule < time.time()

        if new_state == self.last_state and new_state is not None and time_to_blink:
            if self.blink_blanked:
                self.show_bitmap(new_state)
            else:
                self.hide_bitmap()

            self.blink_blanked = not self.blink_blanked
            self.blink_schedule = time.time() + self.blink_duration

        elif new_state is None:
            self.hide_bitmap()
            self.blink_schedule = None
            self.blink_blanked = False

        elif new_state != self.last_state:
            self.show_bitmap(new_state)
            self.blink_blanked = False
            self.blink_schedule = time.time() + self.blink_duration

        self.last_state = new_state


class HighBeam(Element):
    """A high beam indicator light"""

    def __init__(self, display: GttDisplay):
        super().__init__(display)

        display.load_bitmap('high_beam', 'rooibos_assets/high_beam.bmp')
        display.set_bitmap_transparency('high_beam', 'FFFFFF')

        self.x_pos = 400
        self.y_pos = 80
        self.width = 70
        self.height = 45

    def update(self, show: bool):
        if show:
            self.display.display_bitmap(f'high_beam', self.x_pos, self.y_pos)
        else:
            self.display.set_drawing_color('000000')
            self.display.draw_rectangle(self.x_pos, self.y_pos, self.width, self.height, fill=True)


class NeutralLight(Element):
    """A green N"""

    def __init__(self, display: GttDisplay):
        super().__init__(display)

        self.display.create_label(
            'neutral',
            x_pos=335, y_pos=120, width=65, height=70,
            font_size=32, font_id='sans', fg_color_hex='00FF00',
            value=''
        )

    def update(self, show: bool):
        if show:
            self.display.update_label('neutral', 'N')
        else:
            self.display.update_label('neutral', '')
