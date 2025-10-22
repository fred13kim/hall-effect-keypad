cmake_minimum_required(VERSION 3.31)

if (NOT DEFINED ENV{PICO_SDK_PATH})
    message(FATAL_ERROR "PICO_SDK_PATH DOES NOT EXIST")
endif()

message(STATUS "PICO_SDK_PATH EXISTS AT " $ENV{PICO_SDK_PATH})
set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})

set(PICO_BOARD pico2)
set(PICO_PLATFORM rp2350-arm-s)

include(${PICO_SDK_PATH}/pico_sdk_init.cmake)

project(hall_effect_keypad)

pico_sdk_init()
