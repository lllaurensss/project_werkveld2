from lib.gpio.drivers.mock_relay import MockRelay
from lib.gpio.drivers.raspberry_pi_relay import RaspberryPiRelay
from lib.gpio.relay_driver import RelayDriver
from lib.gpio.relay_interface import RelayInterface


class RelayFactory:

    @staticmethod
    def create_relay(relay_driver: RelayDriver, gpio_pin: int = None) -> RelayInterface:
        if relay_driver == RelayDriver.RPI:
            return RaspberryPiRelay(gpio_pin)
        if relay_driver == RelayDriver.MOCK:
            return MockRelay(gpio_pin)
