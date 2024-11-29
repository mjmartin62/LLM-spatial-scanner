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
sys.path.append(os.path.join(os.path.dirname(__file__), "hardware"))
sys.path.append(os.path.join(os.path.dirname(__file__), "ai"))
from agent_openai import OpenAIAgent
from simulation import Hardware_Sim

TARGET_ANGLE_IC = -45
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

def get_prompt():
    """
    Display prompt type options to the user.
    """
    # Load available prompts from the JSON file
    try:
        with open("ai/prompts.json", "r") as file:
            prompts = json.load(file)
    except FileNotFoundError:
        print("Error: prompts.json file not found. Please create the file with prompt data.")
        return None
    
    # Allow user to select the type of prompt to use
    print("\nPrompt type available:")
    print("1. Overly descriptive")
    print("2. More to come")
    choice = input("Enter the number of the prompt type you'd like to use: ").strip()

    # Validate the user's input
    if choice in prompts:
        print(f"\nSelected Prompt:\n{prompts[choice]}\n")
        return prompts[choice]
    else:
        print("Invalid selection. Please enter a valid number from the list.")
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

    return parent_conn

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


def main():

    # Initialize and configure user based execution
    print("Welcome to the Motor Control and AI LLM Integration Project!")
    mode = main_menu()
    pipe_conn = initialize_system(mode)
    
    # Create AI agent and prompt the agent with initial instructions
    openAIAgent = OpenAIAgent(TARGET_ANGLE_IC)
    openAIAgent.initial_prompt = get_prompt()  
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
    print("AI agent goal complete.  Exiting program.....")
    pipe_conn.close()
    sys.exit(0)

if __name__ == "__main__":
    main()