# -*- coding: utf-8 -*-
import os
import cv2
import random
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _oku(dosya_yolu):
    try:
        with open(dosya_yolu, "rb") as f:
            return cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
    except Exception:
        return None


def _kaydet(dosya_yolu, img):
    is_ok, buffer = cv2.imencode(".jpg", img)
    if is_ok:
        with open(dosya_yolu, "wb") as f:
            f.write(buffer)
    return is_ok


def _artir(img, islem):
    if islem == 0:
        return cv2.flip(img, 1)
    elif islem == 1:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif islem == 2:
        return cv2.rotate(img, cv2.ROTATE_180)
    elif islem == 3:
        return cv2.flip(img, 0)
    else:
        alpha = random.uniform(0.8, 1.2)
        beta = random.randint(-20, 20)
        return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)


def veri_artir(klasor_yolu, hedef_sayi=1000):
    """Tek klasor icin veri artirma (mask olmadan)."""
    if not os.path.exists(klasor_yolu):
        print(f"HATA: Klasor bulunamadi: {klasor_yolu}")
        return

    dosyalar = [f for f in os.listdir(klasor_yolu) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    mevcut_sayi = len(dosyalar)

    if mevcut_sayi == 0:
        print("HATA: Klasorun ici bos!")
        return

    if mevcut_sayi >= hedef_sayi:
        print(f"Zaten {mevcut_sayi} goruntu var, artirma gerekmez.")
        return

    eklenecek_sayi = hedef_sayi - mevcut_sayi
    print(f"Mevcut: {mevcut_sayi} | Hedef: {hedef_sayi} | Eklenecek: {eklenecek_sayi}")

    eklenen = 0
    i = 0
    while eklenen < eklenecek_sayi:
        secilen = random.choice(dosyalar)
        img = _oku(os.path.join(klasor_yolu, secilen))
        if img is None:
            i += 1
            continue

        islem = random.randint(0, 4)
        img = _artir(img, islem)

        yeni_ad = f"aug_{i}_{os.path.splitext(secilen)[0]}.jpg"
        if _kaydet(os.path.join(klasor_yolu, yeni_ad), img):
            eklenen += 1
        i += 1

    print(f"Tamamlandi! {eklenen} goruntu eklendi.")


def veri_artir_paired(img_klasor, mask_klasor, hedef_sayi=1000):
    """
    Goruntu ve maskeyi ayni augmentation ile birlikte artir.
    Segmentasyon egitimi icin uygundur — eslestirmeyi bozmayin.
    """
    if not os.path.exists(img_klasor) or not os.path.exists(mask_klasor):
        print("HATA: Goruntu veya maske klasoru bulunamadi.")
        return

    dosyalar = [f for f in os.listdir(img_klasor) if f.lower().endswith(('.jpg', '.png', '.jpeg'))
                and os.path.exists(os.path.join(mask_klasor, f))]

    mevcut_sayi = len(dosyalar)
    if mevcut_sayi == 0:
        print("HATA: Eslesen goruntu-maske cifti bulunamadi!")
        return

    if mevcut_sayi >= hedef_sayi:
        print(f"Zaten {mevcut_sayi} goruntu var, artirma gerekmez.")
        return

    eklenecek_sayi = hedef_sayi - mevcut_sayi
    print(f"[Paired] Mevcut: {mevcut_sayi} | Hedef: {hedef_sayi} | Eklenecek: {eklenecek_sayi}")

    eklenen = 0
    i = 0
    while eklenen < eklenecek_sayi:
        secilen = random.choice(dosyalar)
        img = _oku(os.path.join(img_klasor, secilen))
        mask_img = _oku(os.path.join(mask_klasor, secilen))

        if img is None or mask_img is None:
            i += 1
            continue

        # Parlaklik augmentation maskeye uygulanmaz (sadece geometrik)
        islem = random.randint(0, 3)
        img_aug = _artir(img, islem)
        mask_aug = _artir(mask_img, islem)

        ad_koku = os.path.splitext(secilen)[0]
        yeni_ad = f"aug_{i}_{ad_koku}.jpg"

        img_ok = _kaydet(os.path.join(img_klasor, yeni_ad), img_aug)
        mask_ok = _kaydet(os.path.join(mask_klasor, yeni_ad), mask_aug)

        if img_ok and mask_ok:
            eklenen += 1
        i += 1

    print(f"Tamamlandi! {eklenen} goruntu-maske cifti eklendi.")


if __name__ == "__main__":
    # Corn diseased dengesizligini duzelt
    corn_img  = os.path.join(BASE_DIR, "dataset_balanced", "corn", "diseased")
    corn_mask = os.path.join(BASE_DIR, "dataset_balanced", "masks", "corn")
    veri_artir_paired(corn_img, corn_mask, hedef_sayi=1000)
