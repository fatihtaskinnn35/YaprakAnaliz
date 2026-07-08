# -*- coding: utf-8 -*-
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import os
import random

# 1. Modeli Yukle
model = tf.keras.models.load_model('yaprak_analiz_modeli.h5')
print("Model basariyla yuklendi.")

# 2. Rastgele bir test resmi sec
base_path = "dataset_balanced/apple/diseased" # Elma klasorunden ornek aliyoruz
if not os.path.exists(base_path):
    print("Hata: Klasor yolu bulunamadi! Klasor adini kontrol et.")
else:
    dosyalar = [f for f in os.listdir(base_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    secilen_resim = random.choice(dosyalar) # Klasordeki resimlerden birini rastgele secer
    test_img_yolu = os.path.join(base_path, secilen_resim)
    print("Test edilen resim: " + test_img_yolu)

    # 3. Resmi Oku ve Tahmin Et
    with open(test_img_yolu, "rb") as f:
        img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
    
    img_res = cv2.resize(img, (256, 256))
    img_input = np.expand_dims(img_res / 255.0, axis=0)
    prediction = model.predict(img_input)[0]
    mask = (prediction > 0.5).astype(np.uint8)

    # 4. Sonuclari Goster
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title("Orijinal Yaprak")
    plt.imshow(cv2.cvtColor(img_res, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.title("Modelin Hastalik Tahmini")
    plt.imshow(mask.squeeze(), cmap='gray')
    plt.axis('off')
    
    plt.show()