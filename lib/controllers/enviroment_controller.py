
class EnvironmentController:
    """
    Adjust the threshold, Kp, and Kd values to control the response:

    Increase Kp for a stronger response to the temperature difference.
    Increase Kd if you want the controller to be more responsive to changes in temperature difference over time.
    Threshold: Start with a moderate threshold and adjust until the heating element only turns on when there's a significant enough temperature difference.
    """
    def __init__(self, kp, kd, threshold):
        self._kp = kp  # Proportional gain
        self._kd = kd  # Derivative gain
        self._threshold = threshold  # Threshold to turn on the heater
        self._previous_error = 0  # Store the previous error

    def calculate_abstract_device_on_off(self, internal_env_value: float, external_env_value: float) -> bool:
        # Calculate the error (difference in temperatures)
        error = external_env_value - internal_env_value

        p_out = self._kp * error
        d_out = self._kd * (error - self._previous_error)
        pd_output = p_out + d_out

        self._previous_error = error

        if pd_output > self._threshold:
            return True  # Turn on the heater
        else:
            return False  # Turn off the heater


if __name__ == "__main__":
    # Initialize the controller with tuning parameters
    Kp = 0.5  # Proportional gain
    Kd = 0.1  # Derivative gain
    threshold = 10  # PD output threshold to turn on the heater (tune this as needed)

    heating_controller = EnvironmentController(Kp, Kd, threshold)

    # Example usage
    internal_temp = 20
    external_temp = 25

    # Get heating control status
    heater_status = heating_controller.calculate_abstract_device_on_off(internal_temp, external_temp)
    print(f"Heater status: {heater_status}")
