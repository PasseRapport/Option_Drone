#include "motor.h"
#include "stm32l4xx_hal.h"
#include "stdio.h"

#define COUNTER_PERIOD 19999 // Maximal counter value
#define MIN_PWM 1000 // µs, basic value for 0%
#define MAX_PWM 2000 // µs, basic value for 100%

void motor_ArmESC(h_motor_t* h_motor) {
    motor_SetPower(h_motor, 0);
    HAL_Delay(100);
    motor_SetPower(h_motor, 5); // Low value to not have a violent start
    HAL_Delay(100);
}

int percentageToMicrosecondsAtHighState(int percentage) {
    if (percentage < 0) percentage = 0; // Minimal value
    if (percentage > 100) percentage = 100; // Maximal value

    int pulse_length = MIN_PWM + ((MAX_PWM - MIN_PWM) * percentage) / 100; // Convert percentage into µs
    return (pulse_length * COUNTER_PERIOD) / 20000;
}

void motor_SetPower(h_motor_t* h_motor, int targetPercentage) {
    int step = (targetPercentage > h_motor->PercentageOfTotalPower) ? 1 : -1; // Determine direction
    int currentPercentage = h_motor->PercentageOfTotalPower;

    while (currentPercentage != targetPercentage) { // Gradually adjust the power percentage to the target value
        currentPercentage += step;

        int microsecondsAtHighState = percentageToMicrosecondsAtHighState(currentPercentage);
        __HAL_TIM_SET_COMPARE(h_motor->htim, h_motor->channel, microsecondsAtHighState); // Set the PWM duty cycle

        h_motor->PercentageOfTotalPower = currentPercentage;
        //HAL_Delay(20); // Delay adjustable for smoother or faster transitions
    }
}


void motor_Init(h_motor_t* h_motor) {
	HAL_TIM_PWM_Start(h_motor->htim, h_motor->channel);
	motor_ArmESC(h_motor);
}


void motor_Security(h_motor_t* h_motor) {
	motor_SetPower(h_motor, 0);
	while(1){

	}
}

void motor_TurnOn(h_motor_t* h_motor) {
	motor_SetPower(h_motor, 5);
}
