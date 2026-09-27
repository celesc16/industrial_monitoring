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

### Autenticación y roles (RBAC)

Al iniciar la app se crean automáticamente dos cuentas demo si no existen:

| Rol      | Email               | Contraseña | Permisos                                                  |
|----------|---------------------|------------|-----------------------------------------------------------|
| ADMIN    | `admin@demo.com`    | `1234`     | Consultas + activar/desactivar sensores (controles demo)  |
| VIEWER   | `operario@demo.com` | `1234`     | Consultas (solo lectura)                                  |

Obtener un token JWT:

```bash
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@demo.com", "password": "1234"}'
```

Devuelve `access_token`, `role` y `email`. Incluí el token en el header
`Authorization: Bearer <token>` para acceder a rutas protegidas, por
ejemplo `PATCH /api/v1/sensors/{id}/status` (solo ADMIN).

- Sin token → `401`.
- Token de un rol `VIEWER` en ruta de administrador → `403`.
- Token inválido o expirado → `401`.

### Planificación de mantenimiento (programación matemática / confiabilidad)

El dominio `maintenance_scheduler` recomienda la edad óptima a la que
conviene detener preventivamente una máquina, minimizando el costo
esperado por día de operación, combinando dos términos que penalizan el
retraso del mantenimiento:

- Se modela el tiempo hasta la falla con una **distribución de Weibull**:
  fiabilidad `R(t) = e^{-(t/η)^β}` y probabilidad de falla acumulada
  `F(t) = 1 - R(t)`. El shape `β > 1` refleja fallas por desgaste.
- La decisión `T` es la **edad de reemplazo preventivo** (ventana en días).
- Si la máquina llega a `T` sin fallar: parada planificada de costo `C_m`.
- Si falla antes de `T`: parada no planificada de costo `C_f >> C_m`.

Minimizamos la tasa de costo esperado por día (modelo de reemplazo por
edad de Barlow-Proschan):

```
C(T) = [ C_m·R(T) + C_f·F(T) ] / ∫₀ᵀ R(t) dt
```

El numerador es el costo esperado del ciclo y el denominador, su
duración esperada. Retrasar `T` aumenta `F(T)`, trasladando cada vez más
paradas al escenario caro de falla no planificada (`C_f` en vez de
`C_m`); apurarlo demasiado paga `C_m` con una frecuencia innecesaria.
El óptimo equilibra ambos, y el modelo reporta además el costo de "dejarlo
correr hasta fallar" (`C_f` dividido por el MTTF) para dimensionar el
ahorro de mantener antes de ese punto.

La forma y escala de Weibull `(β, η)` se estiman por momentos (CV ↔ β,
η = media / Γ(1 + 1/β)) a partir del historial ficticio del sensor: los
intervalos en días entre lecturas anómalas. Si el historial es escaso se
usan parámetros por defecto y se reporta `parameters_estimated=false`.

Endpoint (recibe `sensor_id` en el path; los costos son opcionales):

```bash
curl -X POST http://localhost:8000/api/v1/maintenance/sensors/SENSOR-001/schedule \
  -H "Content-Type: application/json" \
  -d '{"preventive_cost": 1000, "failure_cost": 20000, "min_window_days": 0.5, "max_window_days": 365}'
```

Respuesta: `recommended_window_days` (ventana óptima), costos esperados por
día (planificado / no planificado / total), la probabilidad de falla en esa
ventana, los parámetros Weibull usados y el `config_used`.

El cálculo vive en `app/domains/maintenance_scheduler/service.py`
(lógica pura, sin dependencias de FastAPI), los datos se leen a través de
`MaintenanceRepository`, y el endpoint solo mapea excepciones de dominio a
HTTP.

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
