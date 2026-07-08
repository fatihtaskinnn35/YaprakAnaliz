# Yaprak Analiz (Leaf Analysis)

Mobil Cihazlarda Gerçek Zamanlı Yaprak Hastalığı Segmentasyonu — Bitirme Projesi
Bandırma Onyedi Eylül Üniversitesi

**Hazırlayanlar:** Hazan Ezgi Erçin (2311504299) & Fatih Taşkın (2111504031)

## English Summary

An Android application for real-time plant leaf disease detection and
severity analysis, developed as a senior thesis project. Uses a U-Net
segmentation model together with a NIR (near-infrared) model, trained on
the PlantVillage dataset (apple, corn, grape leaves). The trained models
are converted to TensorFlow Lite for on-device mobile inference.

- `Android_Uygulama/` — Android app source code (Kotlin)
- `Python_Model/` — model training code (U-Net + NIR), TFLite conversion scripts
- `Raporlar/` — thesis and project reports, including an English report
  (`HazanEzgi_Ercin_Fatih_Taskin_Project_Report_EN.docx`)

The PlantVillage dataset itself is not included in this repo due to its size;
it is publicly available at
https://www.kaggle.com/datasets/arjuntejaswi/plant-village

---

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

## Teşekkür

Bu bitirme projesinin danışmanlığını üstlenen Dr. Öğr. Üyesi **Alpay Doruk**'a
(Bandırma Onyedi Eylül Üniversitesi, Bilgisayar Mühendisliği Bölümü)
değerli katkı ve rehberliği için teşekkür ederiz.
