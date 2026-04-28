add_library(usb_descriptors STATIC hid_usb_descriptors.c)
target_link_libraries(usb_descriptors
    pico_stdlib
    tinyusb_device
    tinyusb_board
)
