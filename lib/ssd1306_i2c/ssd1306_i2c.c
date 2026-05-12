#include "ssd1306_i2c.h"
#include "ssd1306_cmd.h"
#include "font.h"
#include <pico/error.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

inline static int ssd1306_write_raw(ssd1306_inst_t *ssd_dev, const uint8_t *src,
									size_t len)
{
	int ret =
		i2c_write_blocking(ssd_dev->i2c_dev, ssd_dev->addr, src, len, false);
	switch (ret) {
	case PICO_ERROR_GENERIC:
		printf("ERROR: PICO_ERROR_GENERIC\n");
		break;
	case PICO_ERROR_TIMEOUT:
		printf("ERROR: PICO_ERROR_TIMEOUT\n");
		break;
	default:
		break;
	}
	return ret;
}

inline static int ssd1306_write_cmd(ssd1306_inst_t *ssd_dev, uint8_t val)
{
	uint8_t cmd[2] = { 0x00, val };
	int		ret	   = ssd1306_write_raw(ssd_dev, cmd, sizeof(cmd));
	return ret;
}


void ssd1306_init(ssd1306_inst_t *ssd_dev)
{
	i2c_init(ssd_dev->i2c_dev, ssd_dev->baudrate);

	gpio_set_function(ssd_dev->sda_pin, GPIO_FUNC_I2C);
	gpio_set_function(ssd_dev->scl_pin, GPIO_FUNC_I2C);
	gpio_pull_up(ssd_dev->sda_pin);
	gpio_pull_up(ssd_dev->scl_pin);

	ssd_dev->pages	 = ssd_dev->height / 8;
	ssd_dev->bufsize = (ssd_dev->pages) * (ssd_dev->width);
	ssd_dev->buffer	 = malloc(ssd_dev->bufsize + 1);
	if ((ssd_dev->buffer) == NULL) {
		ssd_dev->bufsize = 0;
		return;
	}

	++(ssd_dev->buffer);

	uint8_t init_seq[] = {
		/* power */
		SSD1306_CMD_DISPLAY_OFF,

		/* timing and driving scheme */
		SSD1306_CMD_SET_DISPLAY_CLK_DIV,
		0x80,
		SSD1306_CMD_SET_MUX_RATIO,
		ssd_dev->height - 1,
		SSD1306_CMD_SET_DISPLAY_OFFSET,
		0x00,

		/* resolution and layout */
		SSD1306_CMD_SET_START_LINE,

		/* charge pump */
		SSD1306_CMD_CHARGE_PUMP,
		SSD1306_CHARGE_PUMP_ENABLE,

		/* hardware configuration */
		SSD1306_CMD_SET_SEG_REMAP_1,
		SSD1306_CMD_SET_COM_SCAN_DEC,
		SSD1306_CMD_SET_COM_PINS,
		ssd_dev->width > 2 * ssd_dev->height ? SSD1306_COM_PINS_SEQUENTIAL :
											   SSD1306_COM_PINS_ALTERNATIVE,

		/* display */
		SSD1306_CMD_SET_CONTRAST,
		0xFF,
		SSD1306_CMD_SET_PRECHARGE,
		SSD1306_PRECHARGE_PHASE2_15 | SSD1306_PRECHARGE_PHASE1_1,
		SSD1306_CMD_SET_VCOMH_DESELECT,
		SSD1306_VCOMH_083_VCC,
		SSD1306_CMD_DISPLAY_ALL_ON_RESUME,
		SSD1306_CMD_NORMAL_DISPLAY,

		/* addressing */
		SSD1306_CMD_SET_MEM_ADDR_MODE,
		SSD1306_MEM_ADDR_HORIZONTAL,

		/* done */
		SSD1306_CMD_DISPLAY_ON,
	};

	for (size_t i = 0; i < sizeof(init_seq); i++) {
		ssd1306_write_cmd(ssd_dev, init_seq[i]);
	}
}

void ssd1306_clear(ssd1306_inst_t *ssd_dev)
{
	memset(ssd_dev->buffer, 0, ssd_dev->bufsize);
}

void ssd1306_update(ssd1306_inst_t *ssd_dev)
{
	uint8_t cmd_seq[] = { SSD1306_CMD_SET_COL_ADDR,	 0, ssd_dev->width - 1,
						  SSD1306_CMD_SET_PAGE_ADDR, 0, ssd_dev->pages - 1 };

	if (ssd_dev->width == 64) {
		cmd_seq[1] += 32;
		cmd_seq[2] += 32;
	}

	for (size_t i = 0; i < sizeof(cmd_seq); i++) {
		ssd1306_write_cmd(ssd_dev, cmd_seq[i]);
	}

	*(ssd_dev->buffer - 1) = 0x40;
	ssd1306_write_raw(ssd_dev, ssd_dev->buffer - 1, ssd_dev->bufsize + 1);
}

void ssd1306_draw_pixel(ssd1306_inst_t *p, uint32_t x, uint32_t y)
{
	if (x >= p->width || y >= p->height)
		return;

	p->buffer[x + p->width * (y >> 3)] |=
		0x1 << (y & 0x07); // y>>3==y/8 && y&0x7==y%8
}


void ssd1306_draw_square(ssd1306_inst_t *ssd_dev, uint32_t x, uint32_t y,
						 uint32_t width, uint32_t height)
{
	for (uint32_t i = 0; i < width; ++i)
		for (uint32_t j = 0; j < height; ++j)
			ssd1306_draw_pixel(ssd_dev, x + i, y + j);
}

void ssd1306_draw_char_with_font(ssd1306_inst_t *ssd_dev, uint32_t x,
								 uint32_t y, uint32_t scale,
								 const uint8_t *font, char c)
{
	if (c < font[3] || c > font[4])
		return;

	uint32_t parts_per_line = (font[0] >> 3) + ((font[0] & 7) > 0);
	for (uint8_t w = 0; w < font[1]; ++w) { // width
		uint32_t pp =
			(c - font[3]) * font[1] * parts_per_line + w * parts_per_line + 5;
		for (uint32_t lp = 0; lp < parts_per_line; ++lp) {
			uint8_t line = font[pp];

			for (int8_t j = 0; j < 8; ++j, line >>= 1) {
				if (line & 1)
					ssd1306_draw_square(ssd_dev, x + w * scale,
										y + ((lp << 3) + j) * scale, scale,
										scale);
			}

			++pp;
		}
	}
}

void ssd1306_draw_string_with_font(ssd1306_inst_t *ssd_dev, uint32_t x,
								   uint32_t y, uint32_t scale,
								   const uint8_t *font, const char *s)
{
	for (int32_t x_n = x; *s; x_n += (font[1] + font[2]) * scale) {
		ssd1306_draw_char_with_font(ssd_dev, x_n, y, scale, font, *(s++));
	}
}

void ssd1306_draw_char(ssd1306_inst_t *ssd_dev, uint32_t x, uint32_t y,
					   uint32_t scale, char c)
{
	ssd1306_draw_char_with_font(ssd_dev, x, y, scale, font_8x5, c);
}

void ssd1306_draw_string(ssd1306_inst_t *ssd_dev, uint32_t x, uint32_t y,
						 uint32_t scale, const char *s)
{
	ssd1306_draw_string_with_font(ssd_dev, x, y, scale, font_8x5, s);
}
