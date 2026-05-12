add_library(mcp3008_spi STATIC mcp3008_spi.c)

target_include_directories(mcp3008_spi PUBLIC include)

target_link_libraries(mcp3008_spi pico_stdlib hardware_spi hardware_gpio)
