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

// cs low:
// msg format:
// ex for channel 0 single mode
// 5'b11000
// |start|s/d mode|D2|D1|D0
// 
void mcp3008_read(mcp3008_inst_t *mcp_dev, mcp3008_channel_t ch) {
    uint8_t ch_config = 0x80 | ((ch & 0x07) << 4);
    uint8_t tx[3] = {
        0x01,       // start bit
        ch_config,  // config
        0x00,       // XX don't care
    };

    gpio_put(mcp_dev->cs_pin, 0);
    spi_write_blocking(mcp_dev->spi_dev, tx, sizeof(tx));
    gpio_put(mcp_dev->cs_pin, 1); }
