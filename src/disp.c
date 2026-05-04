#include <stdio.h>
#include "pico/stdlib.h"
#include "ssd1306_i2c.h"

static ssd1306_inst_t ssd0 = {
    .i2c_dev = i2c1,
    .baudrate = 400 * 1000,
    .sda_pin = 6,
    .scl_pin = 7,
    
    .addr = 0x3c,
    .width = 128,
    .height = 64
};
static ssd1306_inst_t ssd1 = {
    .i2c_dev = i2c1,
    .baudrate = 400 * 1000,
    .sda_pin = 6,
    .scl_pin = 7,
    
    .addr = 0x3d,
    .width = 128,
    .height = 64
};

int main(void) {
    stdio_init_all();
    printf("DEV START\n");

    ssd1306_init(&ssd0);
    ssd1306_init(&ssd1);
    ssd1306_clear(&ssd0);
    ssd1306_clear(&ssd1);


    ssd1306_draw_string(&ssd0, 8, 0, 1, "The Cooper Union");
    ssd1306_draw_string(&ssd0, 8, 12, 1, "Analog Hall Effect");
    ssd1306_draw_string(&ssd0, 8, 24, 1, "Keyboard Switches");
    ssd1306_draw_string(&ssd1, 8, 0, 1, "Stephen Brockerhoff");
    ssd1306_draw_string(&ssd1, 8, 12, 1, "Fred Kim");
    ssd1306_draw_string(&ssd1, 8, 24, 1, "Anthony Kwon");
    ssd1306_draw_string(&ssd1, 8, 36, 1, "Andrew Yuan");
    ssd1306_update(&ssd0);
    ssd1306_update(&ssd1);

    for (;;)
    {
        printf("hello");
        sleep_ms(1000);
    }
}
