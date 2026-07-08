# -*- coding: utf-8 -*-
import tensorflow as tf
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_yolu  = os.path.join(BASE_DIR, "yaprak_nir_modeli.h5")
cikis_yolu  = os.path.join(BASE_DIR, "yaprak_nir_modeli_mobil.tflite")

model = tf.keras.models.load_model(model_yolu, compile=False)

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open(cikis_yolu, "wb") as f:
    f.write(tflite_model)

print("NIR TFLite boyutu : %.1f KB" % (os.path.getsize(cikis_yolu) / 1024))
print("Kaydedildi        : %s" % cikis_yolu)
