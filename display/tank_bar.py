from os import path

from gtt import GttDisplay

from display.element import Element

FILE_PATH = 'refill.odo'
AVERAGE_MPG = 45
TANK_GALLONS = 4


class TankBar(Element):
    """Estimates the amount of fuel in the tank based on the odometer reading and displays it as a bar.
    Can also display a low fuel warning.
    """

    def __init__(self, display: GttDisplay):
        super().__init__(display)

        self.id = display._pick_new_id()
        self.color = 'FFFFFF'
        self._redraw_bar()
        self.display.create_label(
            'fuel',
            x_pos=0, y_pos=80, width=40, height=20,
            font_size=10, font_id='sans',
            value='Tank'
        )

        with open(FILE_PATH) as odo_file:
            self.last_refill_odo = float(odo_file.read().strip())

    def _redraw_bar(self):
        self.display.overwrite_bar(
            self.id, max_value=TANK_GALLONS * 10,
            x_pos=6, y_pos=105, width=30, height=50,
            fg_color_hex=self.color, bg_color_hex='909090'
        )

    def update(self, odometer_reading: float, low_fuel_warning=False):
        """:param odometer_reading: the current odometer reading
        :param low_fuel_warning: if set to True, the fuel estimation will be skipped and the bar will be red and empty
        """
        tank_gallons = TANK_GALLONS - (odometer_reading - self.last_refill_odo) / AVERAGE_MPG

        if tank_gallons < 1.2 or low_fuel_warning:
            new_color = 'FF0000'
            tank_gallons = max(0.5, tank_gallons)
            tank_gallons = min(1.2, tank_gallons)

        elif tank_gallons < 2:
            new_color = 'FFFF00'
        else:
            new_color = '00FF00'

        if new_color != self.color:
            self.color = new_color
            self._redraw_bar()

        self.display.update_bar_value(self.id, round(tank_gallons * 10))

    def refill(self, odometer_reading: float):
        """Similar to resetting a trip meter, calling this indicates that the tank has been refilled."""
        self.last_refill_odo = odometer_reading

        with open(FILE_PATH, 'w') as odo_file:
            odo_file.truncate()
            odo_file.seek(0)
            odo_file.write(str(odometer_reading))

        self.update(odometer_reading)
