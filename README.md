# Senior Project - Hall Effect Switch

## Preliminary Requirements & Setup
This project runs off of the Pico-SDK, raspberrypi fork of the FreeRTOS-Kernel,
and the raspberrypi fork of OpenOCD.



## CLI Usage

```bash
# to compile project
make

# to flash target directly (make sure device is in boot mode)
# to put device in boot mode:
# whilest the boot button is pressed, plug in USB cable
picotool load build/keypad-fw.elf
picotool reboot

# to flash target using debugger
make flash

# to open debug server
make debug

```

```bash
# to display serial output
picocom <device> -b 115200
```

