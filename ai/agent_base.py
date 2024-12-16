"""
Base class to serve derived agents 
"""
from abc import ABC, abstractmethod

class AIBase:
    """
    Initialize the LLM with configurable prompts and hardware states
    """
    def __init__(self, angle=0):
        self._angle = float(angle)
        self._distance = float(0)
        self._angle_history = []
        self._distance_history = []
        self._comprehension = None
        self._initial_prompt = None
        self._complete_state = False
        self._query_state = False
        self._ai_logic = None

    
    @abstractmethod
    def initialize_agent(self):
        '''
        Initializes agent with ai model specific requirements
        '''
        pass

    @abstractmethod
    def update_angle(self):
        '''
        Querry agent to update the target angle
        '''
        pass

    @abstractmethod
    def get_agent_logic(self):
        '''
        Querry agent to ask its logic for achieving its goal
        '''
        pass

    # Getter for angle
    @property
    def angle(self):
        return self._angle

    # Setter for angle
    @angle.setter
    def angle(self, new_angle):
        if not isinstance(new_angle, (int, float)):
            raise ValueError("Angle must be a number")
        elif new_angle < -90 or new_angle > 90:
            raise ValueError("Angle must be between -90 and +90 degrees")
        else:
            self._angle = new_angle
            self._angle_history.append(new_angle)

    # Getter for distance
    @property
    def distance(self):
        return self._distance

    # Setter for distance
    @distance.setter
    def distance(self, new_distance):
        if not isinstance(new_distance, (int, float)):
            raise ValueError("Distance must be a number")
        elif new_distance < 0:
            raise ValueError("Distance must be greater than 0")
        else:
            self._distance = new_distance
            self._distance_history.append(new_distance)

    # Getter for ai agent comprehension state
    @property
    def comprehension(self):
        return self._comprehension

    # Setter for ai agent comprehension state
    @comprehension.setter
    def comprehension(self, new_comprehension):
        if (new_comprehension.lower() == "nok"):
            self._comprehension = "nok"
            raise ValueError("AI agent does not understand")
        elif (new_comprehension.lower().strip() == "ok"):
            self._comprehension = "ok"
        else:
            self._comprehension = None

    # Getter for ai agent initial prompt
    @property
    def initial_prompt(self):
        return self._initial_prompt
    
    # Setter for ai agent initial prompt
    @initial_prompt.setter
    def initial_prompt(self, prompt):
        self._initial_prompt = prompt

    # Getter for query state
    @property
    def query_state(self):
        return self._query_state

    # Setter for query state
    @query_state.setter
    def query_state(self, state):
        self._query_state = state

    # Getter for completion state
    @property
    def complete_state(self):
        return self._complete_state

    # Setter for completion state
    @complete_state.setter
    def complete_state(self, state):
        self._complete_state = state

    # Getter for ai logic
    @property
    def ai_logic(self):
        return self._ai_logic

    # Setter for ai logic
    @ai_logic.setter
    def ai_logic(self, logic):
        self._ai_logic = logic