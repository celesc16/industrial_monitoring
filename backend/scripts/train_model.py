"""
Entrena un Isolation Forest con datos "normales" simulados de la planta
y guarda el modelo + el scaler en app/ml/artifacts/model.pkl.

En un caso real, acá cargarías tu histórico real de sensores (CSV/DB)
en vez de generar datos sintéticos.

Uso (desde la carpeta backend/):
    python scripts/train_model.py
"""

import sys
from pathlib import Path

# Permite importar el paquete `app` al correr este script directamente
sys.path.append(str(Path(__file__).resolve().parent.parent))

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.core.config import settings
from app.services.ml_model import FEATURE_ORDER

RANDOM_STATE = 42
N_SAMPLES = 5000


def generar_datos_normales(n: int) -> np.ndarray:
    rng = np.random.default_rng(RANDOM_STATE)
    # Rango operativo "normal" de la planta (ajustar a tu caso real)
    temperature = rng.normal(loc=60, scale=4, size=n)      # °C
    vibration = rng.normal(loc=1.5, scale=0.25, size=n)    # mm/s
    pressure = rng.normal(loc=100, scale=6, size=n)        # kPa
    return np.column_stack([temperature, vibration, pressure])


def main():
    print("Generando dataset de entrenamiento (operación normal)...")
    X = generar_datos_normales(N_SAMPLES)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("Entrenando Isolation Forest...")
    model = IsolationForest(
        n_estimators=150,
        contamination=0.02,  # % esperado de outliers en operación normal
        random_state=RANDOM_STATE,
    )
    model.fit(X_scaled)

    bundle = {
        "model": model,
        "scaler": scaler,
        "feature_names": FEATURE_ORDER,
    }

    output_path = Path(settings.model_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, output_path)
    print(f"Modelo guardado en {output_path}")

    # Sanity check rápido: un valor claramente anómalo debería marcar -1
    prueba_anomala = scaler.transform([[95, 4.8, 130]])
    print("Predicción sobre lectura anómala de prueba:", model.predict(prueba_anomala))


if __name__ == "__main__":
    main()
