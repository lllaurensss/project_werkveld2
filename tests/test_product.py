import threading
from multiprocessing import Process

from lib.envirosense_app.enviro_sense import EnviroSense
from lib.mqtt.mqtt_manager import MQTTManager
from tests.test_infra import example_config


class TestProduct:

    def test_system_envirosense(self):
        # arrange
        mqtt_manager = MQTTManager()
        enviro_sense = EnviroSense(example_config)
        enviro_thread = threading.Thread(target=enviro_sense.run)
        enviro_thread.daemon = True

        # act
        enviro_thread.start()

        enviro_sense.stop()
        enviro_thread.join()

        # assert
        a = 3 + 1
