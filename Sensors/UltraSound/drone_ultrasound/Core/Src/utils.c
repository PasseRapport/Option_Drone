/*
 * utils.c
 *
 *  Created on: Apr 2, 2026
 *      Author: Ted
 */

/* Configuration du Timer pour mesurer en microsecondes */
// Prescaler = (SystemCoreClock / 1000000) - 1
// Pour obtenir une résolution de 1µs

#include "main.h"
#include "utils.h"// Ensures HAL and GPIO definitions are available

extern TIM_HandleTypeDef htim5;  // Déclaré dans main.c

/**
 * @brief Délai en microsecondes utilisant TIM5
 * @param us : nombre de microsecondes
 */
void delay_us(uint32_t us)
{
    __HAL_TIM_SET_COUNTER(&htim5, 0);
    while(__HAL_TIM_GET_COUNTER(&htim5) < us);
}

/**
 * @brief Lecture de la distance avec le HC-SR04
 * @return Distance en centimètres
 */
float HC_SR04_Read(void)
{
    uint32_t local_time = 0;
    float distance = 0;

    // 1. Envoyer une impulsion de 10µs sur TRIG
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_RESET);
    delay_us(2);
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_SET);
    delay_us(10);
    HAL_GPIO_WritePin(TRIG_PORT, TRIG_PIN, GPIO_PIN_RESET);

    // 2. Attendre que ECHO passe à HIGH (timeout 10ms)
    uint32_t timeout = 10000;  // 10ms
    while(HAL_GPIO_ReadPin(ECHO_PORT, ECHO_PIN) == GPIO_PIN_RESET)
    {
        if(--timeout == 0) return -1;  // Timeout
        delay_us(1);
    }

    // 3. Démarrer le compteur
    __HAL_TIM_SET_COUNTER(&htim5, 0);

    // 4. Attendre que ECHO repasse à LOW (timeout 30ms)
    timeout = 30000;  // 30ms (distance max ~400cm)
    while(HAL_GPIO_ReadPin(ECHO_PORT, ECHO_PIN) == GPIO_PIN_SET)
    {
        if(--timeout == 0) return -1;  // Timeout
        delay_us(1);
    }

    // 5. Lire le temps écoulé
    local_time = __HAL_TIM_GET_COUNTER(&htim5);

    // 6. Calculer la distance
    // Distance (cm) = (temps en µs × vitesse du son) / 2
    // Vitesse du son = 340 m/s = 0.034 cm/µs
    distance = (local_time * 0.034) / 2.0;

    return distance;
}
