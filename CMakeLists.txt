cmake_minimum_required(VERSION 3.22)

if (NOT DEFINED ENV{PICO_SDK_PATH})
    message(FATAL_ERROR "PICO_SDK_PATH DOES NOT EXIST")
endif()

message(STATUS "PICO_SDK_PATH EXISTS AT " $ENV{PICO_SDK_PATH})
set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})

set(PICO_BOARD pico2)
set(TARGET_NAME keypad-fw)

set(FREERTOS_KERNEL_PATH ${CMAKE_CURRENT_SOURCE_DIR}/lib/FreeRTOS-Kernel)

set(SRC ${CMAKE_CURRENT_SOURCE_DIR}/src)
set(INCLUDE ${CMAKE_CURRENT_SOURCE_DIR}/include)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(${PICO_SDK_PATH}/pico_sdk_init.cmake)

project(hall_effect_keypad C CXX ASM)

pico_sdk_init()

add_subdirectory(${FREERTOS_KERNEL_PATH}/portable/ThirdParty/GCC/RP2350_ARM_NTZ
    FreeRtos-Kernel)

add_subdirectory(lib/mcp3008_spi)
add_subdirectory(lib/usb_descriptors)
add_subdirectory(lib/ssd1306_i2c)

add_executable(${TARGET_NAME}
    ${SRC}/disp.c
    )

target_link_libraries(${TARGET_NAME}
    pico_stdlib
    hardware_gpio
    hardware_spi
    ssd1306_i2c
    FreeRTOS-Kernel-Heap4
    tinyusb_device
    tinyusb_board
    mcp3008_spi
    usb_descriptors
)

target_include_directories(${TARGET_NAME} PRIVATE ${INCLUDE})

pico_enable_stdio_uart(${TARGET_NAME} 1)
pico_add_extra_outputs(${TARGET_NAME})


configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/.gdbinit.in
    ${CMAKE_CURRENT_BINARY_DIR}/.gdbinit
    @ONLY
)
