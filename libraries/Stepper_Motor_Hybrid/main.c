/*
 * main.c
 *
 * Description:
 *     Test program for the stepper motor driver. This file tests key functionalities
 *     such as initialization, motor control (speed and position), and cleanup.
 *
 * Author: Matthew Martin
 * Date: 2024-Dec-10
 */

#include "motor_control_api.h" // The library being tested
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>


int main(void)
{
    // Initialize GPIO chip and lines
    const unsigned int gpio_pins[4] = {17, 27, 23, 24};
    int status = driver_init("/dev/gpiochip0", gpio_pins);
    printf("Driver initialization complete with status: %d\n", status);

    // Initialize the motor with target speed setting
    Motor_State_t *motor_state = motor_init(720);

   for (int i = 0; i < 5; i++)
   {
        int status_fullstep_position = motor_set_position_full_step(motor_state, 360);
        printf("Motor positioning complete with status: %d\n", status_fullstep_position);
   }


   for (int i = 0; i < 5; i++)
   {
        int status_halfstep_position = motor_set_position_half_step(motor_state, 360);
        printf("Motor positioning complete with status: %d\n", status_halfstep_position);
   }


    // Free motor
    int stop_status = motor_stop(motor_state);
    printf("Motor stopped with status: %d\n", stop_status);
}
