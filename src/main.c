#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "mcp3008_spi.h"
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

#define NUM_CHANNELS 4

static mcp3008_inst_t mcp = {
    .spi_dev	= spi0,
    .baudrate	= BAUDRATE,
    .mosi_pin	= MOSI_PIN,
    .miso_pin	= MISO_PIN,
    .sck_pin	= SCK_PIN,
    .cs_pin	    = CS_PIN,
};


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

    mcp3008_init(&mcp);

    while (true) {
	    if (tud_hid_ready()) {
		    uint16_t raw[4];
		    for (mcp3008_channel_t ch = MCP3008_CH0; ch < NUM_CHANNELS; ch++) {
			    mcp3008_read(&mcp, ch, &raw[ch]);
		    }
		    tud_hid_report(0, raw, sizeof(raw));
	    }
	    vTaskDelay(pdMS_TO_TICKS(10));
    }
}

int main(void) {
    stdio_init_all();

    xTaskCreate(usb_device_task, "USB", USB_TASK_STACK, NULL, USB_TASK_PRIO, NULL);
    xTaskCreate(adc_task,        "ADC", ADC_TASK_STACK, NULL, ADC_TASK_PRIO, NULL);

    vTaskStartScheduler();

    while (true) {}
}
