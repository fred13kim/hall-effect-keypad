cmake_minimum_required(VERSION 3.31)

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

include(${PICO_SDK_PATH}/pico_sdk_init.cmake)

project(hall_effect_keypad C CXX ASM)

pico_sdk_init()

add_subdirectory(${FREERTOS_KERNEL_PATH}/portable/ThirdParty/GCC/RP2350_ARM_NTZ
    FreeRtos-Kernel)

add_executable(${TARGET_NAME}
    ${SRC}/hello.c)

target_link_libraries(${TARGET_NAME}
    pico_stdlib
    FreeRTOS-Kernel-Heap4
)

target_include_directories(${TARGET_NAME} PRIVATE ${INCLUDE})

pico_enable_stdio_usb(${TARGET_NAME} 1)

