# Yaprak Analiz

Mobil Cihazlarda Gerçek Zamanlı Yaprak Hastalığı Segmentasyonu — Bitirme Projesi
Bandırma Onyedi Eylül Üniversitesi

**Hazırlayanlar:** Hazan Ezgi Erçin (2311504299) & Fatih Taşkın (2111504031)

## Proje Özeti

U-Net segmentasyon modeli ve NIR (yakın kızılötesi) modeli kullanılarak yaprak
hastalıklarının tespiti ve şiddet analizi yapan bir Android uygulaması.
PlantVillage veri seti (elma, mısır, üzüm) üzerinde eğitilmiştir.

## İçerik

| Klasör | Açıklama |
|---|---|
| `Android_Uygulama/` | Android uygulaması kaynak kodu (Kotlin/Java) |
| `Python_Model/` | Model eğitim kodu, U-Net + NIR modelleri, TFLite dönüşümleri |
| `Raporlar/` | Bitirme tezi ve proje raporları |
| `*.pptx` | Proje sunumu |

## Python Model Kodunu Çalıştırmak İçin

```
pip install tensorflow numpy opencv-python matplotlib
```

- `egitim.py` — Segmentasyon modeli eğitimi
- `egitim_nir.py` — NIR model eğitimi
- `final_test.py` — Model test ve görselleştirme
- `metrik_hesapla.py` — IoU ve Dice metrikleri

**Not:** PlantVillage veri seti bu repoya dahil edilmemiştir (boyut nedeniyle).
Veri setine buradan ulaşabilirsiniz:
https://www.kaggle.com/datasets/arjuntejaswi/plant-village

## Android Kaynak Kodunu Açmak İçin

1. Android Studio'yu aç
2. File → Open → `Android_Uygulama` klasörünü seç
3. Gradle sync bekle
4. Build → Build Bundle/APK → Build APK
