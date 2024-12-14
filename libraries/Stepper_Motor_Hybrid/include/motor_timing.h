/*
 * motor_timing.h
 *
 * Description:
 *     This file implements function prototypes for motor timing control
 *
 * Author: Matthew Martin
 * Date: 2024-Dec-09
 */


#include "motor_control_api.h"

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
 * @struct Motor_full_step_logic_t
 * @brief Represents the step logic for the motor
 *
 * This structure provides the step logic for the motor for full step mode
 */
typedef struct {
    enum gpiod_line_value gpio_step0[4];
    enum gpiod_line_value gpio_step1[4];
    enum gpiod_line_value gpio_step2[4];
    enum gpiod_line_value gpio_step3[4];
} Motor_full_step_logic_t;


/*
 * @struct Motor_half_step_logic_t
 * @brief Represents the step logic for the motor
 *
 * This structure provides the step logic for the motor for half step mode
 */
typedef struct {
    enum gpiod_line_value gpio_step0[4];
    enum gpiod_line_value gpio_step1[4];
    enum gpiod_line_value gpio_step2[4];
    enum gpiod_line_value gpio_step3[4];
    enum gpiod_line_value gpio_step4[4];
    enum gpiod_line_value gpio_step5[4];
    enum gpiod_line_value gpio_step6[4];
    enum gpiod_line_value gpio_step7[4];
} Motor_half_step_logic_t;

/* 
 * Initializes the motor control timing.
 * 
 * Parameters:
 *      motor_state is the pointer reference to the motor instance
 *      step_type is the type of motor step commanded (Full = 1, Half = 2)
 *      position is the amount in angular degrees commanded to move the motor.
  * Returns:
 *     0 on success, -1 on failure.
 */
int motor_drive(int step_type, float position);