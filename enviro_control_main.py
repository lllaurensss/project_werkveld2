import yaml

from enviro_sense_main import run_enviro_control

if __name__ == "__main__":
    config = None
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    run_enviro_control(config)
