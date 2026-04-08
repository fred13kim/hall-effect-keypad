#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/adc.h"
#include "mcp3008_spi.h"

#include "FreeRTOS.h"
#include "task.h"

#define SPI_PORT spi0
#define SPI_BAUDRATE 500 * 1000

#define MISO_PIN 4
#define CS_PIN 5
#define SCK_PIN 6
#define MOSI_PIN 7

static mcp3008_inst_t mcp_dev = {
    .spi_dev = SPI_PORT,
    .baudrate = SPI_BAUDRATE,
    .cs_pin = CS_PIN,
    .miso_pin = MISO_PIN,
    .mosi_pin = MOSI_PIN,
    .sck_pin = SCK_PIN,
};

int main(void){
    stdio_init_all();

    mcp3008_init(&mcp_dev);
    

    /*
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
    */
}


