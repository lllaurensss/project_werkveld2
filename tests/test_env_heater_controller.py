import time
import matplotlib.pyplot as plt
from lib.controllers.enviroment_controller import EnvironmentController


class TestEnvHeaterController:

    def test_can_heat_the_box(self):
        # arrange
        kp = 0.3
        kd = 0.2
        threshold = 0.5
        heating_control = EnvironmentController(kp, kd, threshold)

        internal_temp = 18
        external_temp = 20

        while internal_temp <= external_temp:
            turn_heater_on = heating_control.calculate_abstract_device_on_off(internal_temp, external_temp)
            if turn_heater_on:
                internal_temp = internal_temp + 0.486

        # arrange
        assert turn_heater_on

    def test_wont_heat_the_box(self):
        # arrange
        kp = 0.3
        kd = 0.2
        threshold = 0.5
        heating_control = EnvironmentController(kp, kd, threshold)

        internal_temp = 25
        external_temp = 20

        turn_heater_on = heating_control.calculate_abstract_device_on_off(internal_temp, external_temp)

        # arrange
        assert turn_heater_on is False

    def test_long_pd_controller_when_internal_is_lower_than_external(self):
        # Arrange
        kp = 0.3
        kd = 0.2
        threshold = 0.5
        heating_control = EnvironmentController(kp, kd, threshold)

        internal_temp = 18  # Initial internal temperature
        external_temp = 20  # Target external temperature

        start_time = time.time()
        duration = 120  # Duration in seconds (2 minutes)
        heater_on = False
        is_above_target = False

        time_values = []
        internal_temp_values = []
        external_temp_values = []
        heater_status_values = []

        while time.time() - start_time < duration:
            elapsed_time = time.time() - start_time
            time_values.append(elapsed_time)
            internal_temp_values.append(internal_temp)
            external_temp_values.append(external_temp)
            heater_status_values.append(heater_on)

            heater_on = heating_control.calculate_abstract_device_on_off(internal_temp, external_temp)
            if heater_on:
                internal_temp += 0.486
            else:
                internal_temp -= 0.05 * (internal_temp - external_temp)

            if internal_temp > external_temp:
                is_above_target = True
            time.sleep(1)

        # Plot temperature and heater status over time
        plt.figure(figsize=(10, 6))
        plt.plot(time_values, internal_temp_values, label="Internal Temperature (°C)", color="blue")
        plt.plot(time_values, external_temp_values, label="External Temperature (°C)", color="orange", linestyle="--")
        plt.fill_between(time_values, external_temp, max(internal_temp_values), where=heater_status_values,
                         color='lightcoral', alpha=0.3, label="Heater ON")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Temperature (°C)")
        plt.title("test_long_pd_controller_when_internal_is_lower_than_external")
        plt.legend()
        plt.savefig("test_long_pd_controller_when_internal_is_lower_than_external.png")

        assert is_above_target, "The internal temperature did not stay above the external temperature for 2 minutes."

    def test_long_pd_controller_when_internal_is_higher_than_external(self):
        # Arrange
        kp = 0.3
        kd = 0.2
        threshold = 0.5
        heating_control = EnvironmentController(kp, kd, threshold)

        internal_temp = 22  # Initial internal temperature
        external_temp = 20  # Target external temperature

        start_time = time.time()
        duration = 120  # Duration in seconds (2 minutes)
        heater_on = False
        is_above_target = False

        # Data collection for plotting
        time_values = []
        internal_temp_values = []
        external_temp_values = []
        heater_status_values = []

        while time.time() - start_time < duration:
            elapsed_time = time.time() - start_time
            time_values.append(elapsed_time)
            internal_temp_values.append(internal_temp)
            external_temp_values.append(external_temp)
            heater_status_values.append(heater_on)

            heater_on = heating_control.calculate_abstract_device_on_off(internal_temp, external_temp)
            if heater_on:
                internal_temp += 0.486
            else:
                internal_temp -= 0.05 * (internal_temp - external_temp)

            if internal_temp > external_temp:
                is_above_target = True
            time.sleep(1)

        plt.figure(figsize=(10, 6))
        plt.plot(time_values, internal_temp_values, label="Internal Temperature (°C)", color="blue")
        plt.plot(time_values, external_temp_values, label="External Temperature (°C)", color="orange", linestyle="--")
        plt.fill_between(time_values, external_temp, max(internal_temp_values), where=heater_status_values,
                         color='lightcoral', alpha=0.3, label="Heater ON")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Temperature (°C)")
        plt.title("test_long_pd_controller_when_internal_is_higher_than_external")
        plt.legend()
        plt.savefig("test_long_pd_controller_when_internal_is_higher_than_external.png")

        assert is_above_target, "The internal temperature did not stay above the external temperature for 2 minutes."

    def test_very_long_pd_controller(self):
        # Arrange
        kp = 0.3
        kd = 0.2
        threshold = 0.5
        heating_control = EnvironmentController(kp, kd, threshold)

        internal_temp = 18  # Initial internal temperature
        external_temp = 23  # Target external temperature

        start_time = time.time()
        duration = 60 * 10
        heater_on = False
        is_above_target = False

        # Data collection for plotting
        time_values = []
        internal_temp_values = []
        external_temp_values = []
        heater_status_values = []

        while time.time() - start_time < duration:
            elapsed_time = time.time() - start_time
            time_values.append(elapsed_time)
            internal_temp_values.append(internal_temp)
            external_temp_values.append(external_temp)
            heater_status_values.append(heater_on)

            heater_on = heating_control.calculate_abstract_device_on_off(internal_temp, external_temp)
            if heater_on:
                internal_temp += 0.486
            else:
                internal_temp -= 0.05 * (internal_temp - external_temp)

            if internal_temp > external_temp:
                is_above_target = True
            time.sleep(1)

        plt.figure(figsize=(10, 6))
        plt.plot(time_values, internal_temp_values, label="Internal Temperature (°C)", color="blue")
        plt.plot(time_values, external_temp_values, label="External Temperature (°C)", color="orange", linestyle="--")
        plt.fill_between(time_values, external_temp, max(internal_temp_values), where=heater_status_values,
                         color='lightcoral', alpha=0.3, label="Heater ON")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Temperature (°C)")
        plt.title("test_very_long_pd_controller")
        plt.legend()
        plt.savefig("test_very_long_pd_controller.png")

        assert is_above_target, f"The internal temperature did not stay above the external temperature for {duration} seconds."
