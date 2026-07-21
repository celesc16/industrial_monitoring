# Backend — Sistema de Monitoreo Industrial

API desarrollada con **FastAPI** para un sistema de monitoreo industrial en tiempo real.

Gestiona la recepción de datos de sensores, almacenamiento de mediciones, detección de anomalías mediante IA y comunicación en tiempo real con el dashboard mediante WebSocket.


## Tecnologías

- Python
- FastAPI
- MQTT (Mosquitto)
- WebSocket
- PostgreSQL
- Scikit-learn
- Docker

## 1. Instalar dependencias

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configurar variables de entorno

```bash
cp .env_example .env
```

Para las alertas de Telegram: crear un bot con `@BotFather`, copiar el token,
y obtener tu `chat_id` hablándole a `@userinfobot`. Si dejás esos campos
vacíos, el sistema funciona igual: solo queda logueado como warning en vez
de mandar el mensaje.

## 3. Entrenar el modelo de IA

```bash
python scripts/train_model.py
```

Genera `app/ml/artifacts/model.pkl` (Isolation Forest + scaler) a partir de
datos sintéticos de operación normal. Cuando tengas datos reales de planta,
reemplazá `generar_datos_normales()` por la carga de tu histórico real.

## 4. Levantar el broker MQTT (Mosquitto)

```bash
docker compose up -d mosquitto
```

> `allow_anonymous true` en `mosquitto.conf` es solo para desarrollo.
> Para producción, configurar usuario/contraseña o certificados.

## 5. Levantar el backend

```bash
uvicorn app.main:app --reload --port 8000
```

(o `docker compose up --build` para levantar backend + Mosquitto juntos)

- WebSocket en vivo: `ws://localhost:8000/ws`
- Histórico: `GET http://localhost:8000/api/v1/readings?limit=100`
- Estadísticas: `GET http://localhost:8000/api/v1/stats`
- Salud: `GET http://localhost:8000/api/v1/health`
- Docs interactivas (Swagger): `http://localhost:8000/docs`

## 6. Probar de punta a punta

**Opción A — con el simulador real (MQTT):**

```bash
cd ../simulator
pip install -r requirements.txt
python sensor_simulator.py
```

Apretá ENTER en la consola del simulador para inyectar una falla artificial
y ver la alerta viajar por todo el pipeline (IA → DB → WebSocket → Telegram).

**Opción B — sin Mosquitto, solo para probar el backend:**

```bash
curl -X POST http://localhost:8000/api/v1/simulate \
  -H "Content-Type: application/json" \
  -d '{"sensor_id": "1", "temperature": 92, "vibration": 4.1, "pressure": 145}'
```

## 7. Correr los tests

```bash
pytest
```
