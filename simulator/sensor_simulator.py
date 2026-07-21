import json
import os
import random
import threading
import time

import paho.mqtt.client as mqtt


MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

INTERVALO_SEGUNDOS = 1
DURACION_FALLA_SEGUNDOS = 8


SENSORS = [
    {
        "id": "SENSOR-001",
        "name": "Motor principal",
        "temperature_mean": 60.0,
        "temperature_std": 2.5,
        "vibration_mean": 1.50,
        "vibration_std": 0.18,
        "pressure_mean": 100.0,
        "pressure_std": 4.0,
    },
    {
        "id": "SENSOR-002",
        "name": "Compresor",
        "temperature_mean": 58.0,
        "temperature_std": 2.8,
        "vibration_mean": 1.40,
        "vibration_std": 0.20,
        "pressure_mean": 98.0,
        "pressure_std": 4.5,
    },
    {
        "id": "SENSOR-003",
        "name": "Bomba hidráulica",
        "temperature_mean": 61.0,
        "temperature_std": 2.6,
        "vibration_mean": 1.60,
        "vibration_std": 0.20,
        "pressure_mean": 102.0,
        "pressure_std": 4.0,
    },
    {
        "id": "SENSOR-004",
        "name": "Cinta transportadora",
        "temperature_mean": 57.0,
        "temperature_std": 2.4,
        "vibration_mean": 1.30,
        "vibration_std": 0.17,
        "pressure_mean": 99.0,
        "pressure_std": 4.5,
    },
    {
        "id": "SENSOR-005",
        "name": "Generador",
        "temperature_mean": 63.0,
        "temperature_std": 2.7,
        "vibration_mean": 1.70,
        "vibration_std": 0.22,
        "pressure_mean": 104.0,
        "pressure_std": 4.0,
    },
]


fault_until_by_sensor: dict[str, float] = {}
fault_lock = threading.Lock()


def build_topic(sensor_id: str) -> str:
    return f"sensores/{sensor_id}/datos"


def lectura_normal(sensor: dict) -> dict:
    return {
        "sensor_id": sensor["id"],
        "temperature": round(
            random.gauss(
                sensor["temperature_mean"],
                sensor["temperature_std"],
            ),
            2,
        ),
        "vibration": round(
            max(
                0,
                random.gauss(
                    sensor["vibration_mean"],
                    sensor["vibration_std"],
                ),
            ),
            2,
        ),
        "pressure": round(
            random.gauss(
                sensor["pressure_mean"],
                sensor["pressure_std"],
            ),
            2,
        ),
    }


def lectura_con_falla(sensor: dict) -> dict:
    return {
        "sensor_id": sensor["id"],
        "temperature": round(
            random.uniform(
                sensor["temperature_mean"] + 25,
                sensor["temperature_mean"] + 40,
            ),
            2,
        ),
        "vibration": round(
            random.uniform(
                sensor["vibration_mean"] + 2.5,
                sensor["vibration_mean"] + 4.0,
            ),
            2,
        ),
        "pressure": round(
            random.uniform(
                sensor["pressure_mean"] + 25,
                sensor["pressure_mean"] + 50,
            ),
            2,
        ),
    }


def sensor_en_falla(sensor_id: str) -> bool:
    current_time = time.monotonic()

    with fault_lock:
        fault_until = fault_until_by_sensor.get(sensor_id)

        if fault_until is None:
            return False

        if current_time >= fault_until:
            del fault_until_by_sensor[sensor_id]
            print(f"✅ Falla finalizada en {sensor_id}.")
            return False

        return True


def activar_falla(sensor_id: str) -> None:
    with fault_lock:
        fault_until_by_sensor[sensor_id] = (
            time.monotonic() + DURACION_FALLA_SEGUNDOS
        )

    sensor = next(
        sensor
        for sensor in SENSORS
        if sensor["id"] == sensor_id
    )

    print(
        f"⚠️ Falla inyectada en {sensor_id} "
        f"({sensor['name']}) durante "
        f"{DURACION_FALLA_SEGUNDOS} segundos."
    )


def buscar_sensor(command: str) -> dict | None:
    normalized_command = command.strip().upper()

    if not normalized_command:
        return random.choice(SENSORS)

    if normalized_command.isdigit():
        sensor_position = int(normalized_command) - 1

        if 0 <= sensor_position < len(SENSORS):
            return SENSORS[sensor_position]

        return None

    return next(
        (
            sensor
            for sensor in SENSORS
            if sensor["id"] == normalized_command
        ),
        None,
    )


def escuchar_teclado() -> None:
    print()
    print("Inyección manual de fallas:")
    print("  ENTER       -> sensor aleatorio")
    print("  1 a 5       -> seleccionar sensor por número")
    print("  SENSOR-001  -> seleccionar por identificador")
    print()

    while True:
        try:
            command = input(
                "Sensor para inyectar falla: "
            )
        except EOFError:
            return

        sensor = buscar_sensor(command)

        if sensor is None:
            print(
                "Sensor inválido. Usá un número entre 1 y 5 "
                "o un identificador como SENSOR-003."
            )
            continue

        activar_falla(sensor["id"])


def publish_reading(
    client: mqtt.Client,
    sensor: dict,
) -> None:
    sensor_id = sensor["id"]
    en_falla = sensor_en_falla(sensor_id)

    payload = (
        lectura_con_falla(sensor)
        if en_falla
        else lectura_normal(sensor)
    )

    topic = build_topic(sensor_id)

    publish_result = client.publish(
        topic,
        json.dumps(payload),
    )

    if publish_result.rc != mqtt.MQTT_ERR_SUCCESS:
        print(
            f"❌ No se pudo publicar la lectura de {sensor_id}. "
            f"Código MQTT: {publish_result.rc}"
        )
        return

    status = "🔴 FALLA" if en_falla else "🟢 normal"

    print(
        f"[{status}] "
        f"{sensor_id} | "
        f"Temp: {payload['temperature']} °C | "
        f"Vib: {payload['vibration']} mm/s | "
        f"Presión: {payload['pressure']} kPa"
    )


def main() -> None:
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2
    )

    try:
        client.connect(
            MQTT_BROKER,
            MQTT_PORT,
            keepalive=60,
        )
    except OSError as exc:
        print(
            f"❌ No se pudo conectar al broker MQTT "
            f"{MQTT_BROKER}:{MQTT_PORT}: {exc}"
        )
        return

    client.loop_start()

    keyboard_thread = threading.Thread(
        target=escuchar_teclado,
        daemon=True,
    )
    keyboard_thread.start()

    print(
        f"Publicando lecturas de {len(SENSORS)} sensores "
        f"cada {INTERVALO_SEGUNDOS} segundo(s)."
    )
    print(f"Broker MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    print("Presioná Ctrl+C para detener el simulador.")
    print()

    try:
        while True:
            for sensor in SENSORS:
                publish_reading(client, sensor)

            time.sleep(INTERVALO_SEGUNDOS)

    except KeyboardInterrupt:
        print("\nDeteniendo simulador...")

    finally:
        client.loop_stop()
        client.disconnect()
        print("Simulador desconectado.")


if __name__ == "__main__":
    main()