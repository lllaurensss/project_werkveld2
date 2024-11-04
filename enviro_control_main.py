import yaml
from lib.envirocontrol_app.enviro_control import EnviroControl

if __name__ == "__main__":
    config = None
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    enviro_control = EnviroControl(config)
    enviro_control.run()
