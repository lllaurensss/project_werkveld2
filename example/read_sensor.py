import time
import RPi.GPIO as GPIO
from smbus2 import SMBus
from bme280 import BME280

# GPIO setup for relay
GPIO.setmode(GPIO.BCM)
RELAY_PIN = 17  # GPIO pin connected to the relay
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Initialize the sensor
bus = SMBus(1)  # I2C bus 1 on the Raspberry Pi
bme280 = BME280(i2c_dev=bus)

# PD control parameters
K_p = 1.5  # Proportional gain
K_d = 0.1  # Derivative gain
previous_error = 0
previous_time = time.time()


# Relay control function
def set_heater(state):
    GPIO.output(RELAY_PIN, GPIO.HIGH if state else GPIO.LOW)


# Target temperature setter
def set_temperature(target_temp):
    global previous_error, previous_time

    while True:
        # Read current temperature
        current_temp = bme280.get_temperature()

        # Calculate error
        error = target_temp - current_temp

        # Calculate time difference
        current_time = time.time()
        dt = current_time - previous_time if current_time - previous_time > 0 else 1e-6

        # Proportional and derivative terms
        P_out = K_p * error
        D_out = K_d * (error - previous_error) / dt

        # Control output
        control_output = P_out + D_out

        # Determine if heater should be on or off
        if control_output > 0:
            set_heater(True)  # Turn on the heating element
            print("Heating ON")
        else:
            set_heater(False)  # Turn off the heating element
            print("Heating OFF")

        print(f"Temperature: {current_temp:.2f} °C, Control Output: {control_output:.2f}")

        # Update previous error and time
        previous_error = error
        previous_time = current_time

        # Delay (control loop frequency)
        time.sleep(1)  # Run control loop every second


try:
    set_temperature(25.0)  # Example target temperature
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()  # Clean up GPIO settings on exit