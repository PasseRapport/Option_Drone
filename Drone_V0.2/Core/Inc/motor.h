#ifndef INC_MOTOR_H_
#define INC_MOTOR_H_

#include <stdint.h> // Required for uint32_t
// Include your specific STM32 HAL header, for example:
#include "stm32l4xx_hal.h" // Change 'f4' to your specific series (f1, g4, h7, etc.)
#include "main.h"

// Motors management


// Motor management structure

typedef struct Motor{
	TIM_HandleTypeDef* htim;
	uint32_t channel;
	float PercentageOfTotalPower;
}h_motor_t;


//=======
// Function declarations

int percentageToMicrosecondsAtHighState(int percentage);
void motor_Init(h_motor_t* h_motor);
void motor_SetPower(h_motor_t* h_motor, int percentage);
void motor_TurnOff(h_motor_t* h_motor);
void motor_ArmESC(h_motor_t* h_motor) ;
#endif /* INC_MOTOR_H_ */
