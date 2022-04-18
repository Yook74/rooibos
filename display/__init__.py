import time

from gtt import GttDisplay
from gtt.byte_formatting import ints_to_signed_shorts, hex_colors_to_bytes
from gtt.enums import BarDirection

from display import rpm_bar, clock, tank_bar, speedometer


class RooibosDisplay(GttDisplay):
    def __init__(self, port: str):
        super().__init__(port)
        self.clear_screen()
        self.load_font('sans', 'rooibos_assets/Oswald-VariableFont_wght.ttf')

        self.rpm_bar = rpm_bar.RpmBar(self)
        self.clock = clock.Clock(self)
        self.tank_bar = tank_bar.TankBar(self)
        self.speedometer = speedometer.Speedometer(self)

    def overwrite_bar(self, bar_id: int, max_value: int,
                         x_pos: int, y_pos: int, width: int, height: int,
                         min_value: int = 0, fg_color_hex='FFFFFF', bg_color_hex='000000',
                         direction: BarDirection = BarDirection.BOTTOM_TO_TOP):
        """Acts like create_plain_bar but all the ID reuse protection is turned off"""
        self._conn.write(
            bytes.fromhex('FE 67') +
            bar_id.to_bytes(1, 'big') +
            ints_to_signed_shorts(min_value, max_value, x_pos, y_pos, width, height) +
            hex_colors_to_bytes(fg_color_hex, bg_color_hex) +
            direction.to_bytes(1, 'big')
        )


if __name__ == '__main__':
    d = RooibosDisplay('/dev/ttyUSB0')
    rpms = list(range(300, 1000, 50)) + list(range(1000, 7300, 300)) + list(range(7300, 2500, -750))

    for speed in [8, 60, 120]:
        d.speedometer.update(speed)
        time.sleep(0.5)

    for rpm in rpms:
        d.rpm_bar.update(rpm)
        time.sleep(0.05)

    for odo in range(0, 200, 3):
        d.tank_bar.update(odo)
        time.sleep(0.05)

