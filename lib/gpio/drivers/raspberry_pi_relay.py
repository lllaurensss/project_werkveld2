import time
from lib.gpio.relay_interface import RelayInterface

# Try to import RPi.GPIO, or define a mock if unavailable
try:
    import RPi.GPIO as GPIO
except ImportError:
    # Define a mock GPIO class for non-Raspberry Pi environments
    class MockGPIO:
        BCM = 'BCM'
        OUT = 'OUT'
        HIGH = 'HIGH'
        LOW = 'LOW'

        @staticmethod
        def setmode(mode):
            print(f"MockGPIO: set mode to {mode}")

        @staticmethod
        def setup(pin, mode):
            print(f"MockGPIO: set up pin {pin} as {mode}")

        @staticmethod
        def output(pin, state):
            print(f"MockGPIO: set pin {pin} to {state}")

        @staticmethod
        def cleanup():
            print("MockGPIO: cleaned up")


    # Use the mock class in place of GPIO
    GPIO = MockGPIO


class RaspberryPiRelay(RelayInterface):

    def __init__(self, gpio_pin: int = 17) -> None:
        self._gpio_pin = gpio_pin
        self._init_gpio()

    def _init_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._gpio_pin, GPIO.OUT)

    def open_relay(self):
        GPIO.output(self._gpio_pin, GPIO.HIGH)
        time.sleep(2)

    def close_relay(self):
        GPIO.output(self._gpio_pin, GPIO.LOW)  # Deactivate relay
        time.sleep(5)

    def __del__(self):
        GPIO.cleanup()
