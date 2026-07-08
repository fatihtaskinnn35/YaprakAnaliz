# -*- coding: utf-8 -*-
import cv2
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Her kategori icin hastalik renk araliklari (HSV uzayi)
# Mevcut maskesi olan goruntuleri atliyoruz — sadece eksik olanlari uretiyoruz
HASTALIK_RENK_ARALIKLARI = {
    # Elma: kahverengi, sari, koyu leke
    "apple": [
        (np.array([10, 30, 30]),  np.array([30, 255, 255])),   # Sari-kahverengi
        (np.array([0,  30, 30]),  np.array([10, 255, 255])),   # Koyu kirmizi-kahve
        (np.array([170,30, 30]),  np.array([180,255, 255])),   # Kirmizimsi ton
    ],
    # Misir (corn): gri-kahve pas lekeleri, sari
    "corn": [
        (np.array([10, 20, 20]),  np.array([30, 255, 255])),   # Sari-kahve
        (np.array([0,  10, 50]),  np.array([15, 180, 200])),   # Pas tonu (dusuk doygunluk)
    ],
    # Uzum: koyu kahve, siyahimsi urup lekeleri
    "grape": [
        (np.array([10, 30, 20]),  np.array([30, 255, 255])),   # Sari-kahve
        (np.array([0,  20, 20]),  np.array([15, 255, 180])),   # Koyu kahve
        (np.array([100,30, 20]),  np.array([130,255, 150])),   # Morumsu pas
    ],
}


def _hastalik_maskesi_olustur(img, kategori):
    """
    Birden fazla renk araligini birlestirir.
    Sonunda morfolojik temizleme yaparak gurultuyu azaltir.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    aralıklar = HASTALIK_RENK_ARALIKLARI.get(kategori, HASTALIK_RENK_ARALIKLARI["apple"])

    birlesik_maske = np.zeros(img.shape[:2], dtype=np.uint8)
    for alt, ust in aralıklar:
        birlesik_maske = cv2.bitwise_or(birlesik_maske, cv2.inRange(hsv, alt, ust))

    # Morfolojik islemler: kucuk gurultuyu sil, buyuk lekeleri birlestir
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    birlesik_maske = cv2.morphologyEx(birlesik_maske, cv2.MORPH_OPEN,  kernel, iterations=1)
    birlesik_maske = cv2.morphologyEx(birlesik_maske, cv2.MORPH_CLOSE, kernel, iterations=2)

    return birlesik_maske


def create_masks(sadece_eksik=True):
    """
    sadece_eksik=True: zaten maskesi olan goruntuleri atlar (mevcut maskeleri bozmaz)
    sadece_eksik=False: tum maskeleri yeniden olusturur
    """
    dataset_path = os.path.join(BASE_DIR, "dataset_balanced")
    categories = ["apple", "corn", "grape"]

    for cat in categories:
        img_dir  = os.path.join(dataset_path, cat, "diseased")
        mask_dir = os.path.join(dataset_path, "masks", cat)

        if not os.path.exists(img_dir):
            print(f"Klasor bulunamadi: {img_dir}")
            continue

        os.makedirs(mask_dir, exist_ok=True)
        dosyalar = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        islenen = 0
        atlanan = 0
        for img_name in dosyalar:
            save_path = os.path.join(mask_dir, img_name)

            if sadece_eksik and os.path.exists(save_path):
                atlanan += 1
                continue

            img_path = os.path.join(img_dir, img_name)
            try:
                with open(img_path, "rb") as f:
                    img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
            except Exception:
                continue

            if img is None:
                continue

            maske = _hastalik_maskesi_olustur(img, cat)

            is_ok, buffer = cv2.imencode(".jpg", maske)
            if is_ok:
                with open(save_path, "wb") as f:
                    f.write(buffer)
                islenen += 1

        print(f"{cat}: {islenen} maske olusturuldu, {atlanan} mevcut maske atlatildi.")

    print("\nISLEM TAMAM!")


if __name__ == "__main__":
    # Sadece maskesi olmayan goruntuleri isle (mevcut maskelere dokunma)
    create_masks(sadece_eksik=True)
