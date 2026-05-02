import re
import pickle
import os
import tensorflow as tf

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class InferenceEngine:
    def __init__(self):
        # TRUE = dummy (TF-IDF)
        # FALSE = pakai TensorFlow model
        self.use_dummy = True

        # load model kalau pakai real model
        if not self.use_dummy:
            self.model = tf.keras.models.load_model("models/model_job_tf")

            with open("models/vectorizer.pkl", "rb") as f:
                self.vectorizer = pickle.load(f)

            with open("models/label_encoder.pkl", "rb") as f:
                self.encoder = pickle.load(f)

    # =====================
    # CLEAN TEXT
    # =====================
    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9 ]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    # =====================
    # MAIN PREDICT
    # =====================
    def predict(self, cv_text, jobs_db):
        if self.use_dummy:
            return self._dummy_predict(cv_text, jobs_db)
        else:
            return self._real_predict(cv_text)

    # =====================
    # DUMMY (TF-IDF)
    # =====================
    def _dummy_predict(self, cv_text, jobs_db):
        cv_text = self.clean_text(cv_text)

        job_desc = [j["desc"] for j in jobs_db]
        texts = [cv_text] + job_desc

        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform(texts)

        cv_vec = tfidf[0:1]
        job_vecs = tfidf[1:]

        scores = cosine_similarity(cv_vec, job_vecs).flatten()

        results = []
        for i, score in enumerate(scores):
            results.append({
                "job_title": jobs_db[i]["title"],
                "score": round(float(score) * 100, 2)
            })

        return sorted(results, key=lambda x: x["score"], reverse=True)

    # =====================
    # REAL MODEL (TensorFlow)
    # =====================
    def _real_predict(self, cv_text):
        text = self.clean_text(cv_text)

        vec = self.vectorizer.transform([text]).toarray()
        pred = self.model.predict(vec)

        index = pred.argmax()
        job = self.encoder.inverse_transform([index])[0]

        return [{
            "job_title": job,
            "score": round(float(pred.max() * 100), 2)
        }]