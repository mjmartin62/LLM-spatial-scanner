"""
project.py
Main entry point for the Raspberry Pi motor control and AI integration project.

Author: Matthew Martin
Date: 2024-Nov-25
"""

import sys
import os
import multiprocessing
import psutil
import time
sys.path.append(os.path.join(os.path.dirname(__file__), "hardware"))
sys.path.append(os.path.join(os.path.dirname(__file__), "ai"))
import run_hardware
from agent_openai import OpenAIAgent
from simulation import Hardware_Sim

TARGET_ANGLE_IC = 0
REAL_TIME_CORE = 3

def main_menu():
    """
    Display the main menu and handle user input.
    """
    print("\nMain Menu:")
    print("Execution mode options:")
    print("1. Run AI with Hardware Simulation")
    print("2. Run AI with Real Hardware")
    mode = int(input("Select an option: ").strip())
    print("\n")
    return mode

def initialize_system(mode):
    """
    Perform system initialization tasks:
     - Configure host environment
     - Configure pseudo Real Time application to dedicated core
    """
    print("Initializing system...")
    
    # Instantiate a parallel child process and data pipe
    parent_conn, child_conn = multiprocessing.Pipe()
    realtime_process = multiprocessing.Process(target=run_system, args=(mode, child_conn,))
    realtime_process.start()
    
    # Assign realtime hardware to dedicate core
    pid = realtime_process.pid
    p = psutil.Process(pid)
    p.cpu_affinity([REAL_TIME_CORE])  

    return parent_conn

def run_system(mode, pipe_conn):
    """
    Motor control and environmental sensing.
    """
    if mode == 1:
        print("Starting hardware simulation...")
        hardware = Hardware_Sim(pipe_conn)
    elif mode == 2:
        print("Starting motor control...")
        run_hardware.just_a_test(pipe_conn)
    else:
        print("Enter valid execution mode")


def main():
    # Initialize and configure user based execution
    print("Welcome to the Motor Control and AI LLM Integration Project!")
    mode = main_menu()
    pipe_conn = initialize_system(mode)
    
    # Create AI agent and prompt
    openAIAgent = OpenAIAgent()

    # Temp code for debug
    angle_list = [-89, -45, 0, 45, 89 ]
    i = 0

    while True:
        time.sleep(1)
        
        # Retrieve proximity distance from hardware; configure pipe as LIFO and then flush
        distance = None
        while not pipe_conn.poll():
            time.sleep(0.5)
        while pipe_conn.poll():
            distance = pipe_conn.recv()

        # Update AI with latest distance and send new target angle
        print(f"Latest measured distance is " + str(distance))
        pipe_conn.send(angle_list[i])
        i += 1


if __name__ == "__main__":
    main()