# Industrial Monitoring System

Sistema de monitoreo industrial en tiempo real para supervisar variables de sensores, detectar anomalías mediante inteligencia artificial y visualizar la información en un dashboard web.

El sistema está compuesto por un backend encargado del procesamiento de datos, un frontend para visualización y un simulador de sensores para generar telemetría industrial.

---

## Arquitectura

El proyecto está dividido en tres módulos principales:

### Backend

API encargada de:

- Recepción de datos de sensores mediante MQTT.
- Procesamiento y almacenamiento de mediciones.
- Detección de anomalías mediante Machine Learning.
- Comunicación en tiempo real mediante WebSocket.
- Gestión de alertas.

Ver documentación:
`backend/README.md`

---

### Frontend

Dashboard web encargado de:

- Visualización de telemetría en tiempo real.
- Gráficos de sensores.
- Consulta de históricos y estadísticas.
- Estado del sistema.

Ver documentación:
`frontend/README.md`

---

### Simulator

Simulador de dispositivos industriales encargado de:

- Generar datos de sensores.
- Enviar telemetría al backend mediante MQTT.
- Simular condiciones normales y fallas.

---

## Tecnologías principales

### Backend
- Python
- FastAPI
- MQTT (Mosquitto)
- PostgreSQL
- Scikit-learn
- Docker

### Frontend
- React
- Vite
- CSS Modules
- WebSocket

### Comunicación
- MQTT
- REST API
- WebSocket

---

## Instalación rápida

Clonar el repositorio:

```bash
git clone <url-del-repositorio>

cd IndustrialMonitoring
```

Cada módulo posee su propia configuración e instrucciones de instalación:

Backend:

```bash
cd backend
```

Frontend:

```bash
cd frontend
```

Simulator:

```bash
cd simulator
```

Consultar el README correspondiente para los pasos completos.

---

## Requisitos

Antes de ejecutar el sistema se necesita:

- Python 3.10+
- Node.js y npm
- Docker
- Broker MQTT Mosquitto
- PostgreSQL

---

## Ejecución completa

Orden recomendado:

1. Levantar servicios externos:

```bash
docker compose up -d
```

2. Iniciar backend:

```bash
cd backend
```

3. Iniciar simulador:

```bash
cd simulator
```

4. Iniciar frontend:

```bash
cd frontend
```

---

## Estado del proyecto

Actualmente incluye:

- Recepción de telemetría industrial.
- Dashboard en tiempo real.
- Persistencia de mediciones.
- Detección de anomalías con IA.
- Comunicación mediante WebSocket.
- Simulación de fallas.

---

## Licencia

Este proyecto está bajo la licencia MIT.
