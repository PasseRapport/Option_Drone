#include "app_sensors.h"
#include <stdio.h>
#include <string.h>

extern TIM_HandleTypeDef htim5;
extern UART_HandleTypeDef huart2;

HCSR04_HandleTypeDef hcsr04;

static void uart_print(const char *msg)
{
    HAL_UART_Transmit(&huart2, (uint8_t *)msg, strlen(msg), HAL_MAX_DELAY);
}

void App_Sensors_Init(void)
{
    HCSR04_Init(&hcsr04,
                TRIG_GPIO_Port, TRIG_Pin,
                ECHO_GPIO_Port, ECHO_Pin,
                &htim5);

    uart_print("HCSR04 init OK\r\n");
}

void App_Sensors_Run(void)
{
    char buffer[128];
    uint32_t distance_cm = 0;
    uint32_t min_distance = 999;
    uint32_t max_distance = 0;
    uint32_t success_count = 0;
    uint32_t fail_count = 0;

    uart_print("=== Test HC-SR04 ===\r\n\r\n");

    while (1)
    {
        distance_cm = 0;
        HCSR04_Trigger(&hcsr04);

        uint32_t start = HAL_GetTick();
        uint8_t measurement_ok = 0;

        while (!HCSR04_ReadDistanceCm(&hcsr04, &distance_cm))
        {
            if ((HAL_GetTick() - start) > 100)
            {
                // Timeout : pas de mesure valide
                measurement_ok = 0;
                fail_count++;
                break;
            }
        }

        // Si on est sorti de la boucle sans timeout
        if (distance_cm > 0)
        {
            measurement_ok = 1;
        }

        // Afficher seulement si la mesure est valide
        if (measurement_ok && distance_cm > 0 && distance_cm < 400)
        {
            success_count++;

            // Mettre à jour min/max
            if (distance_cm < min_distance) min_distance = distance_cm;
            if (distance_cm > max_distance) max_distance = distance_cm;

            snprintf(buffer, sizeof(buffer),
                     "[OK] Distance: %3lu cm | Pulse: %4lu us | Min: %3lu | Max: %3lu | Success: %lu\r\n",
                     distance_cm,
                     hcsr04.pulse_us,
                     min_distance,
                     max_distance,
                     success_count);
            uart_print(buffer);
        }
        else
        {
            snprintf(buffer, sizeof(buffer),
                     "[FAIL] Timeout ou distance invalide | Echecs: %lu\r\n",
                     fail_count);
            uart_print(buffer);
        }

        HAL_Delay(200);
    }
}
