import os
import numpy as np
import tensorflow as tf
import pickle

class ModelHandler:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        # Menggunakan path relatif sederhana
        self.model_path = 'model/model.keras'
        self.encoder_path = 'model/label_encoder.pkl'

    def load_components(self):
        try:
            print(f"⏳ Mencoba memuat model dari: {self.model_path}")
            
            # Memuat model secara langsung
            # compile=False tetap disarankan agar tidak error saat pemuatan di Windows
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
            
            # Memuat label encoder
            with open(self.encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            print("✅ AI Components Loaded Successfully!")
            return True
        except Exception as e:
            print(f"❌ Gagal memuat komponen: {e}")
            return False

    def predict(self, text_cv: str):
        if self.model is None:
            raise Exception("Model belum dimuat!")
        
        # Prediksi teks CV
        prediction = self.model.predict(np.array([text_cv]))
        idx = np.argmax(prediction, axis=1)[0]
        label = self.label_encoder.inverse_transform([idx])[0]
        confidence = float(np.max(prediction))
        
        return {
            "recommendation": str(label),
            "confidence": round(confidence, 4),
            "status": "success"
        }

handler = ModelHandler()