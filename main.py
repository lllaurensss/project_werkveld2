import logging
import yaml

from lib.envirosense_app.enviro_sense import EnviroSense

if __name__ == "__main__":
    logger = logging.getLogger("EnviroSense")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("app.log")

    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    config = None
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    enviro_sense = EnviroSense(logger, config)
    enviro_sense.run()
