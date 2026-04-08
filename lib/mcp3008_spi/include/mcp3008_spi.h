#ifndef MCP_3008_H
#define MCP_3008_H
#include "hardware/spi.h"
#include "hardware/gpio.h"

typedef struct {
    spi_inst_t *spi_dev;
    uint baudrate;
    uint cs_pin;
    uint miso_pin;
    uint mosi_pin;
    uint sck_pin;
} mcp3008_inst_t;

void mcp3008_init(mcp3008_inst_t *mcp_dev);

#endif // !MCP_3008_H
