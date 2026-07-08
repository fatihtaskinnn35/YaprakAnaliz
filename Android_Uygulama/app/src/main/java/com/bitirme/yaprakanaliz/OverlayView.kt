package com.bitirme.yaprakanaliz

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View

// Kamera on izlemesinin ustune segmentasyon maskesini cizer
class OverlayView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var maskeBitmap: Bitmap? = null
    private val paint = Paint().apply { isFilterBitmap = true }

    fun maskeyiGuncelle(bitmap: Bitmap) {
        maskeBitmap = bitmap
        invalidate()
    }

    fun temizle() {
        maskeBitmap = null
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        maskeBitmap?.let { bmp ->
            // Maskeyi view boyutuna uzat
            canvas.drawBitmap(bmp, null, android.graphics.RectF(0f, 0f, width.toFloat(), height.toFloat()), paint)
        }
    }
}
