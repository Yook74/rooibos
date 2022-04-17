import time

from gtt import GttDisplay

from display import rpm_bar


class RooibosDisplay(GttDisplay):
    def __init__(self, port: str):
        super().__init__(port)
        self.clear_screen()

        self.rpm_bar = rpm_bar.RpmBar(self)


if __name__ == '__main__':
    d = RooibosDisplay('/dev/ttyUSB0')
    rpms = list(range(300, 1000, 50)) + list(range(1000, 7300, 300)) + list(range(7300, 2500, -750))

    for rpm in rpms:
        d.rpm_bar.update(rpm)
        time.sleep(0.05)