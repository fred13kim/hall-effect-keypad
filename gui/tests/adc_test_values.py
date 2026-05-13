import hid
import time
import struct

VID = 0xCAFE
PID = 0x4004

device = hid.Device(VID, PID)
device.nonblocking = True

# Track min/max for each of the 4 channels
min_adc = [None] * 4
max_adc = [None] * 4


def get_latest_adc_reading(dev):
    """Drain the HID queue and return the latest 4-channel reading."""
    latest_values = None
    while True:
        data = dev.read(64)
        if not data:
            break
        # Expecting at least 8 bytes for 4 channels (uint16_t x 4)
        if len(data) >= 8:
            latest_values = struct.unpack_from("<4H", bytes(data), 0)
    return latest_values


try:
    while True:
        adc_values = get_latest_adc_reading(device)

        if adc_values:
            # Update min/max for each channel
            for i in range(4):
                val = adc_values[i]
                if min_adc[i] is None or val < min_adc[i]:
                    min_adc[i] = val
                if max_adc[i] is None or val > max_adc[i]:
                    max_adc[i] = val

            # Format output for all 4 channels
            channels_str = " | ".join(
                [f"CH{i}: {v:4d}" for i, v in enumerate(adc_values)]
            )
            print(f"\r{channels_str}", end="")

        time.sleep(0.005)

except KeyboardInterrupt:
    print("\n\nFinal Ranges:")
    for i in range(4):
        print(f"CH{i}: Min={min_adc[i]}, Max={max_adc[i]}")

finally:
    device.close()
