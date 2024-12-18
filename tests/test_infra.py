example_config = {
            'enviro_sense':
                {
                    'internal_sensor_driver': 'mock',
                    'internal_sensor_address': 118,
                    'external_sensor_driver': 'mock',
                    'external_sensor_address': 22,
                    'relay_driver': 'mock',
                    'broker_address': 'localhost',
                    'broker_port': 1883,
                    'kp_heater': 0.3,
                    'kd_heater': 0.2,
                    'threshold_heater': 0.5,
                    'sensor_publish_data_timeout': 3,
                    'sensor_digital_id': 'LP_ENVIROSENSE_APP',
                    'control_digital_id': 'LP_ENVIROCONTROL_APP',
                    'control_sensor_to_listen': 'LP_ENVIROSENSE_APP',
                    'control_relay_gpio_1': 17,
                    'control_relay_gpio_2': 27
                }
        }