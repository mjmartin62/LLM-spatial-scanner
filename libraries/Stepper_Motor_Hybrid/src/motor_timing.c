/*
 * motor_timing.c
 *
 * Description:
 *     This file implements the timing control to modulate the GPIO state changes for motor control.
 *
 * Author: Matthew Martin
 * Date: 2024-Dec-09
 */

#include "motor_timing.h"
#include "motor_control_api.h"
#include "motor_gpio.h"
#include <math.h>
#include <unistd.h>

extern Motor_State_t *motor_state;

/* GPIO state control logic */
// Full Step Logic
Motor_full_step_logic_t motor_full_step_logic = {
    .gpio_step0 = {GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE},
    .gpio_step1 = {GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE},
    .gpio_step2 = {GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE},
    .gpio_step3 = {GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE}
};
// Half Step Logic
Motor_half_step_logic_t motor_half_step_logic = {
    .gpio_step0 = {GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE},
    .gpio_step1 = {GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE},
    .gpio_step2 = {GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_INACTIVE},
    .gpio_step3 = {GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE},
    .gpio_step4 = {GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE},
    .gpio_step5 = {GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE},
    .gpio_step6 = {GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_INACTIVE},
    .gpio_step7 = {GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE, GPIOD_LINE_VALUE_ACTIVE, GPIOD_LINE_VALUE_INACTIVE}
};

int motor_drive(int step_type, float position)
{
    
    // Full step motor control
    if (step_type == 1)
    {
        float full_step_size = 1.8;
        float full_step_num_steps = abs(position) / full_step_size;
        int pause_us = (int)(1e6 / (motor_state->speed) * full_step_size);
        int last_step = motor_state->last_step;
        int executed_steps = 0;
        
        // Execute motor steps
        while (executed_steps < full_step_num_steps) {
            if (position > 0)
            {
                last_step = (last_step + 1) % 4;
            } else
            {
                last_step = (last_step + 3) % 4;
            }
        
            switch (last_step)
            {
                case 0:
                    gpio_set_states(motor_full_step_logic.gpio_step0);
                    break;
                case 1:
                    gpio_set_states(motor_full_step_logic.gpio_step1);
                    break;
                case 2:
                    gpio_set_states(motor_full_step_logic.gpio_step2);
                    break;   
                case 3:
                    gpio_set_states(motor_full_step_logic.gpio_step3);
                    break; 
                default:
                    break;
            }
                // Software pause to control speed and updated step count
                executed_steps++;
                usleep(pause_us);
        }
        // Update the step state and position
        motor_state->last_step = last_step;
        motor_state->position += position;
        return 0;
    } 
    
    // Half step motor control
    else if (step_type == 2)
    {
        float half_step_size = 0.9;
        float half_step_num_steps = abs(position) / half_step_size;
        int pause_us = (int)(1e6 / (motor_state->speed) * half_step_size);
        int last_step = motor_state->last_step;
        int executed_steps = 0;
        
        // Execute motor steps
        while (executed_steps < half_step_num_steps) {
            if (position > 0)
            {
                last_step = (last_step + 1) % 8;
            } else
            {
                last_step = (last_step + 7) % 8;
            }
        
            switch (last_step)
            {
                case 0:
                    gpio_set_states(motor_half_step_logic.gpio_step0);
                    break;
                case 1:
                    gpio_set_states(motor_half_step_logic.gpio_step1);
                    break;
                case 2:
                    gpio_set_states(motor_half_step_logic.gpio_step2);
                    break;   
                case 3:
                    gpio_set_states(motor_half_step_logic.gpio_step3);
                    break; 
                case 4:
                    gpio_set_states(motor_half_step_logic.gpio_step4);
                    break;
                case 5:
                    gpio_set_states(motor_half_step_logic.gpio_step5);
                    break;
                case 6:
                    gpio_set_states(motor_half_step_logic.gpio_step6);
                    break;   
                case 7:
                    gpio_set_states(motor_half_step_logic.gpio_step7);
                    break; 
                default:
                    break;
            }
                // Software pause to control speed and updated step count
                executed_steps++;
                usleep(pause_us);
        }
        // Update the step state and position
        motor_state->last_step = last_step;
        motor_state->position += position;
        return 0;
    } 
    
    else
    {
        return -1;
    }
    
}