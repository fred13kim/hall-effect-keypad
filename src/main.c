#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/adc.h"
#include "FreeRTOS.h"
#include "task.h"
#include "tusb.h"

#define ADC_GPIO        26
#define ADC_CHANNEL     0
#define USB_TASK_STACK  512
#define ADC_TASK_STACK  512
#define USB_TASK_PRIO   (configMAX_PRIORITIES - 1)
#define ADC_TASK_PRIO   (configMAX_PRIORITIES - 2)

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
    //const float conversion_factor = 3.3f / (1 << 12);
    //char buf[64];

    adc_init();
    adc_gpio_init(ADC_GPIO);
    adc_select_input(ADC_CHANNEL);

    /* CDC ADC TASK
    while (true) {
        if (tud_ready()) {
            uint16_t raw = adc_read();
            float volts = raw * conversion_factor;

            int len = snprintf(buf, sizeof(buf),
                               "RAW: 0x%03x, VOLTS: %.4f V\r\n", raw, volts);

            tud_cdc_write(buf, len);
            tud_cdc_write_flush();
        }
        vTaskDelay(pdMS_TO_TICKS(10)); // 100Hz sample rate
    }*/
    
    while (true) {
	    if (tud_hid_ready()) {
		    uint16_t raw = adc_read();
		    tud_hid_report(0, &raw, sizeof(raw));
	    }
	    vTaskDelay(pdMS_TO_TICKS(10));
    }

    /* test hid report without ADC
    uint16_t test = 0;

    while(true) {
	    if (tud_hid_ready()) {
		    tud_hid_report(0, &test, sizeof(test));
		    test = (test +64) & 0xFFF;
	    }
	    vTaskDelay(pdMS_TO_TICKS(10));
    }
    void*/ 
}

int main(void) {
    stdio_init_all();

    xTaskCreate(usb_device_task, "USB", USB_TASK_STACK, NULL, USB_TASK_PRIO, NULL);
    xTaskCreate(adc_task,        "ADC", ADC_TASK_STACK, NULL, ADC_TASK_PRIO, NULL);

    vTaskStartScheduler();

    while (true) {}
}
