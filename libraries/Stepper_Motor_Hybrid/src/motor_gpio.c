/*
 * motor_gpio.c
 *
 * Description:
 *     Implementation of GPIO-related functionality for the stepper motor driver. This
 *     file handles initialization, setting GPIO pins output states for motor control, and
 *     cleanup of resources.
 *
 * Author: Matthew Martin
 * Date: 2024-Dec-09
 */

#include "motor_gpio.h"
#include <stdio.h>
#include <stdlib.h> 

/* Static variables to hold GPIO chip and lines */
static struct gpiod_chip *chip = NULL;
struct gpiod_line_config *line_config = NULL;
struct gpiod_line_settings *line_settings = NULL;
struct gpiod_request_config *request_config = NULL;
struct gpiod_line_request *request = NULL;


int gpio_init(const char *gpiochip_name, const unsigned int *gpio_pins) 
{
    /* Open the GPIO chip */
    chip = gpiod_chip_open(gpiochip_name);
    if (!chip) {
        perror("gpiod_chip_open_by_name");
        return -1;
    }
    
    /* Create new line settings object and set GPIOs to output state */
    line_settings = gpiod_line_settings_new();
    if (!line_settings) {
    perror("gpiod_line_settings_new");
    gpiod_chip_close(chip);
    return -1;
    }
    gpiod_line_settings_set_direction(line_settings, GPIOD_LINE_DIRECTION_OUTPUT);

    /* Configure the lines */
    line_config = gpiod_line_config_new();
    if (!line_config) {
        perror("gpiod_line_config_new");
        gpiod_line_settings_free(line_settings);
        gpiod_chip_close(chip);
        return -1;
    }
    gpiod_line_config_add_line_settings(line_config, gpio_pins, 4, line_settings);

    /* Request the lines */
    request = gpiod_chip_request_lines(chip, request_config, line_config);
    if (request < 0) {
        perror("gpiod_chip_request_lines");
        gpiod_line_config_free(line_config);
        gpiod_line_settings_free(line_settings);
        gpiod_chip_close(chip);
        return -1;
    }

    /* Clean up configuration objects */
    gpiod_line_config_free(line_config);
    gpiod_line_settings_free(line_settings);

    return 0;
}


int gpio_set_states(enum gpiod_line_value *gpio_states)
{
    int status = gpiod_line_request_set_values(request, gpio_states);
    if (status != 0) {
        return -1;
    }

    return 0;
}