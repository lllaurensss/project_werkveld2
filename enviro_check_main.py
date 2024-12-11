import cmd

from lib.gpio.relay_driver import RelayDriver
from lib.gpio.relay_factory import RelayFactory
from lib.gpio.relay_interface import RelayInterface
from lib.sensor_drivers.sensor_driver import SensorDriver
from lib.sensor_drivers.sensor_factory import SensorFactory
from lib.sensor_drivers.sensor_interface import SensorInterface


class DeviceManager:
    def __init__(self):
        self._sensors = {}
        self._relays = {}

    def register_sensor(self, name: str, sensor: SensorInterface) -> None:
        self._sensors[name.lower()] = sensor

    def register_relay(self, name: str, relay: RelayInterface) -> None:
        self._relays[name.lower()] = relay

    def get_sensor(self, name: str) -> SensorInterface:
        return self._sensors.get(name.lower())

    def get_relay(self, name: str) -> RelayInterface:
        return self._relays.get(name.lower())

    def list_sensors(self) -> list:
        return list(self._sensors.keys())

    def list_relays(self) -> list:
        return list(self._relays.keys())


class SensorShell(cmd.Cmd):
    intro = "Welcome to the Sensor Shell. Type help or ? to list commands.\n"
    prompt = "(sensor-shell) "

    def __init__(self, manager: DeviceManager):
        super().__init__()
        self._manager = manager

    def do_read(self, arg):
        """Read sensor data. Example: read <sensor_name>"""
        sensor_name = arg.strip()
        sensor = self._manager.get_sensor(sensor_name)
        if sensor:
            try:
                data = sensor.get_sensor_data()
                print(f"{sensor_name.capitalize()} Sensor Reading: {data}")
            except Exception as e:
                print(f"Error reading from {sensor_name}: {e}")
        else:
            print(f"Sensor '{sensor_name}' not found. Available sensors: {', '.join(self._manager.list_sensors())}")

    def do_control(self, arg):
        """Control a relay. Example: control <relay name> <action>"""
        try:
            parts = arg.split()
            if len(parts) < 2:
                print("Usage: control <relay_name> <action>")
                return

            relay_name, action = parts[0], parts[1]
            relay = self._manager.get_relay(relay_name)
            if relay:
                if action.lower() == "open":
                    relay.open_relay()
                elif action.lower() == "close":
                    relay.close_relay()
                else:
                    print("this action doesn't exist for relay drivers (open/close)")
            else:
                print(f"Relay '{relay_name}' not found. Available actuators: {', '.join(self._manager.list_relays())}")
        except Exception as e:
            print(f"Error controlling relay: {e}")

    def do_list(self, arg):
        """List all devices"""
        sensors = self._manager.list_sensors()
        relays = self._manager.list_relays()
        if sensors:
            print("Available Sensors:")
            for sensor in sensors:
                print(f"  - {sensor}")
        if relays:
            print("Available Relays:")
            for relay in relays:
                print(f"  - {relay}")
        else:
            print("No devices registered.")

    def do_exit(self, arg):
        """Exit the shell"""
        print("Goodbye!")
        return True


if __name__ == "__main__":

    dht22 = SensorFactory.create_driver(SensorDriver.MOCK, 22)
    bme280 = SensorFactory.create_driver(SensorDriver.MOCK, 0x76)

    relay_heater = RelayFactory.create_relay(RelayDriver.MOCK, 17)
    relay_steamer = RelayFactory.create_relay(RelayDriver.MOCK, 27)

    manager = DeviceManager()
    manager.register_sensor("dht22", dht22)
    manager.register_sensor("bme280", bme280)

    manager.register_relay("heater", relay_heater)
    manager.register_relay("steamer", relay_steamer)

    # Start the shell
    SensorShell(manager).cmdloop()
