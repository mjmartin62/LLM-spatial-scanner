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
import json
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), "hardware"))
sys.path.append(os.path.join(os.path.dirname(__file__), "ai"))
from agent_openai import OpenAIAgent
from simulation import Hardware_Sim
from run_hardware import Hardware_Control

TARGET_ANGLE_IC = 0
REAL_TIME_CORE = 3

def parse_arguments():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Motor Control and AI Integration Project."
    )
    parser.add_argument(
        "-m", "--mode", type=int, choices=[1, 2], required=True,
        help="Execution mode: 1 for hardware simulation, 2 for real hardware."
    )
    parser.add_argument(
        "-p", "--prompt", type=int, choices=[1, 2, 3], required=True,
        help="Specify the prompt type to use (1 for Overly Descriptive, 2 for more to come)."
    )
    parser.add_argument(
        "-a", "--agent", type=str, required=True,
        help="Specify the ai agent type to use (openAI or openAI model 4o)."
    )
    return parser.parse_args()

def get_prompt(prompt):
    """
    Load prompt type.
    """
    # Load available prompts from the JSON file
    try:
        with open("ai/prompts.json", "r") as file:
            prompts = json.load(file)
    except FileNotFoundError:
        print("Error: prompts.json file not found. Please create the file with prompt data.")
        return None

    # Validate the user's input
    if prompt in prompts:
        print(f"\nSelected Prompt:\n{prompts[prompt]}\n")
        return prompts[prompt]
    else:
        print("Invalid prompt. Please update promp library.")
        return None

def initialize_system(mode):
    """
    Perform system initialization tasks:
     - Configure host environment
     - Configure pseudo Real Time application to dedicated core
    """
    print("Initializing system...")
    
    # Instantiate a parallel child subprocess and data pipe
    parent_conn, child_conn = multiprocessing.Pipe()
    ipc_status_flag = multiprocessing.Value('i', 0)
    realtime_process = multiprocessing.Process(target=run_system, args=(mode, child_conn, ipc_status_flag))
    realtime_process.start()
        
    # Error handling for the run_system subprocess
    # Kill process if errors occur during startup
    # Continue process if no errors occur and pin subprocess to dedicated core
    if realtime_process.exitcode is None:
        print("System initialized successfully.")
        pid = realtime_process.pid
        p = psutil.Process(pid)
        p.cpu_affinity([REAL_TIME_CORE])  
        hardware_status = 0
    elif realtime_process.exitcode == 1:
        print("System initialization failed: Hardware initialization error.")
        hardware_status = -1
    elif realtime_process.exitcode == 2:
        print("System initialization failed: Invalid mode.")
        hardware_status = -2
    elif realtime_process.exitcode == 3:
        print("System initialization failed: Unexpected error.")
        hardware_status = -3
    else:
        print("System initialization failed: Unknown error.")
        hardware_status = -4


    # Assign realtime hardware to dedicate core
    pid = realtime_process.pid
    p = psutil.Process(pid)
    p.cpu_affinity([REAL_TIME_CORE])  

    return parent_conn, realtime_process, hardware_status, ipc_status_flag

def run_system(mode, pipe_conn, ipc_status_flag):
    """
    Motor control and environmental sensing subprocess.
    Process is killed if the hardware initialization fails.
    """
    try:
        if mode == 1:
            print("Starting hardware simulation...")
            hardware = Hardware_Sim(conn = pipe_conn, ipc_status_flag = ipc_status_flag, initial_angle = TARGET_ANGLE_IC)
        elif mode == 2:
            hardware = Hardware_Control(conn = pipe_conn, ipc_status_flag = ipc_status_flag, initial_angle = TARGET_ANGLE_IC, motor_speed = 90, gpio_pins = [17, 27, 23, 24])
            print("Starting proximity sensing and motor control...")
        else:
            raise ValueError("Invalid mode")
    
        print("Hardware initialization successful. Subprocess is now running.")
    
    except RuntimeError as e:
        print(f"Hardware initialization error: {e}")
        os._exit(1)
    except ValueError as e:
        print(f"Invalid mode: {e}")
        os._exit(2)
    except Exception as e:
        print(f"Unexpected error: {e}")
        os._exit(3)
    
def system_shutdown(pipe_conn, realtime_process, ipc_status_flag):
    '''
    Returns hardware to starting position
    Gracefully shuts down applications
    '''
    print("AI agent goal complete.  Exiting program.....")
    #pipe_conn.send(TARGET_ANGLE_IC)
    time.sleep(1)
    
    while (ipc_status_flag.value != 2):
        time.sleep(0.1)
    pipe_conn.close()
    realtime_process.terminate()
    realtime_process.join()
    sys.exit(0)

def initialize_agent(pipe_conn, args):
    """
    Inititialize AI agent and start communication.
    """
    # Instantiate AI agent with desired model
    if args.agent == "openAI":
        print("Initializing openAI agent...")
        aiAgent = OpenAIAgent(TARGET_ANGLE_IC)      
    else:
        print("Enter valid ai agent model")

    # Start communication with ai agent
    aiAgent.initial_prompt = get_prompt(str(args.prompt))  
    aiAgent.connect_agent()
    aiAgent.initialize_agent() 
    while aiAgent.comprehension is None:
        time.sleep(0.1)
    if aiAgent.comprehension == "nok":
        print("Agent responded with 'nok'. Exiting program.")
        pipe_conn.close()
        sys.exit(0)
    if aiAgent.comprehension == "ok":
        print("Agent responded with 'ok'. Hardware interaction starting.")
    else:
        print("Agent is not following instructions. Exiting program.")
        aiAgent.close()
        sys.exit(0)

    return aiAgent

def main():
    
    # Parse input arguments for application flow control
    args = parse_arguments()

    # Initialize the system and configure based on CLI arguments
    pipe_conn, realtime_process, hardware_status, ipc_status_flag = initialize_system(args.mode)
    
    # Create AI agent and prompt the agent with initial instructions
    aiAgent = initialize_agent(pipe_conn, args)

    # Loop to iteratively interact with the AI agent
    while True:
        time.sleep(1)
        
        # Retrieve proximity distance from hardware; configure pipe as LIFO and then flush
        distance = None
        while not pipe_conn.poll():
            time.sleep(0.1)
        while pipe_conn.poll():
            distance = pipe_conn.recv()

        # Update AI agent with latest distance and send new target angle
        print(f"Latest measured distance is " + str(distance))
        aiAgent.distance = distance
        aiAgent.update_angle()

        # Wait for AI agent response
        while aiAgent.query_state == False:
            time.sleep(0.1)
        aiAgent.query_state = False

        # Shut down interaction with AI agent
        if aiAgent.complete_state == True:
            aiAgent.get_agent_logic()
            pipe_conn.send(aiAgent.angle)
            ipc_status_flag.value = 1
            break

        # Update hardware target angle
        pipe_conn.send(aiAgent.angle)
    
    # Shut down application
    system_shutdown(pipe_conn, realtime_process, ipc_status_flag)

if __name__ == "__main__":
    main()