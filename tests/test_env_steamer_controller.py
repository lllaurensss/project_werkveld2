import time
import matplotlib.pyplot as plt

from lib.controllers.enviroment_controller import EnvironmentController
from lib.util.csv_lookup import CSVLookup


# stel u heersende temperatuur is 30° dan gaat ge in u tabel de waarde zoeken voor de temperatuur van 29° wat dat is het maximale vocht dat er mag zijn
# is dat onder die waarde van 29° dan moet ge de stomer gaan aanzetten
class TestEnvSteamerController:

    def test_basic_steam_env_controller(self):
        # arrange
        internal_temp = 20.59
        internal_humidity = 13.65
        kp = 0.3
        kd = 0.3
        threshold = 0.5

        csv_env_table = CSVLookup("../doc/waterdampspanning.csv")
        steamer_control = EnvironmentController(kp, kd, threshold)

        # act
        target_humidity = csv_env_table.get_closest_value(internal_temp)[1]
        turn_steamer_on = steamer_control.calculate_abstract_device_on_off(internal_humidity, target_humidity)

        assert turn_steamer_on

    def test_very_long_pd_controller_steam(self):
        # Arrange
        kp = 0.3
        kd = 0.6
        threshold = 0.5
        steam_control = EnvironmentController(kp, kd, threshold)

        internal_humidity = 23.05
        wanted_humidity = 28.73

        start_time = time.time()
        duration = 60 * 10
        steamer_on = False
        is_above_target = False

        # Data collection for plotting
        time_values = []
        internal_temp_values = []
        external_temp_values = []
        heater_status_values = []

        while time.time() - start_time < duration:
            elapsed_time = time.time() - start_time
            time_values.append(elapsed_time)
            internal_temp_values.append(internal_humidity)
            external_temp_values.append(wanted_humidity)
            heater_status_values.append(steamer_on)

            steamer_on = steam_control.calculate_abstract_device_on_off(internal_humidity, wanted_humidity)
            if steamer_on:
                internal_humidity += 0.486
            else:
                internal_humidity -= 0.05 * (internal_humidity - wanted_humidity)

            if internal_humidity > wanted_humidity:
                is_above_target = True
            time.sleep(1)

        plt.figure(figsize=(10, 6))
        plt.plot(time_values, internal_temp_values, label="Internal humidity (gm3)", color="blue")
        plt.plot(time_values, external_temp_values, label="Wanted humidity (gm3)", color="orange", linestyle="--")
        plt.fill_between(time_values, wanted_humidity, max(internal_temp_values), where=heater_status_values,
                         color='lightcoral', alpha=0.3, label="Steamer ON")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Temperature (°C)")
        plt.title("test_very_long_pd_controller_steam")
        plt.legend()
        plt.savefig("test_very_long_pd_controller_steam.png")

        assert is_above_target, f"The internal steam did not stay above the wanted steam for {duration} seconds."