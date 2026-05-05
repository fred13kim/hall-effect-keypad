#!/usr/bin/env python3
import time
import struct
import math

import hid
from evdev import UInput, ecodes as e


VID = 0xCAFE
PID = 0x4004
NUM_CHANNELS = 4

# Channel mapping:
# 0 = W/up, 1 = A/left, 2 = S/down, 3 = D/right
CHANNEL_W = 0
CHANNEL_A = 1
CHANNEL_S = 2
CHANNEL_D = 3

# Adjust these after observing your real ADC values.
REST_ADC = 480
HARD_PRESS_ADC = 370

# If pressing makes ADC go up, use "increasing".
# If pressing makes ADC go down, use "decreasing".
PRESS_DIRECTION = "decreasing"

DEADZONE = 0.02          # ignore tiny noise near rest
MAX_SPEED = 25           # pixels per update at full press
MIN_SPEED = 3            # optional slow movement once active
CURVE_POWER = 1.6        # higher = finer low-speed control
UPDATE_DT = 0.01         # 10 ms loop


class HIDReader:
    def __init__(self, vid, pid):
        self.device = hid.Device(vid, pid)
        self.device.nonblocking = True

    def read_adc_all_channels(self):
        """Drain HID queue and return latest 4-channel ADC reading."""
        adc_values = None

        while True:
            data = self.device.read(64)
            if not data:
                break

            if len(data) >= 8:
                adc_values = struct.unpack_from("<4H", bytes(data), 0)

        return adc_values

    def close(self):
        self.device.close()


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def adc_to_press_level(adc):
    """
    Convert raw ADC value to normalized press level:
        0 = not pressed
        1 = hard press
    """

    if PRESS_DIRECTION == "increasing":
        denom = HARD_PRESS_ADC - REST_ADC
        if denom == 0:
            return 0.0
        level = (adc - REST_ADC) / denom

    elif PRESS_DIRECTION == "decreasing":
        denom = REST_ADC - HARD_PRESS_ADC
        if denom == 0:
            return 0.0
        level = (REST_ADC - adc) / denom

    else:
        raise ValueError("PRESS_DIRECTION must be 'increasing' or 'decreasing'")

    level = clamp(level)

    if level < DEADZONE:
        return 0.0

    # Rescale after deadzone so motion starts smoothly from 0.
    level = (level - DEADZONE) / (1.0 - DEADZONE)
    return clamp(level)


def level_to_speed(level):
    """
    Nonlinear speed curve.
    Small presses stay precise; hard presses move fast.
    """
    if level <= 0:
        return 0.0

    curved = level ** CURVE_POWER
    return MIN_SPEED + curved * (MAX_SPEED - MIN_SPEED)


def main():
    reader = HIDReader(VID, PID)

    capabilities = {
        e.EV_REL: [e.REL_X, e.REL_Y],
    }

    ui = UInput(capabilities, name="Hall Effect WASD Mouse")

    print("Hall-effect WASD mouse demo running.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            adc = reader.read_adc_all_channels()

            if adc is None:
                time.sleep(UPDATE_DT)
                continue

            levels = [adc_to_press_level(v) for v in adc]

            w = level_to_speed(levels[CHANNEL_W])
            a = level_to_speed(levels[CHANNEL_A])
            s = level_to_speed(levels[CHANNEL_S])
            d = level_to_speed(levels[CHANNEL_D])

            dx = d - a
            dy = s - w

            # Normalize diagonal movement so W+D is not artificially faster.
            mag = math.hypot(dx, dy)
            if mag > MAX_SPEED:
                scale = MAX_SPEED / mag
                dx *= scale
                dy *= scale

            dx = int(round(dx))
            dy = int(round(dy))

            if dx != 0 or dy != 0:
                ui.write(e.EV_REL, e.REL_X, dx)
                ui.write(e.EV_REL, e.REL_Y, dy)
                ui.syn()

            time.sleep(UPDATE_DT)

    except KeyboardInterrupt:
        print("\nStopping.")

    finally:
        reader.close()
        ui.close()


if __name__ == "__main__":
    main()