# -*- coding: utf-8 -*-
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import os
import random

# 1. Modeli Yukle
model = tf.keras.models.load_model('yaprak_analiz_modeli.h5')

# 2. Kategoriler ve Yollar
categories = ["apple", "corn", "grape"]
base_path = "dataset_balanced"

plt.figure(figsize=(15, 10))

for i, cat in enumerate(categories):
    img_dir = os.path.join(base_path, cat, "diseased")
    
    if os.path.exists(img_dir):
        # Rastgele resim sec
        files = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        secilen = random.choice(files)
        yol = os.path.join(img_dir, secilen)
        
        # Oku ve Tahmin Et
        with open(yol, "rb") as f:
            img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
        
        img_res = cv2.resize(img, (256, 256))
        input_data = np.expand_dims(img_res / 255.0, axis=0)
        mask = model.predict(input_data)[0]
        mask = (mask > 0.5).astype(np.uint8)

        # Gorsellestir
        # Orijinal resimler ustte
        plt.subplot(2, 3, i + 1)
        plt.title(cat.capitalize() + " (Orijinal)")
        plt.imshow(cv2.cvtColor(img_res, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        
        # Tahmin maskeleri altta
        plt.subplot(2, 3, i + 4)
        plt.title(cat.capitalize() + " (Tahmin)")
        plt.imshow(mask.squeeze(), cmap='gray')
        plt.axis('off')

print("3 farkli tur icin analiz yapiliyor...")
plt.tight_layout()
plt.show()