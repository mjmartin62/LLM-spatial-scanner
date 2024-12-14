#ifndef MOTOR_CONTROL_API_H
#define MOTOR_CONTROL_API_H

/*
 * motor_control_api.h
 *
 * Description:
 *     This header file declares the high-level API for controlling a stepper motor.
 *     It provides function prototypes for initializing, controlling speed and position,
 *     starting and stopping the motor, and cleaning up resources.
 *
 * Author: Matthew Martin
 * Date: 2024-Dec-09
 */


#include <stdbool.h>
#include <stdlib.h>
#include "motor_gpio.h"


/* 
 * Initializes the motor control drive system.
 * 
 * Parameters:
 *     gpiochip_name - The name of the GPIO chip to use (e.g., "gpiochip0").
 *     gpio_pins - the 4 gpio single board computer pins to drive the H-bridge.
 */
int driver_init(const char* gpiochip_name, const unsigned int* gpio_pins);

/*
 * Starts motor operation by setting the initial speed and motor control logic.
 * 
 * Parameters:
 *     speed - The desired motor speed in steps per second.
 */
int motor_init(float speed);

/*
 * Moves the motor to a specified target position using full step mode.
 * 
 * Parameters:
 *     position - The desired target position in steps.
 */
int motor_set_position_full_step(float position);

/*
 * Moves the motor to a specified target position using half step motor control.
 * 
 * Parameters:
 *     position - The desired target position in steps.
 */
int motor_set_position_half_step(float position);

/*
 * Stops motor operation and halts all movement.
 * Stops energizing all motor phases.
 * Cleans up motor control resources, including GPIOs and memory.
 */
int motor_stop(void);

#endif // MOTOR_CONTROL_API_H
