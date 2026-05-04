import hid
import time

VID = 0xCAFE
PID = 0x4004

device = hid.Device(VID, PID)
device.nonblocking = True

min_adc = None
max_adc = None

print("Move the key through its full travel. Press Ctrl+C when done.")

try:
    while True:
        data = device.read(64)

        if data and len(data) >= 2:
            adc = data[0] | (data[1] << 8)

            if min_adc is None or adc < min_adc:
                min_adc = adc

            if max_adc is None or adc > max_adc:
                max_adc = adc

            print(f"adc={adc:4d}   min={min_adc:4d}   max={max_adc:4d}")

        time.sleep(0.005)

except KeyboardInterrupt:
    print("\nFinal range:")
    print(f"min_adc = {min_adc}")
    print(f"max_adc = {max_adc}")

finally:
    device.close()