"""
Python wrapper for linux system driver for the ST VL53L1 Time of Flight (TOF) sensor

"""

import ctypes
import time
import os

class ToF_Sensor:
    def __init__(self, library_path=None, i2c_bus = 1, i2c_addr = 0x29):
        if library_path is None:
            library_path = os.path.join(
            os.path.dirname(__file__), "../libraries/VL53L1X/STSW-IMG013/user_lib/libvl53l1x.so")
        
        self._lib = ctypes.CDLL(library_path)
        self._i2c_bus = ctypes.c_int(i2c_bus)
        self._i2c_addr = ctypes.c_uint8(i2c_addr)
        self._dataReady = ctypes.c_uint8(0)
        self._dev = ctypes.c_uint16()
        self._status = int()

        # Software version storage information
        class _vl53l1x_version_t(ctypes.Structure):
            _fields_ = [
                ("Major", ctypes.c_uint8),
                ("Minor", ctypes.c_uint8),
                ("Build", ctypes.c_uint8),
                ("Revision", ctypes.c_uint32)
            ]

        # Sensor values storage 
        class _vl53l1x_result_t(ctypes.Structure):
            _fields_ = [
                ("Status", ctypes.c_uint8),
                ("Distance", ctypes.c_uint16),
                ("Ambient", ctypes.c_uint16),
                ("SigPerSPAD", ctypes.c_uint16),
                ("NumSPADs", ctypes.c_uint16),
            ]

        self._vl53l1x_version_t = _vl53l1x_version_t()
        self._vl53l1x_result_t = _vl53l1x_result_t()

        # Initialize the sensor and start communication upon instantiation
        self._bind_functions()
        self._initialize_i2c()
        self._initialize_sensor()
        self._initialize_ranging()

    def _bind_functions(self):
        '''
        Bind callable c-library functions with python functions
        '''
        # Get SW version
        self._lib.VL53L1X_GetSWVersion.argtypes = [ctypes.POINTER(type(self._vl53l1x_version_t))]
        self._lib.VL53L1X_GetSWVersion.restype = ctypes.c_int8

        # Initialize I2C coms
        self._lib.VL53L1X_UltraLite_Linux_I2C_Init.argtypes = [ctypes.c_uint16, ctypes.c_int, ctypes.c_uint8]
        self._lib.VL53L1X_UltraLite_Linux_I2C_Init.restype = ctypes.c_int8

        # Initialize sensor
        self._lib.VL53L1X_SensorInit.argtypes = [ctypes.c_uint16]
        self._lib.VL53L1X_SensorInit.restype = ctypes.c_int8

        # Start the sensor ranging function
        self._lib.VL53L1X_StartRanging.argtypes = [ctypes.c_uint16]
        self._lib.VL53L1X_StartRanging.restype = ctypes.c_int8

        # Check register if new data is ready
        self._lib.VL53L1X_CheckForDataReady.argtypes = [ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint8)]
        self._lib.VL53L1X_CheckForDataReady.restype = ctypes.c_int8

        # Get new data
        self._lib.VL53L1X_GetResult.argtypes = [ctypes.c_uint16, ctypes.POINTER(type(self._vl53l1x_result_t))]
        self._lib.VL53L1X_GetResult.restype = ctypes.c_int8

        # Trigger the sensor interrupt to prepare for additional measurements
        self._lib.VL53L1X_ClearInterrupt.argtypes = [ctypes.c_uint16]
        self._lib.VL53L1X_ClearInterrupt.restype = ctypes.c_int8

    def get_software_version(self):
        '''
        Retrieves driver software version
        '''
        self._status = self._lib.VL53L1X_GetSWVersion(ctypes.byref(self._vl53l1x_version_t))
        if self._status == 0:
            version  = str(self._vl53l1x_version_t.Major) + "." + str(self._vl53l1x_version_t.Minor) + "." + str( self._vl53l1x_version_t.Build)
            return version
        else:
            raise RuntimeError(f"Could not retrive software version with status: {self._status}")
        
    def _initialize_i2c(self):
        '''
        Initializes bus and address for the VL531 sensor
        '''
        self._status = self._lib.VL53L1X_UltraLite_Linux_I2C_Init(self._dev, self._i2c_bus,self._i2c_addr)
        if self._status == 0:
            print("I2C Coms Initialized....")
        else:
            raise RuntimeError(f"I2C Coms initialization failed with status: {self._status}")

    def _initialize_sensor(self):
        '''
        Initializes the sensor with default operational parameters
        '''
        self._status = self._lib.VL53L1X_SensorInit(self._dev)
        if self._status == 0:
            print("Sensor Initialized....")
        else:
            raise RuntimeError(f"Sensor initialization failed with status: {self._status}")
        
    def _initialize_ranging(self):
        '''
        Starts the distance measurement function
        '''
        self._status = self._lib.VL53L1X_StartRanging(self._dev)
        if self._status == 0:
            print("Ranging Initialized....")
        else:
            raise RuntimeError(f"Ranging initialization failed with status: {self._status}")
        
    def check_for_data(self):
        '''
        Checks device register if new data is ready to be retrieved
        '''
        self._dataReady = ctypes.c_uint8(0)
        while(self._dataReady == ctypes.c_uint8(0)):
            self._status = self._lib.VL53L1X_CheckForDataReady(self._dev, ctypes.byref(self._dataReady))
            time.sleep(0.1)
        return self._status

    def get_new_data(self):
        '''
        Extracts distance releated data from the sensor
        '''
        self._status = self._lib.VL53L1X_GetResult(self._dev, ctypes.byref(self._vl53l1x_result_t))
        if self._status == 0:
            return {
            "Distance": self._vl53l1x_result_t.Distance,
            "Ambient": self._vl53l1x_result_t.Ambient,
            "SigPerSPAD": self._vl53l1x_result_t.SigPerSPAD,
            "NumSPADs": self._vl53l1x_result_t.NumSPADs,
        }
        else:
            raise RuntimeError(f"Data retrieval failed with status: {self._status}")

    def trigger_interrupt(self):
        '''
        Trigger sensor to ready for new data measurements
        '''
        self._status = self._lib.VL53L1X_ClearInterrupt(self._dev)
        if self._status == 0:
            return None
        else:
            raise RuntimeError(f"Sensor trigger failed with status: {self._status}")

    

if __name__ == "__main__":
    
    print("Starting coms....")
    tof = ToF_Sensor(i2c_bus=1, i2c_addr=0x29)
    
    try:
        while(1):
            tof.check_for_data()
            result = tof.get_new_data()
            print(f"{'Distance':>10} {'Ambient':>10} {'SigPerSPAD':>15} {'NumSPADs':>10}")
            print(f"{result['Distance']:>10} {result['Ambient']:>10} {result['SigPerSPAD']:>15} {result['NumSPADs']:>10}")
            tof.trigger_interrupt()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping sensor")
