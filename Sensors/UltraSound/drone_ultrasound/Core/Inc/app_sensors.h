#ifndef APP_SENSORS_H
#define APP_SENSORS_H

#include "main.h"
#include "hcsr04.h"

extern HCSR04_HandleTypeDef hcsr04;

void App_Sensors_Init(void);
void App_Sensors_Run(void);


#endif
