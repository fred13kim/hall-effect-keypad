#ifndef MCP_3008_H
#define MCP_3008_H
#include "hardware/spi.h"
#include "hardware/gpio.h"


// typedefs
typedef enum {
    MCP3008_CH0 = 0,
    MCP3008_CH1,
    MCP3008_CH2,
    MCP3008_CH3,
    MCP3008_CH4,
    MCP3008_CH5,
    MCP3008_CH6,
    MCP3008_CH7,
} mcp3008_channel_t;

typedef struct {
    spi_inst_t *spi_dev;
    uint baudrate;
    uint cs_pin;
    uint miso_pin;
    uint mosi_pin;
    uint sck_pin;
} mcp3008_inst_t;


void mcp3008_init(mcp3008_inst_t *mcp_dev);
int mcp3008_read(mcp3008_inst_t *mcp_dev, mcp3008_channel_t ch, uint16_t *data);

#endif // !MCP_3008_H
