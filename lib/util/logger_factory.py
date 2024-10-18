import logging


class LoggerFactory:

    @staticmethod
    def create(logger_name: str):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(f"{logger_name}.log")

        console_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger
