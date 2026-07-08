# -*- coding: utf-8 -*-
import tensorflow as tf
import numpy as np
import os

# 1. Mevcut Modeli Yukle
model_yolu = 'yaprak_analiz_modeli.h5'
model = tf.keras.models.load_model(model_yolu, compile=False)

# 2. TFLite Donusturucu (Converter) Ayarlari
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# 3. INT8 Quantization (Kuantizasyon) Islemi
# Bu islem model boyutunu yaklasik 4 kat kucultur
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# 4. Donusturme
tflite_model = converter.convert()

# 5. Kaydet
tflite_model_yolu = 'yaprak_modeli_mobil.tflite'
with open(tflite_model_yolu, 'wb') as f:
    f.write(tflite_model)

print("-" * 30)
print(f"MODEL BASARIYLA OPTIMIZE EDILDI!")
print(f"Orijinal Model (.h5): {os.path.getsize(model_yolu) / 1024:.2f} KB")
print(f"Mobil Model (.tflite): {os.path.getsize(tflite_model_yolu) / 1024:.2f} KB")
print("-" * 30)