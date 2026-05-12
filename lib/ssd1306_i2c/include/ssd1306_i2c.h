#ifndef SSD1306_I2C_H
#define SSD1306_I2C_H
#include "hardware/i2c.h"
#include "hardware/gpio.h"

typedef struct {
	i2c_inst_t *i2c_dev;
	uint		baudrate;
	uint		sda_pin;
	uint		scl_pin;

	uint8_t	 addr;
	uint8_t	 width;
	uint8_t	 height;
	uint8_t	 pages;
	uint8_t *buffer;
	size_t	 bufsize;
} ssd1306_inst_t;

void ssd1306_init(ssd1306_inst_t *ssd_dev);
void ssd1306_update(ssd1306_inst_t *ssd_dev);
void ssd1306_clear(ssd1306_inst_t *ssd_dev);

void ssd1306_draw_pixel(ssd1306_inst_t *p, uint32_t x, uint32_t y);
void ssd1306_draw_square(ssd1306_inst_t *p, uint32_t x, uint32_t y,
						 uint32_t width, uint32_t height);
void ssd1306_draw_char_with_font(ssd1306_inst_t *p, uint32_t x, uint32_t y,
								 uint32_t scale, const uint8_t *font, char c);

void ssd1306_draw_string_with_font(ssd1306_inst_t *p, uint32_t x, uint32_t y,
								   uint32_t scale, const uint8_t *font,
								   const char *s);

void ssd1306_draw_char(ssd1306_inst_t *p, uint32_t x, uint32_t y,
					   uint32_t scale, char c);
void ssd1306_draw_string(ssd1306_inst_t *p, uint32_t x, uint32_t y,
						 uint32_t scale, const char *s);
#endif // !SSD1306_I2C_H
