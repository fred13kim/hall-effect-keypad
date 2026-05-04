#ifndef SSD1306_I2C_H
#define SSD1306_I2C_H
#include "hardware/i2c.h"

typedef struct {
    i2c_inst_t *i2c_dev;
    uint baudrate;
    uint sda_pin;
    uint scl_pin;
} ssd1306_inst_t;

void ssd1306_init(ssd1306_inst_t *ssd_dev);

#endif // !SSD1306_I2C_H

