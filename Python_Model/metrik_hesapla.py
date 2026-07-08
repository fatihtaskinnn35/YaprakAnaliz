# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_SIZE  = 256
ESIK      = 0.5   # Segmentasyon karari icin sigmoid esigi


def goruntu_oku(yol):
    with open(yol, "rb") as f:
        return cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)


def maske_oku(yol):
    with open(yol, "rb") as f:
        return cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_GRAYSCALE)


def iou_hesapla(gercek, tahmin):
    kesisim = np.logical_and(gercek, tahmin).sum()
    birlesim = np.logical_or(gercek, tahmin).sum()
    return kesisim / birlesim if birlesim > 0 else 1.0


def dice_hesapla(gercek, tahmin):
    kesisim = np.logical_and(gercek, tahmin).sum()
    toplam   = gercek.sum() + tahmin.sum()
    return (2 * kesisim) / toplam if toplam > 0 else 1.0


def degerlendir(model_yolu, max_goruntu=None):
    print(f"\nModel yukleniyor: {model_yolu}")
    model = tf.keras.models.load_model(model_yolu, compile=False)

    dataset_path = os.path.join(BASE_DIR, "dataset_balanced")
    categories   = ["apple", "corn", "grape"]

    tum_iou   = []
    tum_dice  = []
    kategori_sonuclar = {}

    for cat in categories:
        img_dir  = os.path.join(dataset_path, cat, "diseased")
        mask_dir = os.path.join(dataset_path, "masks", cat)

        if not os.path.exists(img_dir) or not os.path.exists(mask_dir):
            print(f"  [{cat}] Klasor bulunamadi, atlaniyor.")
            continue

        dosyalar = [f for f in os.listdir(mask_dir)
                    if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                    and os.path.exists(os.path.join(img_dir, f))]

        if max_goruntu:
            dosyalar = dosyalar[:max_goruntu]

        cat_iou  = []
        cat_dice = []

        for dosya in dosyalar:
            img  = goruntu_oku(os.path.join(img_dir,  dosya))
            mask = maske_oku( os.path.join(mask_dir, dosya))

            if img is None or mask is None:
                continue

            img_res   = cv2.resize(img,  (IMG_SIZE, IMG_SIZE)) / 255.0
            mask_bin  = (cv2.resize(mask, (IMG_SIZE, IMG_SIZE)) > 127).astype(np.uint8)

            inp       = np.expand_dims(img_res, axis=0)
            pred      = model.predict(inp, verbose=0)[0]
            pred_bin  = (pred.squeeze() > ESIK).astype(np.uint8)

            cat_iou.append( iou_hesapla( mask_bin, pred_bin))
            cat_dice.append(dice_hesapla(mask_bin, pred_bin))

        if cat_iou:
            ort_iou  = np.mean(cat_iou)
            ort_dice = np.mean(cat_dice)
            kategori_sonuclar[cat] = {"IoU": ort_iou, "Dice": ort_dice, "n": len(cat_iou)}
            tum_iou.extend(cat_iou)
            tum_dice.extend(cat_dice)
            print(f"  [{cat}] n={len(cat_iou):4d}  IoU={ort_iou:.4f}  Dice={ort_dice:.4f}")

    print("\n" + "="*45)
    print(f"  GENEL SONUCLAR  (toplam {len(tum_iou)} goruntu)")
    print("="*45)
    print(f"  Mean IoU  (mIoU) : {np.mean(tum_iou):.4f}  (%{np.mean(tum_iou)*100:.1f})")
    print(f"  Mean Dice        : {np.mean(tum_dice):.4f}  (%{np.mean(tum_dice)*100:.1f})")
    print("="*45)

    return {
        "mIoU":  float(np.mean(tum_iou)),
        "mDice": float(np.mean(tum_dice)),
        "kategoriler": kategori_sonuclar,
    }


if __name__ == "__main__":
    model_yolu = os.path.join(BASE_DIR, "yaprak_analiz_modeli.h5")

    # max_goruntu=None => tum veri seti
    # max_goruntu=50   => hizli test icin her kategoriden 50 goruntu
    sonuclar = degerlendir(model_yolu, max_goruntu=None)
