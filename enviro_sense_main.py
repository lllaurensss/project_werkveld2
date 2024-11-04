import yaml
from lib.envirosense_app.enviro_sense import EnviroSense


if __name__ == "__main__":
    config = None
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    enviro_sense = EnviroSense(config)
    enviro_sense.run()
