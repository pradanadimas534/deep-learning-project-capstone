import tensorflow as tf
import pickle
import re
import numpy as np


class InferenceEngine:
    def __init__(self):
        # load model
        self.model = tf.keras.models.load_model("model/model.keras")

        # load label encoder
        with open("model/label_encoder.pkl", "rb") as f:
            self.encoder = pickle.load(f)

    # =====================
    # CLEAN TEXT (optional)
    # =====================
    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9 ]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    # =====================
    # PREDICT TOP N
    # =====================
    def predict(self, text, top_n=3):
        text = self.clean_text(text)

        # model langsung terima text
        preds = self.model.predict([text])[0]

        # ambil top N
        top_indices = np.argsort(preds)[-top_n:][::-1]

        results = []
        for idx in top_indices:
            job = self.encoder.inverse_transform([idx])[0]
            score = float(preds[idx])

            results.append({
                "job_title": job,
                "confidence": round(score, 4)
            })

        return results