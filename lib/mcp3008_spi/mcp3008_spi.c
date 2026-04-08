#include "mcp3008_spi.h"

#define RATE_100_KHZ 100000

void mcp3008_init(mcp3008_inst_t *mcp_dev) {
    spi_init(mcp_dev->spi_dev, mcp_dev->baudrate);

    gpio_set_function(mcp_dev->miso_pin, GPIO_FUNC_SPI);
    gpio_set_function(mcp_dev->mosi_pin, GPIO_FUNC_SPI);
    gpio_set_function(mcp_dev->sck_pin, GPIO_FUNC_SPI);

    gpio_init(mcp_dev->cs_pin);
    gpio_set_dir(mcp_dev->cs_pin, GPIO_OUT);
    gpio_put(mcp_dev->cs_pin, 1);
}
