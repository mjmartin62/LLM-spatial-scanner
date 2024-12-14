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
 * @struct Motor_State_t
 * @brief Represents the state of a motor.
 *
 * This structure is used to track and modify the state of a motor,
 * including whether it is operational, its current speed, and its position.
 * It is typically managed dynamically using the API functions provided.
 */
typedef struct 
{
    bool operational;
    float speed;
    int position;
    int last_step;
    
} Motor_State_t;


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
Motor_State_t* motor_init(float speed);

/*
 * Moves the motor to a specified target position using full step mode.
 * 
 * Parameters:
 *     position - The desired target position in steps.
 */
int motor_set_position_full_step(Motor_State_t* motor_state, int position);

/*
 * Moves the motor to a specified target position using half step motor control.
 * 
 * Parameters:
 *     position - The desired target position in steps.
 */
int motor_set_position_half_step(Motor_State_t* motor_state, int position);

/*
 * Stops motor operation and halts all movement.
 * Stops energizing all motor phases.
 * Cleans up motor control resources, including GPIOs and memory.
 */
int motor_stop(Motor_State_t* motor_state);

#endif // MOTOR_CONTROL_API_H
