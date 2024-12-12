ip: 192.168.0.50

# Envirocontrol & enviroSense

## About
EnviroSense/control/cli are python applications written in python12. 
They were tested on a RPI4 and should be compatible RPI4+. 

The purpose of this application is to
* measure the temperature
* measure the air pressure
* measure the humidity
* control a relay (heater/steamer)

The application has been designed to be very versatile. 
At the moment there are two sensor drivers added. The BME280 and DHT22. You can chose to use
two DHT22 or two BME80 or a DHT22 with a BME280. If you use another sensor it is even possible to add that sensor by providing the sensor driver and add the sensor interface. This way you can add sensors. 

Because we chose a relay way of control, you can hook up any heater or steamer. The relay support up to 250VAC and can bear 16Amps.

You can also choose for a PID steering or a ON/OFF steering. With the PID you'll need to dry run several times to get the right PID values. With on/off you don't have to do that but you'll get more overshoots/undershoots. 

This all can be set in the configuration, yaml.config. More about that later.

## Installation
To install this software on your raspberry py you'll need to have the following things
* Python 3.9 or more installed preferably python 3.12
* Pip installed (pip3)

Once these are installed you can install all dependencies by running
`pip3 install -r requirements.txt`

This will install all dependencies. After that you can run the applications. Because of its very versatile nature you'll need to run 2 applications.
The order of running applications doesn't matter. What does matter is that there is a MQTT broker running. That Ip should be filled in the config.yaml: `  broker_address: "localhost"`.

## Running the applications
### adjust the config.yaml
Here you can find an example config. Be aware this will using mocked drivers. They don't produce any real data. It simulates data.
```
enviro_sense:
  internal_sensor_driver: "mock"
  internal_sensor_address: 0x76

  external_sensor_driver: "mock"
  external_sensor_address: 22

  relay_driver: "mock"

  broker_address: "localhost"
  broker_port: 1883

  enable_pid: false

  kp_heater: 0.3
  kd_heater: 0.2
  threshold_heater: 0.5

  kp_steamer: 0.3
  kd_steamer: 0.2
  threshold_steamer: 0.5

  sensor_publish_data_timeout: 3
  sensor_digital_id: "LP_ENVIROSENSE_APP"

  control_digital_id: "LP_ENVIROCONTROL_APP"
  control_sensor_to_listen: "LP_ENVIROSENSE_APP"

  control_relay_gpio_1: 17
  control_relay_gpio_2: 27
```

To run it in a production environment you'll need to set these things:
1. set the internal sensor to bme280 
   2. `internal_sensor_driver: "BME280"`
   3. `internal_sensor_address: 0x76`
4. set the external sensor to DHT22
   5. `external_sensor_driver: "DHT22"`
   6. `external_sensor_address: 22`
7. set the driver of the relay to that for the rpi: `relay_driver: "rpi"`
8. set the right pins for relay control: 
   9. `control_relay_gpio_1: 17`
   10. `control_relay_gpio_2: 27`
11. If you want to use PID set: `enable_pid: true` else `enable_pid: false`
12. The PID is different for the heater as for the steamer. Different app has different curves. To set the values:
    13. `kp_<device>: 0.3`
    14. `kd_<device>: 0.2`
    15. `threshold_<device>: 0.5`

This should be enough to run in on the same RPI. This will lead us to the following config
If you want to run it on the same rpi with PID on this would be an exmample config:
```
enviro_sense:
  internal_sensor_driver: "BME280"
  internal_sensor_address: 0x76

  external_sensor_driver: "DHT22"
  external_sensor_address: 22

  relay_driver: "RPI"

  broker_address: "192.168.0.50"
  broker_port: 1883

  enable_pid: true

  kp_heater: 0.3
  kd_heater: 0.2
  threshold_heater: 0.5

  kp_steamer: 0.3
  kd_steamer: 0.2
  threshold_steamer: 0.5

  sensor_publish_data_timeout: 3
  sensor_digital_id: "LP_ENVIROSENSE_APP"

  control_digital_id: "LP_ENVIROCONTROL_APP"
  control_sensor_to_listen: "LP_ENVIROSENSE_APP"

  control_relay_gpio_1: 17
  control_relay_gpio_2: 27
```
### more on tuning the PID
Tuninig a PID can be difficult but once the settings are set you are good to go.
Adjust the `kp`, `kd`, and `threshold` values to control response:

    - Increase `kp` for a stronger response to the temperature difference.
    - Increase `kd` for a quicker response to changes in temperature difference.
    - `threshold`: This is the PD output level above which the heater will turn on.

### runninig the applications
The order doesn't matter but the broker should be online before you start. 
`python3 enviro_sense_main.py` will start the application to read the sensors and send them to the mqtt broker.

The control app => `python3 enviro_control_main.py` will start controlling the relay to control the heater/steamer by PID or ON/OFF

Both will spit out logging information so that the user can follow along. But if there are problems you can always use a different application.
This app is a cli app which will let you control the relay or read out the sensors very easy.
You can start it by: `python3 enviro_check_main.py`. This will start a cli.

useful commands of this util app are:
* list => will list all devices (sensors, relays)
* read <sensor> => will give sensor information
  * read dht22
* control <relay> => will control the relay by commands open/close
  * control heater open
  * control steamer close

### problems
contact: Laurens.p@outlook.com or laurens.putseys@brightest.be