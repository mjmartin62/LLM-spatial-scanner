'''
Unit test for central application logic
'''
import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../hardware")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import MagicMock, patch
from project import TARGET_ANGLE_IC, EXIT_CODES, REAL_TIME_CORE
from project import run_system, initialize_system, graceful_system_shutdown

@pytest.fixture
def run_system_mocks():
    with patch("project.Hardware_Sim") as mock_hardware_sim:
        yield mock_hardware_sim

def test_run_system(run_system_mocks):
    '''
    Test the subprocess run_system with proper mode 1 execution.
    Ensures simulation is instantiated with proper arguments.
    '''
    # Arrange: Mock connections and imported classes
    mock_hardware_sim = run_system_mocks
    mode = 1
    pipe_conn = MagicMock()
    ipc_status_flag = MagicMock()
    init_event = MagicMock()
    error_event = MagicMock()
    shutdown_event = MagicMock()

    # Act: Call function under test
    run_system(mode, pipe_conn, ipc_status_flag, init_event, error_event, shutdown_event)
    
    # Assert: Single correct instantiation is called
    mock_hardware_sim.assert_called_once_with(
        conn=pipe_conn,
        init_event=init_event,
        error_event=error_event,
        shutdown_event=shutdown_event,
        ipc_status_flag=ipc_status_flag,
        initial_angle=TARGET_ANGLE_IC
    )

def test_run_system_invalid_mode(run_system_mocks):
    '''
    Test the subprocess run_system with proper mode 1 execution.
    Ensures simulation is instantiated with proper arguments.
    '''
    # Arrange: Mock connections and imported classes
    mode = 55
    pipe_conn = MagicMock()
    ipc_status_flag = MagicMock()
    init_event = MagicMock()
    error_event = MagicMock()
    shutdown_event = MagicMock()

    # Act and assert: call function with invalid mode
    with pytest.raises(SystemExit) as excinfo:
        run_system(mode, pipe_conn, ipc_status_flag, 
                   init_event, error_event, shutdown_event)
        
    # Assert: Verify the exit code corresponds to the invalid mode
    assert excinfo.value.code == EXIT_CODES["INVALID_TYPE"]

def test_run_system_hardware_error(run_system_mocks):
    '''
    Test the subprocess run_system with a hardware failure.
    '''
    # Arrange: Mock connections and imported classes
    mock_hardware_sim = run_system_mocks
    mode = 1
    pipe_conn = MagicMock()
    ipc_status_flag = MagicMock()
    init_event = MagicMock()
    error_event = MagicMock()
    shutdown_event = MagicMock()

    # Simulate a RuntimeError when Hardware_Sim is instantiated
    mock_hardware_sim.side_effect = RuntimeError("Hardware initialization failed")

    # Act and assert: call function with invalid mode
    with pytest.raises(SystemExit) as excinfo:
        run_system(mode, pipe_conn, ipc_status_flag, 
                   init_event, error_event, shutdown_event)
        
    # Assert: Verify the exit code corresponds to the hardware error
    assert excinfo.value.code == EXIT_CODES["HARDWARE_ERROR"]

@pytest.fixture
def initialize_system_mocks():
    with patch("multiprocessing.Event") as mock_event, \
         patch("multiprocessing.Value") as mock_value, \
         patch("multiprocessing.Pipe") as mock_pipe, \
         patch("multiprocessing.Process") as mock_process, \
         patch("psutil.Process") as mock_psutil_process:
        yield mock_event, mock_value, mock_pipe, mock_process, mock_psutil_process

def test_initialize_system(initialize_system_mocks):
    '''
    Test the successful execution of initialize_system
    '''
    # Arrange: Mock connections and subprocess
    mock_event, mock_value, mock_pipe, mock_process, mock_psutil_process = initialize_system_mocks
    mock_pipe.return_value = (MagicMock(), MagicMock())
    mock_event.return_value = MagicMock()
    mock_value.return_value = MagicMock()
    
    parent_conn, child_conn = mock_pipe.return_value
    ipc_status_flag = mock_value.return_value
    init_event = mock_event.return_value
    init_event.is_set.return_value = True
    error_event = mock_event.return_value
    error_event.is_set.return_value = False
    shutdown_event = mock_event.return_value
    
    realtime_process = mock_process.return_value
    realtime_process.pid = 100
    realtime_process.exitcode = None
    mock_psutil_process.return_value = MagicMock()
    
    mode = 1

    # Act
    parent_conn, process, hardware_status, ipc_status_flag, shutdown_event = initialize_system(mode)

    # Assert
    assert hardware_status == 0
    init_event.wait.assert_called_once()
    error_event.is_set.assert_called_once()

def test_initialize_system_hardware_failure(initialize_system_mocks):
    '''
    Test the hardware failure during initialize_system
    '''
    # Arrange: Mock connections and subprocess
    mock_event, mock_value, mock_pipe, mock_process, mock_psutil_process = initialize_system_mocks
    mock_pipe.return_value = (MagicMock(), MagicMock())
    mock_event.return_value = MagicMock()
    mock_value.return_value = MagicMock()
    
    parent_conn, child_conn = mock_pipe.return_value
    ipc_status_flag = mock_value.return_value
    init_event = mock_event.return_value
    init_event.is_set.return_value = True
    error_event = mock_event.return_value
    error_event.is_set.return_value = True
    shutdown_event = mock_event.return_value
    
    realtime_process = mock_process.return_value
    realtime_process.pid = 100
    realtime_process.exitcode = 1
    mock_psutil_process.return_value = MagicMock()
    
    mode = 1

    # Act
    parent_conn, process, hardware_status, ipc_status_flag, shutdown_event = initialize_system(mode)

    # Assert
    assert hardware_status == -1
    init_event.wait.assert_called_once()
    error_event.is_set.assert_called_once()

def test_graceful_system_shutdown():
    '''
    Test the successful execution of graceful_system_shutdown
    '''
    # Arrange: Mock connections and subprocess
    pipe_conn = MagicMock()
    shutdown_event = MagicMock()
    realtime_process = MagicMock()

    shutdown_event.wait.return_value = None
    pipe_conn.close.return_value = None
    realtime_process.terminate.return_value = None
    realtime_process.join.return_value = None

    # Act and assert
    with pytest.raises(SystemExit) as excinfo:
        graceful_system_shutdown(pipe_conn, realtime_process, shutdown_event)
    assert excinfo.value.code == EXIT_CODES["SUCCESS"]