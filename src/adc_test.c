#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/adc.h"

#include "FreeRTOS.h"
#include "task.h"


int main(void){
    stdio_init_all();

    adc_init();
    adc_gpio_init(26);
    adc_select_input(0);

    printf("=== ADC TEST ===");

    while(true) {
        const float conversion_factor = 3.3f / (1 << 12);
        uint16_t res = adc_read();
        printf("RAW: 0x%03x, VOLTS: %f V\n", res, res * conversion_factor);
        sleep_ms(1);
    }
}


