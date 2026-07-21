import os

import joblib
import numpy as np

FEATURE_ORDER = ["temperature", "vibration", "pressure"]


class AnomalyDetector:
    """Carga el Isolation Forest (+ scaler) entrenado y evalúa lecturas nuevas."""

    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"No se encontró el modelo en '{model_path}'. "
                "Corré primero: python scripts/train_model.py"
            )
        bundle = joblib.load(model_path)
        self.model = bundle["model"]
        self.scaler = bundle["scaler"]
        self.feature_names = bundle.get("feature_names", FEATURE_ORDER)

    def predict(self, reading: dict) -> dict:
        """
        reading: {"temperature": float, "vibration": float, "pressure": float}
        return: {"prediction": 1|-1, "is_anomaly": bool, "anomaly_score": float}
        """
        vector = np.array([[reading[f] for f in self.feature_names]])
        vector_scaled = self.scaler.transform(vector)

        prediction = int(self.model.predict(vector_scaled)[0]) 
        # decision_function: valores negativos indican mayor anormalidad
        score = float(self.model.decision_function(vector_scaled)[0])

        return {
            "prediction": prediction,
            "is_anomaly": prediction == -1,
            "anomaly_score": round(score, 5),
        }
