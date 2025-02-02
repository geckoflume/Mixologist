import spidev


class WS2812:
    # color = [g, r, b]
    ready = [50, 25, 255]
    error = [10, 255, 0]
    warning = [220, 255, 25]
    success = [255, 10, 100]
    white = [255, 255, 255]
    black = [0, 0, 0]

    def __init__(self, bus, dev, led_count):
        self.spi = spidev.SpiDev()
        self.bus = bus
        self.dev = dev
        self.leds_count = led_count
        self.current_color = WS2812.white
        self.spi.open(self.bus, self.dev)

    def reset(self):
        self.enable_all(WS2812.black)

    def parse_color(self, color):
        if isinstance(color, str):
            if color == 'ready':
                color = self.ready
            elif color == 'error':
                color = self.error
            elif color == 'warning':
                color = self.warning
            elif color == 'success':
                color = self.success
        if color != WS2812.black:
            self.current_color = color
        return color

    def enable_all(self, color=None):
        if color is None:
            color = self.current_color
        else:
            color = self.parse_color(color)
        self.write2812([color] * self.leds_count)

    def enable_one(self, led, color=None):
        if color is None:
            color = self.current_color
        else:
            color = self.parse_color(color)
        d = [WS2812.black] * self.leds_count
        d[led % self.leds_count] = color
        self.write2812(d)

    def enable_pos(self, pos, color=None):
        if pos == '1':
            self.enable_one(1, color)
        elif pos == '2':
            self.enable_one(4, color)
        elif pos == '3':
            self.enable_one(13, color)
        elif pos == '4':
            self.enable_one(15, color)
        elif pos == '5':
            self.enable_one(8, color)

    def enable_percentage(self, n, color=None):
        if color is None:
            color = self.current_color
        else:
            color = self.parse_color(color)
        n_leds = int((n * self.leds_count / 100))
        d = [color] * n_leds + [WS2812.black] * (self.leds_count - n_leds)
        self.write2812(d)

    def write2812(self, data):
        tx = [0x00]
        for rgb in data:
            for byte in rgb:
                for ibit in range(3, -1, -1):
                    tx.append(((byte >> (2 * ibit + 1)) & 1) * 0x60 + ((byte >> (2 * ibit + 0)) & 1) * 0x06 + 0x88)
        self.spi.xfer(tx, int(4 / 1.05e-6))
