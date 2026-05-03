add_library(usb_descriptors STATIC hid_usb_descriptors.c)
target_include_directories(usb_descriptors PRIVATE ${INCLUDE})
target_link_libraries(usb_descriptors
    pico_stdlib
    tinyusb_device
    tinyusb_board
    FreeRTOS-Kernel
)
