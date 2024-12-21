'''
Hardware control class
Runs on a dedicated core for realtime control and extensibility
'''
import time
from VL53L1_wrapper import ToF_Sensor
from stepper_motor_control_wrapper import Stepper_Motor

class Hardware_Control():
    def __init__(self, conn, init_event, error_event, shutdown_event, 
                 ipc_status_flag, i2c_bus = 1, i2c_addr = 0x29, 
                 gpio_pins = [0, 0, 0, 0], initial_angle = 0, motor_speed = 0):
        self.pipe_conn = conn
        self._polling_period = 0.1
        self._sensor_all_data = None
        self._new_angle = float()
        self._last_angle = float(initial_angle)
        self._rotate = float()
        self._rotate_precision = 0.9
        self._distance = round(float(), 1)
        self._i2c_bus = i2c_bus
        self._i2c_addr = i2c_addr
        self._gpio_pins = gpio_pins
        self._motor_speed = motor_speed
        self._stepper_motor = None 
        self._tof = None
        self._ipc_status_flag = ipc_status_flag
        self._init_event = init_event
        self._error_event = error_event
        self._shutdown_event = shutdown_event


        # Initialize and execute hardware control
        # Raise error to control process exit in calling function
        status = self._initialization()
        if status == 0:
            self._init_event.set()
            self._hardware_transition()
        else:
            self._error_event.set()
            self._init_event.set()
            raise RuntimeError("Hardware initialization failed")


    def _initialization(self):
        '''
        Initializes the proximity sensor and stepper motor objects along with startup procedures.
        '''
        try:
            # Initialize and conifugre the proximity sensor
            self._tof = ToF_Sensor(i2c_bus = self._i2c_bus, i2c_addr = self._i2c_addr)
            self._tof.set_roi(4, 4)
            self._tof.initialize_ranging()

            # Initialize the stepper motor
            self._stepper_motor = Stepper_Motor(gpio_pins = self._gpio_pins, speed = self._motor_speed)

            return 0
        
        except (RuntimeError, OSError) as e:
            print(f"Hardware peripheral initialization failed: {e}")
            return -1

        except Exception as e:
            print(f"An unexpected error occurred during hardware initialization: {e}")
            return -1


    def _hardware_transition(self, test_mode = "off"):
        '''
        State machine to control motor position and updating measured distance
        '''
        while True:
            
            # Poll sensor and send distance data to caller python application
            try:
                self._sensor_all_data = self._tof.poll_sensor()
                self._distance = float(self._sensor_all_data["Distance"])
                self.pipe_conn.send(self._distance)
            
            except (RuntimeError, OSError) as e:
                print(f"ToF Sensor communication failed during hardware transition: {e}")

            except Exception as e:
                print(f"An unexpected error occurred during hardware transition: {e}")

            # Retrieve target angle from caller python application; configure pipe as LIFO and then flush
            try:
                while not self.pipe_conn.poll():
                    time.sleep(self._polling_period)
                while self.pipe_conn.poll():
                    self._new_angle = float(self.pipe_conn.recv())

            except (RuntimeError, OSError) as e:
                print(f"Target angle communication failed during hardware transition: {e}")

            except Exception as e:
                print(f"An unexpected error occurred during hardware transition: {e}")

            # Set motor position.  Note that commanded position is updated according to the motor precision.
            try:
                self._rotate = round((self._new_angle - self._last_angle) / self._rotate_precision, 0) * self._rotate_precision
                self._last_angle = self._last_angle + self._rotate
                self._stepper_motor.motor_set_position_half_step(self._rotate)

            except (RuntimeError, OSError) as e:
                print(f"Stepper motor command failed during hardware transition: {e}")

            except Exception as e:
                print(f"An unexpected error occurred during hardware transition: {e}")

            # Check IPC status flag
            if self._ipc_status_flag.value == 1:
                self._shutdown()

            if test_mode == "on":
                break

    def _shutdown(self):
        '''
        Shut down motor and flag parent process it is safe to kill this subprocess
        '''
        print("Shutting down all hardware...")
        self._stepper_motor.motor_stop()
        self._shutdown_event.set()

if __name__ == "__main__":
    pass