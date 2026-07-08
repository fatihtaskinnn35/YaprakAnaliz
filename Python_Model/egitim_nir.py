# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

# --- AYARLAR ---
IMG_SIZE = 256
BATCH_SIZE = 8
EPOCHS = 10 # NIR tahmini icin 10 tur genellikle yeterlidir

def build_nir_model():
    # Girdi: RGB (3 kanal), Cikti: NIR (1 kanal - Gri tonlama)
    inputs = layers.Input((IMG_SIZE, IMG_SIZE, 3))
    
    # Basit ve etkili bir donusturucu mimari
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = layers.UpSampling2D((2, 2))(x)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    
    # Son katman: Tek kanal (Pseudo-NIR)
    outputs = layers.Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)
    
    model = models.Model(inputs, outputs)
    model.compile(optimizer='adam', loss='mse') # Sayisal tahmin oldugu icin MSE kullanilir
    return model

def load_nir_data():
    images_rgb = []
    images_nir = []
    # Tum kategorilerden veri toplayalim
    categories = ["apple", "corn", "grape"]
    
    print("NIR egitimi icin veriler hazirlaniyor...")
    for cat in categories:
        path = os.path.join("dataset_balanced", cat, "diseased")
        if not os.path.exists(path): continue
        
        files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.png'))][:200]
        
        for file in files:
            full_path = os.path.join(path, file)
            with open(full_path, "rb") as f:
                img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
            
            if img is not None:
                img_res = cv2.resize(img, (IMG_SIZE, IMG_SIZE)) / 255.0
                # Bilimsel yaklasim: Bitkilerde NIR yansimasi en cok Green kanaliyla iliskilidir
                nir_sim = img_res[:, :, 1] * 0.9 # Yesil kanali baz alan bir NIR simulasyonu
                
                images_rgb.append(img_res)
                images_nir.append(np.expand_dims(nir_sim, axis=-1))
                
    return np.array(images_rgb), np.array(images_nir)

# --- CALISTIR ---
X, Y = load_nir_data()
model = build_nir_model()
print("\nPseudo-NIR Tahmin Modeli egitiliyor...")
model.fit(X, Y, epochs=EPOCHS, batch_size=BATCH_SIZE)

model.save("yaprak_nir_modeli.h5")
print("\nBASARILI! NIR Modeli 'yaprak_nir_modeli.h5' olarak kaydedildi.")