cmake_minimum_required(VERSION 3.31)

if (DEFINED ENV{PICO_SDK_PATH})
    message(STATUS "PICO_SDK_PATH EXISTS AT " $ENV{PICO_SDK_PATH})
else()
    message(FATAL_ERROR "PICO_SDK_PATH DOES NOT EXIST")
endif()

project(hall_effect_keypad)
