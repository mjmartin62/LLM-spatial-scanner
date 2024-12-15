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
        "-p", "--prompt", type=int, choices=[1, 2], required=True,
        help="Specify the prompt type to use (1 for Overly Descriptive, 2 for more to come)."
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
    
    # Instantiate a parallel child process and data pipe
    parent_conn, child_conn = multiprocessing.Pipe()
    realtime_process = multiprocessing.Process(target=run_system, args=(mode, child_conn,))
    realtime_process.start()
    
    # Assign realtime hardware to dedicate core
    pid = realtime_process.pid
    p = psutil.Process(pid)
    p.cpu_affinity([REAL_TIME_CORE])  

    return parent_conn, realtime_process

def run_system(mode, pipe_conn):
    """
    Motor control and environmental sensing.
    """
    if mode == 1:
        print("Starting hardware simulation...")
        hardware = Hardware_Sim(conn=pipe_conn, angle=TARGET_ANGLE_IC)
    elif mode == 2:
        print("Starting motor control...")
        
    else:
        print("Enter valid execution mode")

def system_shutdown(pipe_conn, realtime_process):
    '''
    Returns hardware to starting position
    Gracefully shuts down applications
    '''
    print("AI agent goal complete.  Exiting program.....")
    pipe_conn.send(TARGET_ANGLE_IC)
    time.sleep(1)
    pipe_conn.close()
    realtime_process.terminate()
    realtime_process.join()
    sys.exit(0)

def main():

    # Parse input arguments for application flow control
    args = parse_arguments()

    # Initialize the system and configure based on CLI arguments
    pipe_conn, realtime_process = initialize_system(args.mode)
    
    # Create AI agent and prompt the agent with initial instructions
    openAIAgent = OpenAIAgent(TARGET_ANGLE_IC)
    openAIAgent.initial_prompt = get_prompt(str(args.prompt))  
    openAIAgent.connect_agent()
    openAIAgent.initialize_agent() 
    while openAIAgent.comprehension is None:
        time.sleep(0.1)
    if openAIAgent.comprehension == "nok":
        print("Agent responded with 'nok'. Exiting program.")
        pipe_conn.close()
        sys.exit(0)
    if openAIAgent.comprehension == "ok":
        print("Agent responded with 'ok'. Hardware interaction starting.")
    else:
        print("Agent is not following instructions. Exiting program.")
        pipe_conn.close()
        sys.exit(0)

    # Loop to iteratively interact with the AI agent
    while True:
        time.sleep(1)
        
        # Retrieve proximity distance from hardware; configure pipe as LIFO and then flush
        distance = None
        while not pipe_conn.poll():
            time.sleep(0.5)
        while pipe_conn.poll():
            distance = pipe_conn.recv()

        # Update AI agent with latest distance and send new target angle
        print(f"Latest measured distance is " + str(distance))
        openAIAgent.distance = distance
        openAIAgent.update_angle()

        # Wait for AI agent response
        while openAIAgent.query_state == False:
            time.sleep(0.1)
        openAIAgent.query_state = False

        # Shut down interaction with AI agent
        if openAIAgent.complete_state == True:
            openAIAgent.get_agent_logic()
            break

        # Update hardware target angle
        pipe_conn.send(openAIAgent.angle)
    
    # Shut down application
    system_shutdown(pipe_conn, realtime_process)

if __name__ == "__main__":
    main()