import os

import joblib
import numpy as np

FEATURE_ORDER = [
    "temperature",
    "vibration",
    "pressure",
]


class AnomalyDetector:

    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"No se encontró el modelo en '{model_path}'. "
                "Corré primero: python scripts/train_model.py"
            )

        bundle = joblib.load(model_path)

        self.model = bundle["model"]
        self.scaler = bundle["scaler"]
        self.feature_names = bundle.get(
            "feature_names",
            FEATURE_ORDER,
        )

        if "anomaly_threshold" not in bundle:
            raise ValueError(
                "El modelo no contiene un umbral calibrado. "
                "Volvé a entrenarlo ejecutando: "
                "python scripts/train_model.py"
            )

        self.anomaly_threshold = float(
            bundle["anomaly_threshold"]
        )

    def predict(self, reading: dict) -> dict:
        vector = np.array(
            [
                [
                    reading[feature]
                    for feature in self.feature_names
                ]
            ],
            dtype=float,
        )

        vector_scaled = self.scaler.transform(vector)

        score = float(
            self.model.decision_function(vector_scaled)[0]
        )

        is_anomaly = score < self.anomaly_threshold
        prediction = -1 if is_anomaly else 1

        return {
            "prediction": prediction,
            "is_anomaly": is_anomaly,
            "anomaly_score": round(score, 5),
        }