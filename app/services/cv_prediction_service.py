import pickle
from typing import Tuple

import numpy as np
import tensorflow as tf

# -----------------------------------------------------------------------
# Kompatibilitas Keras 2.x (TF 2.13, Python 3.10) vs Keras 3.x (TF 2.16+)
# - Keras 3.x  : import keras → keras.saving.register_keras_serializable
# - Keras 2.x  : bundled di tf.keras → tf.keras.utils.register_keras_serializable
# -----------------------------------------------------------------------
try:
    import keras
    register_serializable = keras.saving.register_keras_serializable
    KerasLayer = keras.layers.Layer
    KerasDense = keras.layers.Dense
    KerasLayerNorm = keras.layers.LayerNormalization
    KerasActivation = keras.layers.Activation
    KerasAdd = keras.layers.Add
except (ImportError, AttributeError):
    keras = tf.keras  # type: ignore[assignment]
    register_serializable = tf.keras.utils.register_keras_serializable
    KerasLayer = tf.keras.layers.Layer
    KerasDense = tf.keras.layers.Dense
    KerasLayerNorm = tf.keras.layers.LayerNormalization
    KerasActivation = tf.keras.layers.Activation
    KerasAdd = tf.keras.layers.Add

from app.core.config import settings

# -----------------------------------------------------------------------
# Patch kompatibilitas: strip 'quantization_config' dari semua layer.
# Field ini ada di model yang disimpan dengan Keras versi lebih baru.
# -----------------------------------------------------------------------
_original_layer_from_config = KerasLayer.from_config.__func__


@classmethod  # type: ignore[misc]
def _patched_layer_from_config(cls, config):
    config.pop("quantization_config", None)
    return _original_layer_from_config(cls, config)


KerasLayer.from_config = _patched_layer_from_config
# -----------------------------------------------------------------------


# -----------------------------------------------------------------------
# CustomResidualBlock - direkonstruksi dari config model.keras
# Block 1: units=64, input=64  -> tanpa projection
# Block 2: units=32, input=64  -> pakai projection
# -----------------------------------------------------------------------
@register_serializable(package="Custom")
class CustomResidualBlock(KerasLayer):
    """
    Arsitektur:
        dense1 (ReLU) -> dense2 -> LayerNorm -> Add(shortcut) -> ReLU
    Projection layer dibuat otomatis jika input_dim != units.
    """

    def __init__(self, units: int, **kwargs):
        super().__init__(**kwargs)
        self.units = units
        self.dense1 = KerasDense(units, activation="relu", name="dense1")
        self.dense2 = KerasDense(units, name="dense2")
        self.layer_norm = KerasLayerNorm(name="layer_norm")
        self.projection_layer = None
        self.activation = KerasActivation("relu", name="activation")
        self.add_layer = KerasAdd()

    def build(self, input_shape):
        input_dim = input_shape[-1]
        if input_dim != self.units:
            self.projection_layer = KerasDense(self.units, name="projection_layer")
        super().build(input_shape)

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        x = self.layer_norm(x)
        shortcut = self.projection_layer(inputs) if self.projection_layer else inputs
        return self.activation(self.add_layer([x, shortcut]))

    def get_config(self):
        config = super().get_config()
        config["units"] = self.units
        return config


class CVPredictionService:
    """
    Service prediksi kategori pekerjaan dari teks CV (plain text).
    Model & encoder dimuat sekali saat startup (pola singleton).
    """

    _model = None
    _encoder = None

    @classmethod
    def load_model(cls) -> None:
        """
        Memuat model TensorFlow dan encoder LabelEncoder dari disk.
        Dipanggil sekali saat aplikasi startup.
        """
        if cls._model is None or cls._encoder is None:
            print(f"[INFO] Memuat model dari   : {settings.MODEL_PATH}")
            cls._model = tf.keras.models.load_model(
                settings.MODEL_PATH,
                custom_objects={"CustomResidualBlock": CustomResidualBlock},
            )

            print(f"[INFO] Memuat encoder dari : {settings.ENCODER_PATH}")
            with open(settings.ENCODER_PATH, "rb") as f:
                cls._encoder = pickle.load(f)

            print("[INFO] Model & Encoder berhasil dimuat.")

    @classmethod
    def predict(cls, teks_cv: str) -> Tuple[str, float]:
        """
        Memprediksi kategori pekerjaan dari string teks CV.

        Args:
            teks_cv: Isi teks CV sebagai plain string.

        Returns:
            Tuple[kategori: str, confidence_persen: float]

        Raises:
            RuntimeError : Model belum dimuat.
            ValueError   : Teks CV kosong.
        """
        if cls._model is None or cls._encoder is None:
            raise RuntimeError(
                "Model belum dimuat. Pastikan load_model() dipanggil saat startup."
            )

        teks_bersih = teks_cv.strip()
        if not teks_bersih:
            raise ValueError("Teks CV tidak boleh kosong.")

        input_tensor = tf.constant([teks_bersih], dtype=tf.string)
        probabilitas = cls._model.predict(input_tensor, verbose=0)

        indeks_tertinggi = int(np.argmax(probabilitas, axis=1)[0])
        kategori = cls._encoder.inverse_transform([indeks_tertinggi])[0]
        confidence = float(probabilitas[0][indeks_tertinggi] * 100)

        return kategori, confidence
