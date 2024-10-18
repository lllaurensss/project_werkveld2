from lib.gpio.relay_interface import RelayInterface


class MockRelay(RelayInterface):

    def __init__(self, gpio_pin: int):
        self._gpio_pin = gpio_pin

    def open_relay(self) -> None:
        pass

    def close_relay(self) -> None:
        pass
