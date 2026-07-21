# Frontend — Dashboard de Monitoreo Industrial

React + Vite. Se conecta al backend por WebSocket (telemetría en vivo) y
REST (histórico y estadísticas).

## Estructura

Cada componente vive en su propia carpeta junto con su hoja de estilos
(**CSS Modules**), así el CSS queda aislado por componente y no se
filtra ni colisiona con el de otros. `pages/` arma el layout combinando
componentes.

## 1. Instalar dependencias

```bash
cd frontend
npm install
```

## 2. Configurar variables de entorno

```bash
cp .env_example .env
```

Por defecto apunta a `http://localhost:8000` / `ws://localhost:8000/ws`.
Cambiá esto si tu backend corre en otro host/puerto.

## 3. Levantar en desarrollo

```bash
npm run dev
```

Abrí **http://localhost:5173**. Con el backend corriendo (ver
`backend/README.md`) y el simulador publicando datos, se va a ver la
telemetría entrar en vivo al osciloscopio.

Si todavía no se tiene Mosquitto/simulador levantado, se puede generar datos
igual pegándole al backend directamente:

```bash
curl -X POST http://localhost:8000/api/v1/simulate \
  -H "Content-Type: application/json" \
  -d '{"sensor_id": "1", "temperature": 92, "vibration": 4.1, "pressure": 145}'
```

## 4. Build de producción

```bash
npm run build
npm run preview  
```
