import os
import cv2
import random


KLASOR_YOLU = r"C:\Users\Ander\OneDrive\Masaüstü\leaf_project\dataset_balanced\grape\healthy"

def veri_artir(hedef_sayi=1000):

    dosyalar = [f for f in os.listdir(KLASOR_YOLU) if f.endswith(('.jpg', '.png', '.jpeg'))]
    mevcut_sayi = len(dosyalar)
    
    if mevcut_sayi >= hedef_sayi:
        print(f"Zaten {mevcut_sayi} görüntü var, artırmaya gerek yok.")
        return

    eklenecek_sayi = hedef_sayi - mevcut_sayi
    print(f"Mevcut: {mevcut_sayi}. {eklenecek_sayi} adet yeni görüntü üretiliyor...")

    for i in range(eklenecek_sayi):
       
        secilen_dosya = random.choice(dosyalar)
        img = cv2.imread(os.path.join(KLASOR_YOLU, secilen_dosya))
        
        if img is None:
            continue

     
        islem = random.randint(0, 1)
        if islem == 0:
            img = cv2.flip(img, 1)  # Yatay çevir
        else:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)  # 90 derece döndür
            
      
        yeni_ad = f"aug_{i}_{secilen_dosya}"
        cv2.imwrite(os.path.join(KLASOR_YOLU, yeni_ad), img)

    print(f"İşlem tamamlandı! Toplam 1000 görüntüye ulaşıldı.")

# Fonksiyonu çalıştır
if __name__ == "__main__":
    veri_artir(1000)