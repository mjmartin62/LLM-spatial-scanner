/*
 * motor_control_api.c
 *
 * Description:
 *     This file implements the high-level API for controlling a stepper motor. It provides
 *     functions to initialize the motor, control its speed and position, start and stop
 *     operation, and perform cleanup. The implementation delegates detailed functionality
 *     to lower-level modules for GPIO management and timing.
 *
 * Author: Matthew Martin
 * Date: 2024-Dec-09
 */

#include "motor_control_api.h" 
#include "motor_gpio.h"   
#include "motor_timing.h" 

// GPIO Initialization output states to ensure no current is going through the motor windings
enum gpiod_line_value gpio_initial_states[] = {GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_INACTIVE};

/* Instantiate motor instance for global access */
Motor_State_t *motor_state = NULL;

int driver_init(const char* gpiochip_name, const unsigned int* gpio_pins) 
{
    int gpio_status = gpio_init(gpiochip_name, gpio_pins);
    if (gpio_status){
        return -1;
    }

    int initial_status = gpio_set_states(gpio_initial_states);
    if (initial_status){
        return -1;
    }

    return 0;
}

int motor_init(float speed) 
{
    motor_state = malloc(sizeof(Motor_State_t));
    if (!motor_state) {
        return -1; // Handle memory allocation failure
    }

    // Initialize motor states
    motor_state->operational = false;
    motor_state->speed = speed;
    motor_state->position = 0;
    motor_state->last_step = 0;

    return 0;
}


int motor_set_position_full_step(float position) 
{
    // Drive motor
    int step_type = 1;
    int status = motor_drive(step_type, position);
    if (status){
        return -1;
    }

    return 0;
}

int motor_set_position_half_step(float position) 
{
    // Drive motor
    int step_type = 2;
    int status = motor_drive(step_type, position);
    if (status){
        return -1;
    }

    return 0;
}


int motor_stop(void) 
{
    // Set GPIOs to inactive
    int initial_status = gpio_set_states(gpio_initial_states);
    if (initial_status){
        return -1;
    }

    // Clean up memory
    free(motor_state);
    motor_state = NULL;

    return 0;
}

