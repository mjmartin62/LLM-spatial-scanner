"""
Hardware simulation class
Simulates both the physical environment and peripherals
"""

import time
import math

class Hardware_Sim:
    def __init__(self, pipe_conn, geom_type="line", angle=0):
        self._geometry = geom_type
        self._angle = float(angle)
        self._distance = float(0)
        self.pipe_conn = pipe_conn
        self.sim_line()

    # Getter for angle
    @property
    def angle(self):
        return self._angle

    # Setter for angle
    @angle.setter
    def angle(self, new_angle):
        if not isinstance(new_angle, (int, float)):
            raise ValueError("Angle must be a number")
        if new_angle < -90 or new_angle > 90:
            raise ValueError("Angle must be between -90 and +90 degrees")
        self._angle = new_angle

    # Getter for distance
    @property
    def distance(self):
        return self._distance

    # Setter for distance
    @distance.setter
    def distance(self, new_distance):
        if not isinstance(new_distance, (int, float)):
            raise ValueError("Distance must be a number")
        if new_distance < 0:
            raise ValueError("Distance must be greater than 0")
        self._distance = new_distance

    # Geometric Simulation:  Line
    def sim_line(self):
        
        while True:
            time.sleep(0.1)

            # Fill data pipe with current system state
            self.pipe_conn.send(self.distance)
            # Retrieve angle from AI; configure pipe as LIFO and then flush
            self.angle = 0
            while not self.pipe_conn.poll():
                time.sleep(0.1)
            while self.pipe_conn.poll():
                self.angle = float(self.pipe_conn.recv())
                self.distance = 10 / math.cos(self.angle * math.pi / 180)



        