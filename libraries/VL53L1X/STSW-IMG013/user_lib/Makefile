# Build system for the VL53L1x ToF sensor
# Build instructions for shared library:
# 	Use make libvl53l1x.so command for linux system
# 	Source Files can be found through the ST website:
#	STSW-IMG013:  https://www.st.com/en/embedded-software/stsw-img013.html

#CC=gcc
#CCPREFIX=/home/user/rpi/tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian/bin/arm-linux-gnueabihf-
CC=$(CCPREFIX)gcc


INC_CFLAGS=-I.
CORE=core
CFLAGS+=$(INC_CFLAGS) -I$(CORE) -Wall -g -D_LINUX_ -fPIC

ifdef POLLING
	CFLAGS+=-D POLLING
endif


MAIN_OBJ = main.o
CORE_OBJ =  $(CORE)/VL53L1X_api.o  \
 		$(CORE)/VL53L1X_calibration.o
PLTF_OBJ =  vl53l1_linux_platform.o


%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS)


ultra_lite: $(CORE_OBJ) $(PLTF_OBJ) $(MAIN_OBJ)
	$(CC) -o $@ $^ $(CFLAGS) -lpthread

libvl53l1x.so: $(CORE_OBJ) $(PLTF_OBJ)
	$(CC) -shared -o $@ $^ $(CFLAGS) -lpthread

clean:
	find . -name "*.o" | xargs rm -f
	rm -f app ultra_lite
	rm -f app libvl53l1x

