# -*- coding: utf-8 -*-
import os
import random
import cv2
import json
import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use("Agg")  # Ekransiz ortamda grafik kaydetmek icin
import matplotlib.pyplot as plt
from model_unet import lightweight_unet

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
BASE_PATH  = os.path.join(BASE_DIR, "dataset_balanced")
IMG_SIZE   = 256
BATCH_SIZE = 8
EPOCHS     = 15


def kayit_listesi():
    """Tum (resim_yolu, maske_yolu) ciftlerinin listesini cikarir.
    Saglikli yapraklarda maske_yolu "" olur — egitim sirasinda bos (sifir) maske kullanilir.
    Tum goruntuleri RAM'e yuklemek yerine sadece yollari topluyoruz, asil okuma
    egitim sirasinda batch batch yapilir (veri seti RAM'e sigmayacak kadar buyuk)."""
    kayitlar = []
    categories = ["apple", "corn", "grape"]

    for cat in categories:
        img_dir  = os.path.join(BASE_PATH, cat, "diseased")
        mask_dir = os.path.join(BASE_PATH, "masks", cat)

        if os.path.exists(mask_dir):
            file_list = [f for f in os.listdir(mask_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            for file in file_list:
                img_path  = os.path.join(img_dir,  file)
                mask_path = os.path.join(mask_dir, file)
                if os.path.exists(img_path):
                    kayitlar.append((img_path, mask_path))

        # Sagikli yapraklari da bos (tamamen siyah) maskeyle egitime kat —
        # aksi halde model "hastaliksiz" gorunumu hic gormez ve saglikli
        # yapraklarda da hastalik isaretler (her seyi hastalik sanir).
        healthy_dir = os.path.join(BASE_PATH, cat, "healthy")
        if os.path.exists(healthy_dir):
            healthy_files = [f for f in os.listdir(healthy_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            for file in healthy_files:
                kayitlar.append((os.path.join(healthy_dir, file), ""))

    for cat in categories:
        diseased_dir = os.path.join(BASE_PATH, cat, "diseased")
        healthy_dir  = os.path.join(BASE_PATH, cat, "healthy")
        n_diseased = sum(1 for _ in os.listdir(diseased_dir) if _.lower().endswith(('.jpg', '.jpeg', '.png'))) if os.path.exists(diseased_dir) else 0
        n_healthy  = sum(1 for _ in os.listdir(healthy_dir)  if _.lower().endswith(('.jpg', '.jpeg', '.png'))) if os.path.exists(healthy_dir)  else 0
        print(f"  {cat:<6}: hastalikli={n_diseased}, saglikli={n_healthy}")

    random.shuffle(kayitlar)
    return kayitlar


def _resim_ve_maske_oku(img_path, mask_path):
    img_path  = img_path.numpy().decode("utf-8")
    mask_path = mask_path.numpy().decode("utf-8")

    with open(img_path, "rb") as f:
        img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE)).astype(np.float32) / 255.0

    if mask_path:
        with open(mask_path, "rb") as f:
            mask = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
        mask = cv2.resize(mask, (IMG_SIZE, IMG_SIZE)).astype(np.float32) / 255.0
    else:
        mask = np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.float32)

    return img, np.expand_dims(mask, axis=-1)


def _tf_oku(img_path, mask_path):
    img, mask = tf.py_function(_resim_ve_maske_oku, [img_path, mask_path], [tf.float32, tf.float32])
    img.set_shape((IMG_SIZE, IMG_SIZE, 3))
    mask.set_shape((IMG_SIZE, IMG_SIZE, 1))
    return img, mask


def dataset_olustur(kayitlar, egitim=True):
    img_paths  = [k[0] for k in kayitlar]
    mask_paths = [k[1] for k in kayitlar]

    ds = tf.data.Dataset.from_tensor_slices((img_paths, mask_paths))
    if egitim:
        ds = ds.shuffle(buffer_size=len(kayitlar))
    ds = ds.map(_tf_oku, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds


def grafik_kaydet(history, kayit_yolu):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(history["loss"],     label="Egitim Loss")
    axes[0].plot(history["val_loss"], label="Dogrulama Loss")
    axes[0].set_title("Loss Grafigi")
    axes[0].set_xlabel("Epoch")
    axes[0].legend()

    axes[1].plot(history["accuracy"],     label="Egitim Accuracy")
    axes[1].plot(history["val_accuracy"], label="Dogrulama Accuracy")
    axes[1].set_title("Accuracy Grafigi")
    axes[1].set_xlabel("Epoch")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(kayit_yolu, dpi=150)
    plt.close()
    print(f"Grafik kaydedildi: {kayit_yolu}")


# 1. Veri listesini cikar ve egitim/dogrulama olarak ayir
print("Veriler taraniyor...")
kayitlar = kayit_listesi()
print(f"\nToplam {len(kayitlar)} goruntu-maske cifti hazir!")

val_sayisi   = int(len(kayitlar) * 0.1)
val_kayitlar = kayitlar[:val_sayisi]
tr_kayitlar  = kayitlar[val_sayisi:]

train_ds = dataset_olustur(tr_kayitlar,  egitim=True)
val_ds   = dataset_olustur(val_kayitlar, egitim=False)

# 2. Modeli kur
model = lightweight_unet(input_shape=(IMG_SIZE, IMG_SIZE, 3))

# 3. Egitim (veri RAM'e tek seferde sigmadigi icin tf.data ile batch batch okunur)
print("\nEgitim basliyor...")
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    verbose=1
)

# 4. Modeli kaydet
model_kayit = os.path.join(BASE_DIR, "yaprak_analiz_modeli.h5")
model.save(model_kayit)
print(f"\nModel kaydedildi: {model_kayit}")

# 5. Egitim logunu JSON olarak kaydet
log_kayit = os.path.join(BASE_DIR, "egitim_logu.json")
with open(log_kayit, "w", encoding="utf-8") as f:
    json.dump(history.history, f, indent=2)
print(f"Egitim logu kaydedildi: {log_kayit}")

# 6. Loss/Accuracy grafigi kaydet
grafik_kaydet(history.history, os.path.join(BASE_DIR, "egitim_grafigi.png"))
