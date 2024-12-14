#ifndef MOTOR_GPIO_H
#define MOTOR_GPIO_H

/*
 * motor_gpio.h
 *
 * Description:
 *     Header file for GPIO-related functionality in the stepper motor driver. This file
 *     declares functions for initializing and controlling the GPIO pins required for
 *     the stepper motor.
 *
 * Author: Matthew Martin
 * Date: 2024-Dec-09
 */

#include <gpiod.h> 

/*
 * Initializes the GPIO pins required for stepper motor control.
 *
 * Parameters:
 *     gpiochip_name - Name of the GPIO chip (e.g., "gpiochip0").
 *     gpio_pins - the gpio pin numbers
 * Returns:
 *     0 on success, -1 on failure.
 */
int gpio_init(const char *gpiochip_name, const unsigned int *gpio_pins);

/*
 * Sets the GPIO pins to a specific step in the sequence.
 *
 * Parameters:
 *     step - The current step in the stepping sequence.
 *
 * Returns:
 *     0 on success, -1 on failure.
 */
int gpio_set_states(enum gpiod_line_value *gpio_states);

#endif // MOTOR_GPIO_H
