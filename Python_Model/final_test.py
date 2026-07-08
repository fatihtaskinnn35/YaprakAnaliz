# -*- coding: utf-8 -*-
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Modelleri Yukle
try:
    seg_model = tf.keras.models.load_model(os.path.join(BASE_DIR, "yaprak_analiz_modeli.h5"), compile=False)
    nir_model = tf.keras.models.load_model(os.path.join(BASE_DIR, "yaprak_nir_modeli.h5"), compile=False)
    print("Modeller basariyla yuklendi!")
except Exception as e:
    print("Hata: " + str(e))

# 2. Rastgele Resim Sec
categories = ["apple", "corn", "grape"]
cat = random.choice(categories)
base_path = os.path.join(BASE_DIR, "dataset_balanced", cat, "diseased")
files = [f for f in os.listdir(base_path) if f.lower().endswith(('.jpg', '.png'))]
test_img_yolu = os.path.join(base_path, random.choice(files))

# 3. Hazirlik ve Tahmin
with open(test_img_yolu, "rb") as f:
    img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)

img_res = cv2.resize(img, (256, 256))
img_input = np.expand_dims(img_res / 255.0, axis=0)

mask = seg_model.predict(img_input)[0]
mask = (mask > 0.5).astype(np.uint8)
pseudo_nir = nir_model.predict(img_input)[0]

# --- YENI: Hastalik Siddeti Hesaplama ---
toplam_piksel = mask.size
hastali_piksel = np.sum(mask == 1)
hastalik_yuzdesi = (hastali_piksel / toplam_piksel) * 100
# ----------------------------------------

# 4. Gorsellestirme
plt.figure(figsize=(15, 6))

plt.subplot(1, 3, 1)
plt.title("Orijinal RGB (" + cat.capitalize() + ")")
plt.imshow(cv2.cvtColor(img_res, cv2.COLOR_BGR2RGB))
plt.axis('off')

plt.subplot(1, 3, 2)
# Basligi dinamik hale getirdik
plt.title("Segmentasyon\nHastalik Siddeti: %{:.2f}".format(hastalik_yuzdesi))
plt.imshow(mask.squeeze(), cmap='gray')
plt.axis('off')

plt.subplot(1, 3, 3)
plt.title("Tahmini Pseudo-NIR\n(Bitki Saglik Haritasi)")
plt.imshow(pseudo_nir.squeeze(), cmap='inferno')
plt.axis('off')

print("-" * 30)
print(f"ANALIZ SONUCU ({cat.upper()})")
print(f"Saptanan Hastalik Alani: %{hastalik_yuzdesi:.2f}")
print("-" * 30)

plt.tight_layout()
plt.show()