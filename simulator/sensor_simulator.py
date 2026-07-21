import json
import random
import threading
import time
from datetime import datetime

import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
SENSOR_ID = "SENSOR-001"
MQTT_TOPIC = f"sensores/{SENSOR_ID}/datos"
INTERVALO_SEGUNDOS = 1
DURACION_FALLA_SEGUNDOS = 8

fault_mode = False
fault_lock = threading.Lock()


def lectura_normal() -> dict:
    return {
        "sensor_id": SENSOR_ID,
        "temperature": round(random.gauss(60, 3), 2),
        "vibration": round(random.gauss(1.5, 0.2), 2),
        "pressure": round(random.gauss(100, 5), 2),
        "timestamp": datetime.utcnow().isoformat(),
    }


def lectura_con_falla() -> dict:
    return {
        "sensor_id": SENSOR_ID,
        "temperature": round(random.uniform(85, 100), 2),
        "vibration": round(random.uniform(3.5, 5.5), 2),
        "pressure": round(random.uniform(125, 160), 2),
        "timestamp": datetime.utcnow().isoformat(),
    }


def escuchar_teclado():
    global fault_mode
    while True:
        input()  # bloquea hasta que el usuario presione ENTER
        with fault_lock:
            fault_mode = True
        print(f"⚠️  Falla inyectada durante {DURACION_FALLA_SEGUNDOS} segundos...")

        def apagar_falla():
            global fault_mode
            time.sleep(DURACION_FALLA_SEGUNDOS)
            with fault_lock:
                fault_mode = False
            print("✅ Falla finalizada, volviendo a modo normal.")

        threading.Thread(target=apagar_falla, daemon=True).start()


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()

    threading.Thread(target=escuchar_teclado, daemon=True).start()

    print(f"Publicando en '{MQTT_TOPIC}' cada {INTERVALO_SEGUNDOS}s. "
          f"Presioná ENTER para inyectar una falla artificial. Ctrl+C para salir.")

    try:
        while True:
            with fault_lock:
                en_falla = fault_mode
            payload = lectura_con_falla() if en_falla else lectura_normal()

            client.publish(MQTT_TOPIC, json.dumps(payload))
            estado = "🔴 FALLA" if en_falla else "🟢 normal"
            print(f"[{estado}] {payload}")

            time.sleep(INTERVALO_SEGUNDOS)
    except KeyboardInterrupt:
        print("Deteniendo simulador...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
