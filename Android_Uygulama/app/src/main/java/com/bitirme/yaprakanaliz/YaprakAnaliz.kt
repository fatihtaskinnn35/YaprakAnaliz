package com.bitirme.yaprakanaliz

import android.content.Context
import android.graphics.Bitmap
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.FileChannel

class YaprakAnaliz(context: Context) {

    private val segInterpreter: Interpreter   // Hastalik segmentasyonu
    private val nirInterpreter: Interpreter   // Pseudo-NIR tahmini
    private val IMG_SIZE = 256
    private val THRESHOLD = 0.5f

    init {
        try {
            segInterpreter = modelYukle(context, "yaprak_modeli_mobil.tflite")
            nirInterpreter = modelYukle(context, "yaprak_nir_modeli_mobil.tflite")
        } catch (e: Exception) {
            throw RuntimeException("TFLite model yuklenemedi: ${e.message}", e)
        }
    }

    private fun modelYukle(context: Context, dosyaAdi: String): Interpreter {
        val fd = context.assets.openFd(dosyaAdi)
        val stream = FileInputStream(fd.fileDescriptor)
        val buffer = stream.channel.map(
            FileChannel.MapMode.READ_ONLY,
            fd.startOffset,
            fd.declaredLength
        )
        return Interpreter(buffer)
    }

    // nirGerekli=false ise NIR modeli atlanir (canli kamerada secili olmayan modu
    // her karede hesaplamak gereksiz sure kaybettiriyordu)
    fun analiz(bitmap: Bitmap, nirGerekli: Boolean = true): SonucModel {
        val olceklenmis = Bitmap.createScaledBitmap(bitmap, IMG_SIZE, IMG_SIZE, true)
        val inputBuffer = goruntuyeByteBuffer(olceklenmis)
        if (olceklenmis !== bitmap) olceklenmis.recycle()

        // 1. Segmentasyon — hastalikli bolgeler  (model cikti sekli: [1, 256, 256, 1])
        val segCikti = Array(1) { Array(IMG_SIZE) { Array(IMG_SIZE) { FloatArray(1) } } }
        segInterpreter.run(inputBuffer, segCikti)

        // 2. Pseudo-NIR — bitki saglik haritasi (model cikti sekli: [1, 256, 256, 1])
        var nirBitmap: Bitmap? = null
        if (nirGerekli) {
            inputBuffer.rewind()
            val nirCikti = Array(1) { Array(IMG_SIZE) { Array(IMG_SIZE) { FloatArray(1) } } }
            nirInterpreter.run(inputBuffer, nirCikti)
            nirBitmap = nirHaritasiBitmap(nirCikti[0])
        }

        // Hastalik yuzdesi hesapla
        val maske = segCikti[0]
        val hastalikPiksel = maske.sumOf { satir -> satir.count { it[0] > THRESHOLD } }
        val yuzde = (hastalikPiksel.toFloat() / (IMG_SIZE * IMG_SIZE)) * 100f

        return SonucModel(
            hastalikYuzdesi = yuzde,
            maskeBitmap     = maskeyeBitmap(maske),
            nirBitmap       = nirBitmap
        )
    }

    private fun goruntuyeByteBuffer(bitmap: Bitmap): ByteBuffer {
        val buffer = ByteBuffer.allocateDirect(1 * IMG_SIZE * IMG_SIZE * 3 * 4)
        buffer.order(ByteOrder.nativeOrder())
        val pixels = IntArray(IMG_SIZE * IMG_SIZE)
        bitmap.getPixels(pixels, 0, IMG_SIZE, 0, 0, IMG_SIZE, IMG_SIZE)
        // Model egitiminde OpenCV (cv2.imdecode) kullanildigi icin kanallar BGR sirasinda;
        // buradaki sira da BGR'a uydurulmustur, aksi halde R/B kanallari ters analiz edilir.
        for (piksel in pixels) {
            buffer.putFloat((piksel          and 0xFF) / 255.0f)
            buffer.putFloat(((piksel shr 8)  and 0xFF) / 255.0f)
            buffer.putFloat(((piksel shr 16) and 0xFF) / 255.0f)
        }
        return buffer
    }

    private fun maskeyeBitmap(maske: Array<Array<FloatArray>>): Bitmap {
        val pixels = IntArray(IMG_SIZE * IMG_SIZE) { i ->
            val y = i / IMG_SIZE; val x = i % IMG_SIZE
            if (maske[y][x][0] > THRESHOLD) 0xCCFF3300.toInt() else 0x00000000
        }
        return Bitmap.createBitmap(IMG_SIZE, IMG_SIZE, Bitmap.Config.ARGB_8888).also {
            it.setPixels(pixels, 0, IMG_SIZE, 0, 0, IMG_SIZE, IMG_SIZE)
        }
    }

    // Inferno renk paleti: dusuk=mor, orta=turuncu, yuksek=sari (saglikli bitki = yuksek NIR)
    private fun nirHaritasiBitmap(nir: Array<Array<FloatArray>>): Bitmap {
        val pixels = IntArray(IMG_SIZE * IMG_SIZE) { i ->
            val y = i / IMG_SIZE; val x = i % IMG_SIZE
            infernoRenk(nir[y][x][0].coerceIn(0f, 1f))
        }
        return Bitmap.createBitmap(IMG_SIZE, IMG_SIZE, Bitmap.Config.ARGB_8888).also {
            it.setPixels(pixels, 0, IMG_SIZE, 0, 0, IMG_SIZE, IMG_SIZE)
        }
    }

    // Basit Inferno renk paleti approximasyonu
    private fun infernoRenk(t: Float): Int {
        val r = (255 * (0.5f + 0.5f * Math.sin((t * 2.5f - 0.5f) * Math.PI).toFloat())).toInt().coerceIn(0, 255)
        val g = (255 * t * t).toInt().coerceIn(0, 255)
        val b = (255 * (1f - t)).toInt().coerceIn(0, 255)
        return (0xAA shl 24) or (r shl 16) or (g shl 8) or b
    }

    fun kapat() {
        segInterpreter.close()
        nirInterpreter.close()
    }
}

data class SonucModel(
    val hastalikYuzdesi: Float,
    val maskeBitmap: Bitmap,
    val nirBitmap: Bitmap?
)
