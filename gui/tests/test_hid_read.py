import hid

VID = 0xCAFE
PID = 0x4004

dev = hid.Device(VID, PID)

while True:
    report = dev.read(8)
    if report:
        adc1 = report[0] | (report[1] << 8)
        adc2 = report[2] | (report[3] << 8)
        adc3 = report[4] | (report[5] << 8)
        adc4 = report[6] | (report[7] << 8)

        print(adc1, adc2, adc3, adc4)