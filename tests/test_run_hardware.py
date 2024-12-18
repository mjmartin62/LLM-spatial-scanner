'''
Unit test for realtime hardware control logic
'''
import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../hardware")))

from unittest.mock import MagicMock, patch
from run_hardware import Hardware_Control

@pytest.fixture
def initialization_mocks():
    with patch("run_hardware.ToF_Sensor") as mock_tof_sensor, \
         patch("run_hardware.Stepper_Motor") as mock_stepper_motor, \
         patch.object(Hardware_Control, "_hardware_transition") as mock_transition:
        yield mock_tof_sensor, mock_stepper_motor, mock_transition

def test_initialization(initialization_mocks):
    '''
    Test initialization of Hardware_Control class.
    Ensures hardware wrappers are instantiated and pipe connection is stored.
    '''
    # Arrange: Mock Pipe connection and hardware wrappers
    mock_pipe_conn = MagicMock()
    mock_tof_sensor, mock_stepper_motor, mock_transition = initialization_mocks
    
    # Act: Create instance of Hardware_Control
    hardware = Hardware_Control(conn = mock_pipe_conn, initial_angle = 30, gpio_pins=[17, 27, 23, 24], motor_speed = 360)
    
    # Assert: Hardware wrappers are initialized correctly and class members are assigned during instantiation
    mock_tof_sensor.assert_called_once_with(i2c_bus = hardware._i2c_bus, i2c_addr = hardware._i2c_addr)
    mock_stepper_motor.assert_called_once_with(gpio_pins = hardware._gpio_pins, speed = hardware._motor_speed)
    assert hardware.pipe_conn == mock_pipe_conn
    assert hardware._last_angle == 30
    assert hardware._motor_speed == 360
    assert hardware._gpio_pins == [17, 27, 23, 24]

@pytest.fixture
def hardware_transition_mocks():
    with patch("run_hardware.ToF_Sensor") as mock_tof_sensor, \
         patch("run_hardware.Stepper_Motor") as mock_stepper_motor, \
         patch.object(Hardware_Control, "_hardware_transition") as mock_transition:
        yield mock_tof_sensor, mock_stepper_motor, mock_transition

def test_hardware_transition(hardware_transition_mocks):
    pass



