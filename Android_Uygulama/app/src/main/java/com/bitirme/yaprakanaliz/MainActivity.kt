package com.bitirme.yaprakanaliz

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.ImageDecoder
import android.location.LocationManager
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.util.Log
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.*
import androidx.camera.core.resolutionselector.ResolutionSelector
import androidx.camera.core.resolutionselector.ResolutionStrategy
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {

    private lateinit var previewView: PreviewView
    private lateinit var overlayView: OverlayView
    private lateinit var nirOverlayView: OverlayView
    private lateinit var tvSonuc: TextView
    private lateinit var tvDurum: TextView
    private lateinit var tvPerformans: TextView
    private lateinit var progressBar: android.widget.ProgressBar
    private lateinit var btnAnalizBaslat: Button
    private lateinit var btnModSeg: Button
    private lateinit var btnModNir: Button
    private lateinit var btnKaydet: Button
    private lateinit var btnGecmis: Button
    private lateinit var btnGaleriden: Button
    private lateinit var ivGaleriResim: ImageView

    private lateinit var yaprakAnaliz: YaprakAnaliz
    private lateinit var cameraExecutor: ExecutorService
    private lateinit var dbHelper: DatabaseHelper

    private var analizAktif = false
    private var nirModuAktif = false
    private var sonHastalikYuzdesi = 0f
    private var sonDurum = ""

    private var sonKareZamani = 0L

    companion object {
        private const val KAMERA_IZIN_KODU = 100
        private const val TAG = "YaprakAnaliz"
        private val IZINLER = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
    }

    private val galeriLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri ->
        uri ?: return@registerForActivityResult
        tvDurum.text = "Analiz ediliyor..."
        btnKaydet.isEnabled = false
        progressBar.visibility = android.view.View.VISIBLE
        Thread {
            try {
                val decoded: Bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                    ImageDecoder.decodeBitmap(
                        ImageDecoder.createSource(contentResolver, uri)
                    ) { decoder, _, _ -> decoder.allocator = ImageDecoder.ALLOCATOR_SOFTWARE }
                } else {
                    @Suppress("DEPRECATION")
                    MediaStore.Images.Media.getBitmap(contentResolver, uri)
                }
                val bitmap = if (decoded.config == Bitmap.Config.HARDWARE)
                    decoded.copy(Bitmap.Config.ARGB_8888, false).also { decoded.recycle() }
                else decoded

                val baslangic = System.currentTimeMillis()
                val sonuc = yaprakAnaliz.analiz(bitmap)
                val sure = System.currentTimeMillis() - baslangic

                runOnUiThread {
                    ivGaleriResim.setImageBitmap(bitmap)
                    ivGaleriResim.visibility = android.view.View.VISIBLE
                    overlayView.maskeyiGuncelle(sonuc.maskeBitmap)
                    sonuc.nirBitmap?.let { nirOverlayView.maskeyiGuncelle(it) }
                    sonucuGoster(sonuc.hastalikYuzdesi, sure, -1f)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Galeri analiz hatasi: ${e.message}", e)
                runOnUiThread {
                    progressBar.visibility = android.view.View.GONE
                    tvDurum.text = "Analiz hatasi olustu"
                }
            }
        }.start()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        previewView     = findViewById(R.id.previewView)
        overlayView     = findViewById(R.id.overlayView)
        nirOverlayView  = findViewById(R.id.nirOverlayView)
        tvSonuc         = findViewById(R.id.tvSonuc)
        tvDurum         = findViewById(R.id.tvDurum)
        tvPerformans    = findViewById(R.id.tvPerformans)
        btnAnalizBaslat = findViewById(R.id.btnAnalizBaslat)
        btnModSeg       = findViewById(R.id.btnModSeg)
        btnModNir       = findViewById(R.id.btnModNir)
        btnKaydet       = findViewById(R.id.btnKaydet)
        btnGecmis       = findViewById(R.id.btnGecmis)
        btnGaleriden    = findViewById(R.id.btnGaleriden)
        ivGaleriResim   = findViewById(R.id.ivGaleriResim)
        progressBar     = findViewById(R.id.progressBar)

        try {
            yaprakAnaliz = YaprakAnaliz(this)
        } catch (e: RuntimeException) {
            Log.e(TAG, "Model yuklenemedi", e)
            Toast.makeText(this, "Hata: Model dosyasi bulunamadi!", Toast.LENGTH_LONG).show()
            tvDurum.text = "Model yuklenemedi"
            return
        }

        cameraExecutor = Executors.newSingleThreadExecutor()
        dbHelper       = DatabaseHelper(this)

        btnAnalizBaslat.setOnClickListener {
            ivGaleriResim.visibility = android.view.View.GONE
            tvPerformans.visibility  = android.view.View.GONE
            analizAktif = !analizAktif
            sonKareZamani = 0L
            if (analizAktif) {
                btnAnalizBaslat.text = "Analizi Durdur"
                btnAnalizBaslat.backgroundTintList =
                    android.content.res.ColorStateList.valueOf(getColor(android.R.color.holo_red_dark))
                tvDurum.text = "Analiz ediliyor..."
                btnKaydet.isEnabled = false
            } else {
                btnAnalizBaslat.text = "Analizi Baslat"
                btnAnalizBaslat.backgroundTintList =
                    android.content.res.ColorStateList.valueOf(0xFF1565C0.toInt())
                tvDurum.text = "Yapragi kameraya tutun"
                tvDurum.setTextColor(getColor(android.R.color.white))
                tvSonuc.text = "Hastalik: -%"
                overlayView.temizle()
                nirOverlayView.temizle()
                sonHastalikYuzdesi = 0f
                sonDurum = ""
                btnKaydet.isEnabled = false
            }
        }

        btnModSeg.setOnClickListener {
            nirModuAktif = false
            overlayView.visibility    = android.view.View.VISIBLE
            nirOverlayView.visibility = android.view.View.GONE
            btnModSeg.backgroundTintList =
                android.content.res.ColorStateList.valueOf(0xFF2E7D32.toInt())
            btnModNir.backgroundTintList =
                android.content.res.ColorStateList.valueOf(0xFF555555.toInt())
        }

        btnModNir.setOnClickListener {
            nirModuAktif = true
            overlayView.visibility    = android.view.View.GONE
            nirOverlayView.visibility = android.view.View.VISIBLE
            btnModNir.backgroundTintList =
                android.content.res.ColorStateList.valueOf(0xFF6A1B9A.toInt())
            btnModSeg.backgroundTintList =
                android.content.res.ColorStateList.valueOf(0xFF555555.toInt())
        }

        btnGaleriden.setOnClickListener {
            analizAktif = false
            sonKareZamani = 0L
            btnAnalizBaslat.text = "Analizi Baslat"
            btnAnalizBaslat.backgroundTintList =
                android.content.res.ColorStateList.valueOf(0xFF1565C0.toInt())
            galeriLauncher.launch("image/*")
        }

        btnKaydet.setOnClickListener {
            if (sonDurum.isNotEmpty()) {
                val konum = konumuAl()
                dbHelper.kaydet(sonHastalikYuzdesi, sonDurum, konum)
                Toast.makeText(this, "Analiz kaydedildi", Toast.LENGTH_SHORT).show()
                btnKaydet.isEnabled = false
            }
        }

        btnGecmis.setOnClickListener {
            startActivity(Intent(this, HistoryActivity::class.java))
        }

        if (tumIzinlerVarMi()) kameraBaslat()
        else ActivityCompat.requestPermissions(this, IZINLER, KAMERA_IZIN_KODU)
    }

    private fun konumuAl(): String {
        return try {
            val lm = getSystemService(LOCATION_SERVICE) as LocationManager
            val loc = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER)
                ?: lm.getLastKnownLocation(LocationManager.NETWORK_PROVIDER)
            if (loc != null) "%.5f, %.5f".format(loc.latitude, loc.longitude)
            else "Konum alinamadi"
        } catch (e: SecurityException) {
            "Konum izni yok"
        }
    }

    private fun kameraBaslat() {
        val future = ProcessCameraProvider.getInstance(this)
        future.addListener({
            val provider = future.get()

            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }

            val analyzer = ImageAnalysis.Builder()
                .setResolutionSelector(
                    ResolutionSelector.Builder()
                        .setResolutionStrategy(
                            ResolutionStrategy(
                                android.util.Size(256, 256),
                                ResolutionStrategy.FALLBACK_RULE_CLOSEST_HIGHER_THEN_LOWER
                            )
                        )
                        .build()
                )
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
                .also {
                    it.setAnalyzer(cameraExecutor) { imageProxy ->
                        if (analizAktif) kareyiAnalizEt(imageProxy)
                        else imageProxy.close()
                    }
                }

            try {
                provider.unbindAll()
                provider.bindToLifecycle(
                    this, CameraSelector.DEFAULT_BACK_CAMERA, preview, analyzer
                )
            } catch (e: Exception) {
                Log.e(TAG, "Kamera hatasi", e)
            }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun kareyiAnalizEt(imageProxy: ImageProxy) {
        val kareBaslangic = System.currentTimeMillis()
        try {
            val bitmap = imageProxy.toBitmap()
            val analizBaslangic = System.currentTimeMillis()
            val sonuc = yaprakAnaliz.analiz(bitmap, nirGerekli = nirModuAktif)
            val analizSuresi = System.currentTimeMillis() - analizBaslangic

            val fps = if (sonKareZamani > 0)
                1000f / (kareBaslangic - sonKareZamani)
            else 0f
            sonKareZamani = kareBaslangic

            runOnUiThread {
                // Bu kare islenirken kullanici "Durdur"a basmis olabilir;
                // bu durumda gecikmeli sonucu ekrana yansitmamak gerekir.
                if (analizAktif) {
                    overlayView.maskeyiGuncelle(sonuc.maskeBitmap)
                    sonuc.nirBitmap?.let { nirOverlayView.maskeyiGuncelle(it) }
                    sonucuGoster(sonuc.hastalikYuzdesi, analizSuresi, fps)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Analiz hatasi: ${e.message}")
            runOnUiThread { if (analizAktif) tvDurum.text = "Analiz hatasi olustu" }
        } finally {
            imageProxy.close()
        }
    }

    private fun sonucuGoster(yuzde: Float, surems: Long = -1, fps: Float = -1f) {
        progressBar.visibility = android.view.View.GONE
        tvSonuc.text = "Hastalik: %.1f%%".format(yuzde)

        if (surems >= 0) {
            tvPerformans.visibility = android.view.View.VISIBLE
            tvPerformans.text = if (fps > 0)
                "FPS: %.1f  |  Süre: %dms".format(fps.coerceAtMost(99f), surems)
            else
                "Süre: %dms".format(surems)
        }

        val (durum, renk) = when {
            yuzde < 5f  -> "Yaprak Saglikli"   to getColor(android.R.color.holo_green_dark)
            yuzde < 25f -> "Hafif Hastalik"    to getColor(android.R.color.holo_orange_light)
            yuzde < 50f -> "Orta Hastalik"     to getColor(android.R.color.holo_orange_dark)
            else        -> "Siddetli Hastalik" to getColor(android.R.color.holo_red_dark)
        }
        tvDurum.text = durum
        tvDurum.setTextColor(renk)
        sonHastalikYuzdesi = yuzde
        sonDurum = durum
        btnKaydet.isEnabled = true
    }

    private fun tumIzinlerVarMi() = IZINLER.all {
        ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED
    }

    override fun onRequestPermissionsResult(
        requestCode: Int, permissions: Array<out String>, grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == KAMERA_IZIN_KODU) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED)
                kameraBaslat()
            else
                tvDurum.text = "Kamera izni gerekli!"
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        cameraExecutor.shutdown()
        if (::yaprakAnaliz.isInitialized) yaprakAnaliz.kapat()
        if (::dbHelper.isInitialized) dbHelper.close()
    }
}
