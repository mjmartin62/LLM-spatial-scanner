"""
Base class to serve derived agents 
"""
class AIBase:
    """
    Initialize the LLM with configurable prompts.
    TO do:
     - verify ai responds with an "ok" if it understands (use regex library)
     - then send the initial condition of the distance and the angle
    '''
    """
    
    def initialize(self, **kwargs):
        raise NotImplementedError

    def prompt_initial(self, input_text):
        raise NotImplementedError
    
    def prompt_angle(self, input_distance):
        raise NotImplementedError


