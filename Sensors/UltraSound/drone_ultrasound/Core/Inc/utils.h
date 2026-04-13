/*
 * utils.h
 *
 *  Created on: Apr 2, 2026
 *      Author: Ted
 */

#ifndef INC_UTILS_H_
#define INC_UTILS_H_

#include "main.h"

// Définir vos pins (à adapter selon votre config)
#define TRIG_PIN GPIO_PIN_0
#define TRIG_PORT GPIOA
#define ECHO_PIN GPIO_PIN_1
#define ECHO_PORT GPIOA

// Fonctions
void delay_us(uint32_t us);
float HC_SR04_Read(void);

#endif /* INC_UTILS_H_ */
