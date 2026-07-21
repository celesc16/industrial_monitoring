"""
Entrena un Isolation Forest con datos normales simulados de los cinco
sensores de la planta y guarda:

- modelo
- scaler
- orden de variables
- umbral calibrado

Ruta de salida:
    app/ml/artifacts/model.pkl

Uso desde backend/:
    python scripts/train_model.py

En un sistema real, los datos simulados se reemplazarían por lecturas
históricas reales obtenidas desde la base de datos o archivos CSV.
"""

import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.core.config import settings
from app.services.ml_model import FEATURE_ORDER


RANDOM_STATE = 42

N_TRAIN_PER_SENSOR = 6000
N_VALIDATION_PER_SENSOR = 3000
N_FAULTS_PER_SENSOR = 1000

# Tasa objetivo de falsos positivos sobre datos normales.
# 0.001 equivale aproximadamente a 0,1 %.
TARGET_FALSE_POSITIVE_RATE = 0.001


SENSOR_PROFILES = [
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


def generate_normal_data(
    samples_per_sensor: int,
    seed: int,
) -> np.ndarray:
    """
    Genera lecturas normales para cada perfil de sensor.
    """
    rng = np.random.default_rng(seed)
    datasets = []

    for profile in SENSOR_PROFILES:
        temperature = rng.normal(
            loc=profile["temperature_mean"],
            scale=profile["temperature_std"],
            size=samples_per_sensor,
        )

        vibration = rng.normal(
            loc=profile["vibration_mean"],
            scale=profile["vibration_std"],
            size=samples_per_sensor,
        )

        vibration = np.maximum(vibration, 0)

        pressure = rng.normal(
            loc=profile["pressure_mean"],
            scale=profile["pressure_std"],
            size=samples_per_sensor,
        )

        sensor_data = np.column_stack(
            [
                temperature,
                vibration,
                pressure,
            ]
        )

        datasets.append(sensor_data)

    return np.vstack(datasets)


def generate_fault_data(
    samples_per_sensor: int,
    seed: int,
) -> np.ndarray:
    """
    Genera fallas artificiales usando los mismos rangos que el simulador.
    Se utiliza únicamente para comprobar la calidad del modelo.
    """
    rng = np.random.default_rng(seed)
    datasets = []

    for profile in SENSOR_PROFILES:
        temperature = rng.uniform(
            profile["temperature_mean"] + 25,
            profile["temperature_mean"] + 40,
            size=samples_per_sensor,
        )

        vibration = rng.uniform(
            profile["vibration_mean"] + 2.5,
            profile["vibration_mean"] + 4.0,
            size=samples_per_sensor,
        )

        pressure = rng.uniform(
            profile["pressure_mean"] + 25,
            profile["pressure_mean"] + 50,
            size=samples_per_sensor,
        )

        fault_data = np.column_stack(
            [
                temperature,
                vibration,
                pressure,
            ]
        )

        datasets.append(fault_data)

    return np.vstack(datasets)


def main() -> None:
    print("Generando datos normales de entrenamiento...")

    training_data = generate_normal_data(
        samples_per_sensor=N_TRAIN_PER_SENSOR,
        seed=RANDOM_STATE,
    )

    print(
        f"Lecturas normales de entrenamiento: "
        f"{len(training_data)}"
    )

    print("Generando datos normales de validación...")

    validation_data = generate_normal_data(
        samples_per_sensor=N_VALIDATION_PER_SENSOR,
        seed=RANDOM_STATE + 1,
    )

    scaler = StandardScaler()

    training_scaled = scaler.fit_transform(
        training_data
    )

    validation_scaled = scaler.transform(
        validation_data
    )

    print("Entrenando Isolation Forest...")

    model = IsolationForest(
        n_estimators=300,
        contamination="auto",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    model.fit(training_scaled)

    # Calculamos los scores sobre datos normales que el modelo
    # no utilizó durante el entrenamiento.
    validation_scores = model.decision_function(
        validation_scaled
    )

    # El percentil más bajo de los scores normales se utiliza
    # como umbral de anomalía.
    anomaly_threshold = float(
        np.quantile(
            validation_scores,
            TARGET_FALSE_POSITIVE_RATE,
        )
    )

    normal_predictions = (
        validation_scores < anomaly_threshold
    )

    observed_false_positive_rate = float(
        normal_predictions.mean()
    )

    print(
        "Umbral calibrado:",
        round(anomaly_threshold, 6),
    )

    print(
        "Tasa de falsas anomalías sobre validación normal:",
        f"{observed_false_positive_rate * 100:.4f}%",
    )

    print("Generando fallas artificiales para validar...")

    fault_data = generate_fault_data(
        samples_per_sensor=N_FAULTS_PER_SENSOR,
        seed=RANDOM_STATE + 2,
    )

    fault_scaled = scaler.transform(fault_data)

    fault_scores = model.decision_function(
        fault_scaled
    )

    detected_faults = (
        fault_scores < anomaly_threshold
    )

    fault_detection_rate = float(
        detected_faults.mean()
    )

    print(
        "Tasa de detección de fallas artificiales:",
        f"{fault_detection_rate * 100:.2f}%",
    )

    bundle = {
        "model": model,
        "scaler": scaler,
        "feature_names": FEATURE_ORDER,
        "anomaly_threshold": anomaly_threshold,
        "target_false_positive_rate": (
            TARGET_FALSE_POSITIVE_RATE
        ),
        "sensor_profiles": SENSOR_PROFILES,
    }

    output_path = Path(settings.model_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(bundle, output_path)

    print(f"Modelo guardado en: {output_path}")

    # Prueba rápida con una lectura normal.
    normal_example = np.array(
        [[60.0, 1.5, 100.0]]
    )

    normal_score = float(
        model.decision_function(
            scaler.transform(normal_example)
        )[0]
    )

    print(
        "Prueba normal:",
        {
            "score": round(normal_score, 5),
            "is_anomaly": (
                normal_score < anomaly_threshold
            ),
        },
    )

    # Prueba rápida con una lectura claramente anómala.
    fault_example = np.array(
        [[95.0, 4.8, 140.0]]
    )

    fault_score = float(
        model.decision_function(
            scaler.transform(fault_example)
        )[0]
    )

    print(
        "Prueba anómala:",
        {
            "score": round(fault_score, 5),
            "is_anomaly": (
                fault_score < anomaly_threshold
            ),
        },
    )


if __name__ == "__main__":
    main()