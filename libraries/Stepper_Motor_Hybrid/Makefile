# Build system for the bi-polar hybrid stepper motor driver
# Build instructions for shared library:
# 	Use make hybrid_motor_driver.so command for linux system

CC=$(CCPREFIX)gcc

SRC=src
INC=include
CFLAGS += -I$(INC) -Wall -g -D_LINUX_ -fPIC

CFLAGS += -I/home/mjmar62/Custom_Apps/LLM-spatial-scanner/libraries/gpiod/libgpiod/include
LFLAGS += -L/home/mjmar62/Custom_Apps/LLM-spatial-scanner/libraries/gpiod/libgpiod/lib/.libs -lgpiod

# Object files for build
MAIN_OBJ = main.o
SRC_OBJ =  $(SRC)/motor_control_api.o  \
		   $(SRC)/motor_gpio.o \
		   $(SRC)/motor_timing.o

# Build object files
%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS)

# Build the executable
motor_driver_test: $(SRC_OBJ) $(MAIN_OBJ)
	$(CC) -o $@ $^ $(CFLAGS) -lpthread $(LFLAGS)

# Build the shared library
motor_driver.so: $(SRC_OBJ) $(MAIN_OBJ)
	$(CC) -shared -o $@ $^ $(CFLAGS) -lpthread $(LFLAGS)

clean:
	find . -name "*.o" | xargs rm -f
	rm -f app motor_driver_test
	rm -f app motor_driver

