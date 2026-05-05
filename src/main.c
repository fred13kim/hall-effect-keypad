#include "projdefs.h"
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "mcp3008_spi.h"
#include "ssd1306_i2c.h"
#include "FreeRTOS.h"
#include "task.h"
#include "tusb.h"

#define USB_TASK_STACK  512
#define ADC_TASK_STACK  512
#define USB_TASK_PRIO   (configMAX_PRIORITIES - 1)
#define ADC_TASK_PRIO   (configMAX_PRIORITIES - 2)

#define BAUDRATE 1000 * 1000
#define SCK_PIN 2
#define MOSI_PIN 3
#define MISO_PIN 4
#define CS_PIN 5
#define SDA_PIN 6
#define SCL_PIN 7
#define SSD_DEV0_ADDR 0x3C
#define SSD_DEV1_ADDR 0x3D
#define SSD_DEV_WIDTH 128
#define SSD_DEV_HEIGHT 64

#define I2C_BAUDRATE 400 * 1000

#define NUM_CHANNELS 4

static mcp3008_inst_t mcp = {
    .spi_dev	= spi0,
    .baudrate	= BAUDRATE,
    .mosi_pin	= MOSI_PIN,
    .miso_pin	= MISO_PIN,
    .sck_pin	= SCK_PIN,
    .cs_pin	    = CS_PIN,
};

static ssd1306_inst_t ssd_dev0 = {
    .i2c_dev = i2c1,
    .baudrate = I2C_BAUDRATE,
    .sda_pin = SDA_PIN,
    .scl_pin = SCL_PIN,
    .addr = SSD_DEV0_ADDR,
    .width = SSD_DEV_WIDTH,
    .height = SSD_DEV_HEIGHT
};

static ssd1306_inst_t ssd_dev1 = {
    .i2c_dev = i2c1,
    .baudrate = I2C_BAUDRATE,
    .sda_pin = SDA_PIN,
    .scl_pin = SCL_PIN,
    .addr = SSD_DEV1_ADDR,
    .width = SSD_DEV_WIDTH,
    .height = SSD_DEV_HEIGHT
};

static void display_lcd(void) {
    ssd1306_init(&ssd_dev0);
    ssd1306_init(&ssd_dev1);
    vTaskDelay(pdMS_TO_TICKS(100));
    ssd1306_clear(&ssd_dev0);
    ssd1306_clear(&ssd_dev1);
    ssd1306_draw_string(&ssd_dev0, 8, 0, 1, "The Cooper Union");
    ssd1306_draw_string(&ssd_dev0, 8, 12, 1, "Capstone Project");
    ssd1306_draw_string(&ssd_dev0, 8, 24, 1, "Analog Hall Effect");
    ssd1306_draw_string(&ssd_dev0, 8, 36, 1, "Keypad");
    ssd1306_draw_string(&ssd_dev1, 8, 0, 1, "Stephen Brockerhoff");
    ssd1306_draw_string(&ssd_dev1, 8, 12, 1, "Fred Kim");
    ssd1306_draw_string(&ssd_dev1, 8, 24, 1, "Anthony Kwon");
    ssd1306_draw_string(&ssd_dev1, 8, 36, 1, "Andrew Yuan");
    ssd1306_update(&ssd_dev0);
    ssd1306_update(&ssd_dev1);
}


void usb_device_task(void *param) {
    (void) param;
    tusb_init();
    while (true) {
        tud_task();
        taskYIELD();
    }
}

void adc_task(void *param) {
    (void) param;
    display_lcd();
    mcp3008_init(&mcp);
    while (true) {
        if (tud_hid_ready()) {
            uint16_t raw[4];
            for (mcp3008_channel_t ch = MCP3008_CH0; ch < NUM_CHANNELS; ch++) {
                mcp3008_read(&mcp, ch, &raw[ch]);
            }

            // Invert and scale: rest~500->0, pressed~270->1023
            uint16_t inv[4];
            for (int i = 0; i < 4; i++) {
                int16_t delta = (int16_t)500 - (int16_t)raw[i];
                if (delta < 0)    delta = 0;
                inv[i] = (uint16_t)(delta * 1023 / 230);
                if (inv[i] > 1023) inv[i] = 1023;
            }

            // Steering: CH0=left, CH2=right, differential centered at 512
            int16_t steering = 512 + ((int16_t)inv[2] - (int16_t)inv[0]) / 2;
            if (steering < 0)    steering = 0;
            if (steering > 1023) steering = 1023;

            struct __attribute__((packed)) {
                uint16_t x, y, z, rx;
                uint8_t  buttons;
            } report = {
                .x       = steering,  // steering (CH0 left, CH2 right)
                .y       = 512,       // unused, centered
                .z       = inv[3],    // throttle (CH3 up)
                .rx      = inv[1],    // brake (CH1 down)
                .buttons = 0,
            };

            tud_hid_report(0, &report, sizeof(report));
        }
        vTaskDelay(pdMS_TO_TICKS(1));
    }
}

int main(void) {
    stdio_init_all();

    xTaskCreate(usb_device_task, "USB", USB_TASK_STACK, NULL, USB_TASK_PRIO, NULL);
    xTaskCreate(adc_task,        "ADC", ADC_TASK_STACK, NULL, ADC_TASK_PRIO, NULL);

    vTaskStartScheduler();

    while (true) {}
}
