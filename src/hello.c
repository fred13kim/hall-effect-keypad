#include <stdio.h>
#include "pico/stdlib.h"

#include "FreeRTOS.h"
#include "task.h"


int main(void){
    stdio_init_all();
    while(true) {
        printf("Senior Projects!\n");
        sleep_ms(1000);
    }
}


