"""
Python wrapper for linux system driver for bipolar stepper motor control logic (Full and Half Step)

"""

import ctypes
import os
import time

class Stepper_Motor:
    def __init__(self, library_path=None, chip="/dev/gpiochip0", gpio_pins=[0, 0, 0, 0], speed=0):
        if library_path is None:
            library_path = os.path.join(
            os.path.dirname(__file__), "../libraries/Stepper_Motor_Hybrid/motor_driver.so")
        
        self._lib = ctypes.CDLL(library_path)
        self._chip = chip.encode('utf-8')
        self._gpio_pins = (ctypes.c_int * len(gpio_pins))(*gpio_pins)
        self._speed = ctypes.c_float(speed)
        self._position = float(0)

        # Initialize the motor driver and motor upon instantiation
        self._bind_functions()
        self._driver_init()
        self._motor_init()

    # Getter method for _position
    def get_position(self):
        return self._position

    # Setter method for _position
    def set_position(self, position):
        if isinstance(position, (int, float)):
            self._position = float(position)
        else:
            raise ValueError("Position must be a number (int or float).")

    def _bind_functions(self):
        '''
        Bind callable c-library functions with python functions
        '''
        # Initialize motor driver
        self._lib.driver_init.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
        self._lib.driver_init.restype = ctypes.c_int

        # Initialize motor
        self._lib.motor_init.argtypes = [ctypes.c_float]
        self._lib.motor_init.restype = ctypes.c_int

        # Position motor with full step
        self._lib.motor_set_position_full_step.argtypes = [ctypes.c_float]
        self._lib.motor_set_position_full_step.restype = ctypes.c_int

        # Position motor with half step
        self._lib.motor_set_position_half_step.argtypes = [ctypes.c_float]
        self._lib.motor_set_position_half_step.restype = ctypes.c_int

        # Stop motor
        self._lib.motor_stop.argtypes = []
        self._lib.motor_stop.restype = ctypes.c_int

        
    def _driver_init(self):
        '''
        Initializes gpio chip and gpio pins
        '''
        status = self._lib.driver_init(self._chip, self._gpio_pins)
        if status == 0:
            print("Motor Driver Initialized....")
        else:
            raise RuntimeError(f"Motor Driver initialization failed with status: {status}")
        
    def _motor_init(self):
        '''
        Initialize motor with target speed
        '''
        status = self._lib.motor_init(self._speed)
        if status == 0:
            print("Motor Initialized....")
        else:
            raise RuntimeError(f"Motor initialization failed with status: {status}")
        
    def motor_set_position_full_step(self, position):
        '''
        Command motor movement postion using full step motor control
        '''
        self.set_position(position)
        status = self._lib.motor_set_position_full_step(ctypes.c_float(self._position))
        if status == 0:
            print("Motor full step positioning complete....")
        else:
            raise RuntimeError(f"Motor full step positioning failed with status: {status}")

    def motor_set_position_half_step(self, position):
        '''
        Command motor movement postion using half step motor control
        '''
        self.set_position(position)
        status = self._lib.motor_set_position_half_step(ctypes.c_float(self._position))
        if status == 0:
            print("Motor half step positioning complete....")
        else:
            raise RuntimeError(f"Motor half step positioning failed with status: {status}")

    def motor_stop(self):
        '''
        Halt current to the motor and clean up memory
        '''
        status = self._lib.motor_stop()
        if status == 0:
            print("Motor stop complete....")
        else:
            raise RuntimeError(f"Motor sotp failed with status: {status}")

if __name__ == "__main__":
    
    print("Starting coms....")
    stepper_motor = Stepper_Motor(chip="/dev/gpiochip0", gpio_pins=[17, 27, 23, 24], speed=720)
    stepper_motor.motor_set_position_full_step(360)
    time.sleep(1)
    stepper_motor.motor_set_position_half_step(-180)
    time.sleep(1)
    stepper_motor.motor_set_position_half_step(180)
    stepper_motor.motor_stop()
