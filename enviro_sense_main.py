import signal
import sys

import yaml

from multiprocessing import Process

from lib.envirocontrol_app.enviro_control import EnviroControl
from lib.envirosense_app.enviro_sense import EnviroSense


def run_enviro_sense(config):
    enviro_sense = EnviroSense(config)
    enviro_sense.run()


def run_enviro_control(config):
    enviro_control = EnviroControl(config)
    enviro_control.run()


def cleanup_processes(processes):
    for p in processes:
        if p.is_alive():
            p.terminate()
            p.join()  # Wait for process to terminate


def signal_handler(sig, frame, processes):
    print("Signal received, terminating processes...")
    cleanup_processes(processes)
    sys.exit(0)


if __name__ == "__main__":
    config = None
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    run_enviro_sense(config)
