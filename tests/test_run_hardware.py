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
         patch.object(Hardware_Control, "_hardware_transition") as mock_transition, \
         patch("multiprocessing.Event") as mock_event, \
         patch("multiprocessing.Value") as mock_value:
        yield mock_tof_sensor, mock_stepper_motor, mock_transition, mock_event, mock_value

def test_initialization(initialization_mocks):
    '''
    Test initialization of Hardware_Control class.
    Ensures hardware wrappers are instantiated and pipe connection is stored.
    '''
    # Arrange: Mock Pipe connection and hardware wrappers
    mock_pipe_conn = MagicMock()
    mock_tof_sensor, mock_stepper_motor, mock_transition, mock_event, mock_value = initialization_mocks
    mock_init_event = mock_event.return_value
    mock_error_event = mock_event.return_value
    mock_shutdown_event = mock_event.return_value
    mock_ipc_status_flag = mock_value.return_value
    
    # Act: Create instance of Hardware_Control
    hardware = Hardware_Control(
        conn = mock_pipe_conn, 
        init_event = mock_init_event,
        error_event = mock_error_event, 
        shutdown_event = mock_shutdown_event,
        ipc_status_flag = mock_ipc_status_flag,
        initial_angle = 30, 
        gpio_pins=[17, 27, 23, 24], 
        motor_speed = 360
    )
    
    # Assert: Hardware wrappers are initialized correctly and class members are assigned during instantiation
    mock_tof_sensor.assert_called_once_with(i2c_bus = hardware._i2c_bus, i2c_addr = hardware._i2c_addr)
    mock_stepper_motor.assert_called_once_with(gpio_pins = hardware._gpio_pins, speed = hardware._motor_speed)
    assert hardware.pipe_conn == mock_pipe_conn
    assert hardware._last_angle == 30
    assert hardware._motor_speed == 360
    assert hardware._gpio_pins == [17, 27, 23, 24]

def test_initialization_failure(initialization_mocks):
    '''
    Tests initialization failure
    '''
    # Arrange: Mock Pipe connection and hardware wrappers
    mock_pipe_conn = MagicMock()
    mock_tof_sensor, mock_stepper_motor, mock_transition, mock_event, mock_value = initialization_mocks
    mock_tof_sensor.side_effect = RuntimeError("Mocked sensor failure")

    # Act and assert: Create instance of Hardware_Control
    with pytest.raises(RuntimeError, match="Hardware initialization failed"):
        Hardware_Control(
            conn = mock_pipe_conn,
            init_event = MagicMock(),
            error_event = MagicMock(),
            shutdown_event = MagicMock(),
            ipc_status_flag = MagicMock(),
            initial_angle = 30,
            gpio_pins = [17, 27, 23, 24],
            motor_speed = 360,
        )
