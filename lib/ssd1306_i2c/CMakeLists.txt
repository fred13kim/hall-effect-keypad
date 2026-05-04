add_library(ssd1306_i2c STATIC ssd1306_i2c.c)

target_include_directories(ssd1306_i2c PUBLIC include)

target_link_libraries(ssd1306_i2c
    pico_stdlib
    hardware_i2c
    hardware_gpio
)
