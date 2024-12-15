# LLM-spatial-scanner; Raspberry Pi Motor Control and AI Integration Project
Discover how an LLM interacts with a planar spatial environment

## Features
- Real-time motor control using Raspberry Pi GPIO.
- AI decision-making for obstacle avoidance and angle optimization.
- Modular Python codebase with support for extensibility.

## Hardware Requirements
 - Raspberry Pi 4B (or compatible model running a Linux embedded system)
 - ST vl53l1x Time of Flight Sensor
 - Any bipolar hybrid steppor motor with compatible dual H-bridge hardware

## Software Requirements
 - Python 3.11 or greater

## Firmware Requirements
 - Update Linux OS kernel boot parameters under /boot/cmdline.txt with flag isolcpus=<cpu core>

## Installation
 - Ensure you have `gcc`, `make`, and other necessary tools installed.
 - Navigate to 'libraries/VL53L1X/STSW-IMG013/user_lib' and build the STSW-IMG013 driver using make
 - Navigate to 'libraries/Stepper_Motor_Hybrid and build the stepper motor driver using make
 - If using openAI API, create an environment variable called:  OPENAI_API_KEY

## Code and Directory Structure
LLM-spatial-scanner/
├── project.py
├── ai
│   ├── agent_base.py
│   ├── agent_openai.py
│   ├── prompts.json
├── hardware
│   ├── run_hardware.py
│   ├── simulation.py
│   ├── VL53L1_wrapper.py
├── libraries
│   ├── VL53L1X
│   │   ├── STSW-IMG013
│   │   │   ├── user_lib
│   │   │   │   ├── Makefile
│   ├── Stepper_Motor_Hybrid
│   │   ├── include
│   │   │   ├── motor_control_api.h
│   │   │   ├── motor_gpio.h
│   │   │   ├── motor_timing.h
│   │   ├── src
│   │   │   ├── motor_control_api.c
│   │   │   ├── motor_gpio.c
│   │   │   ├── motor_timing.c
│   │   ├── main.c
│   │   ├── Makefile

    
## Usage
