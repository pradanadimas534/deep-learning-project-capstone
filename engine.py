import os
import numpy as np
import tensorflow as tf
import pickle

class ModelHandler:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        # GUNAKAN PATH BARU DI DOCUMENTS (Ganti 'NamaUserAnda')
        self.base_path = r'C:\Users\dimas\Documents\Code\Codding\deep-learning-project-capstone\model'
        self.model_path = os.path.join(self.base_path, 'model.keras')
        self.encoder_path = os.path.join(self.base_path, 'label_encoder.pkl')

    def load_components(self):
        try:
            print(f"⏳ Mencoba memuat komponen dari lokasi baru...")
            
            # Memuat folder model (SavedModel format)
            # Menggunakan direktori langsung seringkali melewati proteksi file tunggal di Windows
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
            
            with open(self.encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            print("✅ AI Components Loaded Successfully!")
            return True
        except Exception as e:
            print(f"❌ Error fatal: {e}")
            return False

    def predict(self, text_cv: str):
        if self.model is None:
            raise Exception("Model is not initialized")
        
        # Prediksi teks CV
        prediction = self.model.predict(np.array([text_cv]))
        idx = np.argmax(prediction, axis=1)[0]
        confidence = float(np.max(prediction))
        label = self.label_encoder.inverse_transform([idx])[0]
        
        return {
            "recommendation": str(label),
            "confidence": round(confidence, 4),
            "status": "success"
        }

handler = ModelHandler()