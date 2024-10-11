import uuid


class DigitalId:

    @staticmethod
    def create_digital_id():
        device_id = uuid.uuid4()
        return str(device_id)
