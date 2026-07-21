class SensorNotFoundError(Exception):

    def __init__(self, sensor_id: str):
        self.sensor_id = sensor_id
        super().__init__(f"El sensor '{sensor_id}' no está registrado.")


class InactiveSensorError(Exception):

    def __init__(self, sensor_id: str):
        self.sensor_id = sensor_id
        super().__init__(f"El sensor '{sensor_id}' se encuentra desactivado.")