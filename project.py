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
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), "hardware"))
sys.path.append(os.path.join(os.path.dirname(__file__), "ai"))
from agent_openai import OpenAIAgent
from simulation import Hardware_Sim
from run_hardware import Hardware_Control

# System constants
TARGET_ANGLE_IC = 0
REAL_TIME_CORE = 3

# Exit Codes
EXIT_CODES = {
    "SUCCESS": 0,
    "HARDWARE_ERROR": 1,
    "INVALID_TYPE": 2,
    "UNEXPECTED_ERROR": 3,
    "EMERGENCY_SHUTDOWN": 4,
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Default level for logging
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("project.log", mode="a"),  # Log to file
    ]
)

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
        "-p", "--prompt", type=int, choices=[1, 2, 3, 4, 5, 6], required=True,
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
        logging.error("Error: prompts.json file not found. Please create the file with prompt data.")
        return None

    # Validate the user's input
    if prompt in prompts:
        logging.info(f"\nSelected Prompt:\n{prompts[prompt]}\n")
        return prompts[prompt]
    else:
        logging.error("Invalid prompt. Please update promp library.")
        return None

def initialize_system(mode):
    """
    Perform system initialization tasks:
     - Configure host environment
     - Configure pseudo Real Time application to dedicated core
    """
    logging.info("Initializing system...")
    
    # Instantiate a parallel child subprocess and data pipe
    parent_conn, child_conn = multiprocessing.Pipe()
    ipc_status_flag = multiprocessing.Value('i', 0)
    init_event = multiprocessing.Event()
    error_event = multiprocessing.Event()
    shutdown_event = multiprocessing.Event()
    realtime_process = multiprocessing.Process(
        target=run_system, 
        args=(mode, child_conn, ipc_status_flag, init_event, error_event, shutdown_event)
    )
    realtime_process.start()
    
    # realtime_process blocks until its initialization completes
    init_event.wait()
        
    # Error handling for the run_system subprocess
    # Continue process if no errors occur and pin subprocess to dedicated core
    if not error_event.is_set():
        logging.info("System initialized successfully.")
        pid = realtime_process.pid
        p = psutil.Process(pid)
        p.cpu_affinity([REAL_TIME_CORE])  
        hardware_status = 0

    # Send error return value if initialization fails
    else:

        if realtime_process.exitcode == 1:
            logging.error("System initialization failed: Hardware initialization error.")
            hardware_status = -1
        elif realtime_process.exitcode == 2:
            logging.error("System initialization failed: Invalid mode.")
            hardware_status = -2
        elif realtime_process.exitcode == 3:
            logging.error("System initialization failed: Unexpected error.")
            hardware_status = -3
        else:
            logging.error("System initialization failed: Unknown error.")
            hardware_status = -4

    return parent_conn, realtime_process, hardware_status, ipc_status_flag, shutdown_event

def run_system(mode, pipe_conn, ipc_status_flag, init_event, error_event, shutdown_event):
    """
    Motor control and environmental sensing subprocess.
    Process is killed if the hardware initialization fails.
    """
    try:
        if mode == 1:
            logging.info("Starting hardware simulation...")
            hardware = Hardware_Sim(
                conn = pipe_conn, 
                init_event = init_event,
                error_event = error_event,
                shutdown_event = shutdown_event,
                ipc_status_flag = ipc_status_flag, 
                initial_angle = TARGET_ANGLE_IC)
        elif mode == 2:
            logging.info("Starting proximity sensing and motor control...")
            hardware = Hardware_Control(
                conn = pipe_conn, 
                init_event = init_event,
                error_event = error_event,
                shutdown_event = shutdown_event,
                ipc_status_flag = ipc_status_flag, 
                initial_angle = TARGET_ANGLE_IC, 
                motor_speed = 90, 
                gpio_pins = [17, 27, 23, 24]
            )
        else:
            raise ValueError("Invalid mode")
    
    except (RuntimeError, OSError) as e:
        logging.error(f"Hardware initialization error: {e}")
        sys.exit(EXIT_CODES["HARDWARE_ERROR"])
    except ValueError as e:
        logging.error(f"Invalid mode: {e}")
        sys.exit(EXIT_CODES["INVALID_TYPE"])
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(EXIT_CODES["UNEXPECTED_ERROR"])
    
def graceful_system_shutdown(pipe_conn, realtime_process, shutdown_event):
    '''
    Returns hardware to starting position
    Gracefully shuts down applications
    '''
    logging.info("AI agent goal complete.  Exiting program.....")

    # realtime_process blocks until its shutdown completes
    shutdown_event.wait()
    pipe_conn.close()
    realtime_process.terminate()
    realtime_process.join()
    sys.exit(EXIT_CODES["SUCCESS"])

def unexpected_shutdown(error, pipe_conn, realtime_process,):
    '''
    Handles premature shutdowns other than an ai agent completing its goal
    '''
    logging.error("Unexpected shutdown invoked. Exiting program.....")
    pipe_conn.close()
    realtime_process.terminate()
    realtime_process.join()
    sys.exit(error)

def initialize_agent(pipe_conn, args):
    """
    Inititialize AI agent and start communication.
    """
    status = 0
    aiAgent = None
    # Instantiate AI agent with desired model
    if args.agent == "openAI":
        logging.info("Initializing openAI agent...")
        aiAgent = OpenAIAgent(TARGET_ANGLE_IC)      
    else:
        logging.error("Invalid ai agent model")
        status = EXIT_CODES["INVALID_TYPE"]

    if status == 0:
        # Start communication with ai agent
        aiAgent.initial_prompt = get_prompt(str(args.prompt))  
        aiAgent.connect_agent()
        aiAgent.initialize_agent() 

        # Handle agent's initial response
        if aiAgent.comprehension == "nok":
            logging.info("Agent responded with 'nok'. Exiting program.")
            status = EXIT_CODES["UNEXPECTED_ERROR"]
        elif aiAgent.comprehension == "ok":
            logging.info("Agent responded with 'ok'. Hardware interaction starting.")
        else:
            logging.info("Agent is not following instructions. Exiting program.")
            status = EXIT_CODES["UNEXPECTED_ERROR"]

    return aiAgent, status

def main():
    
    # Parse input arguments for application flow control
    args = parse_arguments()

    # Initialize the system and configure based on CLI arguments
    pipe_conn, realtime_process, hardware_status, ipc_status_flag, shutdown_event = initialize_system(args.mode)
    if hardware_status != 0:
        unexpected_shutdown(EXIT_CODES["HARDWARE_ERROR"], pipe_conn, realtime_process)
    
    # Create AI agent and prompt the agent with initial instructions
    aiAgent, agent_status = initialize_agent(pipe_conn, args)
    if agent_status != 0:
        unexpected_shutdown(agent_status, pipe_conn, realtime_process)

    # Loop to iteratively interact with the AI agent
    while True:
        time.sleep(0.1)
        
        # Retrieve proximity distance from hardware; configure pipe as LIFO and then flush
        distance = None
        while not pipe_conn.poll():
            time.sleep(0.1)
        while pipe_conn.poll():
            distance = pipe_conn.recv()

        # Update AI agent with latest distance and send new target angle
        logging.info(f"Latest measured distance is " + str(distance))
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
    graceful_system_shutdown(pipe_conn, realtime_process, shutdown_event)

if __name__ == "__main__":
    main()