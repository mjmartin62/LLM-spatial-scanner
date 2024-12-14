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

int main(void)
{
    // Initialize GPIO chip and lines
    const unsigned int gpio_pins[4] = {17, 27, 23, 24};
    int status = driver_init("/dev/gpiochip0", gpio_pins);
    printf("Driver initialization complete with status: %d\n", status);

    // Initialize the motor with target speed setting
    int motor_init_status = motor_init(720);
    printf("Motor initialization complete with status: %d\n", motor_init_status);

    // Test full step
    for (int i = 0; i < 2; i++)
    {
            int status_01 = motor_set_position_full_step(360);
            printf("Motor positioning complete with status: %d\n", status_01);
    }


    for (int i = 0; i < 2; i++)
    {
            int status_02 = motor_set_position_full_step(-360);
            printf("Motor positioning complete with status: %d\n", status_02);
    }

    // Test half step
    for (int i = 0; i < 2; i++)
    {
            int status_03 = motor_set_position_half_step(360);
            printf("Motor positioning complete with status: %d\n", status_03);
    }


    for (int i = 0; i < 2; i++)
    {
            int status_04 = motor_set_position_half_step(-360);
            printf("Motor positioning complete with status: %d\n", status_04);
    }


    // Free motor
    int stop_status = motor_stop();
    printf("Motor stopped with status: %d\n", stop_status);
}
