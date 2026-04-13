#ifndef HCSR04_H
#define HCSR04_H

#include "main.h"
#include <stdint.h>

typedef struct
{
    GPIO_TypeDef *trig_port;
    uint16_t trig_pin;

    GPIO_TypeDef *echo_port;
    uint16_t echo_pin;

    TIM_HandleTypeDef *htim_us;

    volatile uint8_t waiting_falling;
    volatile uint32_t t_rising;
    volatile uint32_t t_falling;
    volatile uint32_t pulse_us;
    volatile uint32_t distance_cm;
    volatile uint8_t measurement_ready;
    volatile uint8_t measurement_in_progress;
    volatile uint8_t timeout;
} HCSR04_HandleTypeDef;

void HCSR04_Init(HCSR04_HandleTypeDef *sensor,
                 GPIO_TypeDef *trig_port, uint16_t trig_pin,
                 GPIO_TypeDef *echo_port, uint16_t echo_pin,
                 TIM_HandleTypeDef *htim_us);

HAL_StatusTypeDef HCSR04_Trigger(HCSR04_HandleTypeDef *sensor);
void HCSR04_EchoCallback(HCSR04_HandleTypeDef *sensor);
uint8_t HCSR04_ReadDistanceCm(HCSR04_HandleTypeDef *sensor, uint32_t *distance_cm);

#endif
