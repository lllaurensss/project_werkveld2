from simple_pid import PID
import time


class EnvironmentController:
    """
    A PD-based controller to manage an ON/OFF heating device. The heater turns on if the
    internal temperature is significantly lower than the external (target) temperature.

    Adjust the `kp`, `kd`, and `threshold` values to control response:

    - Increase `kp` for a stronger response to the temperature difference.
    - Increase `kd` for a quicker response to changes in temperature difference.
    - `threshold`: This is the PD output level above which the heater will turn on.
    """

    def __init__(self, kp, kd, threshold):
        self._kp = kp  # Proportional gain
        self._kd = kd  # Derivative gain
        self._ki = 0.05
        self._integral = 0
        self._threshold = threshold  # Output threshold to turn on the heater
        self._previous_error = 0  # Store the previous error for derivative calculation

    def calculate_abstract_device_on_off(self, internal_env_value: float, external_env_value: float) -> bool:
        """
        Calculates whether the heater should be ON or OFF based on PD output.

        Args:
            internal_env_value (float): Current internal temperature.
            external_env_value (float): Target external temperature.

        Returns:
            bool: True if the heater should be ON, False if it should be OFF.
        """
        # Calculate the error (difference between target and current temperature)
        error = external_env_value - internal_env_value
        self._integral += error

        # PD output calculations
        p_out = self._kp * error  # Proportional component
        d_out = self._kd * (error - self._previous_error)  # Derivative component
        i_out = self._ki * self._integral

        # Total PD output
        pd_output = p_out + d_out + i_out

        # Store the error for the next derivative calculation
        self._previous_error = error

        # Determine if the heater should be on or off based on the PD output
        return pd_output > self._threshold
