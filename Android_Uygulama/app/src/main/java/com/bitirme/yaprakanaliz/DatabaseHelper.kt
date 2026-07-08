package com.bitirme.yaprakanaliz

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

data class AnalizKayit(
    val id: Long,
    val tarih: String,
    val hastalikYuzdesi: Float,
    val durum: String,
    val konum: String
)

class DatabaseHelper(context: Context) :
    SQLiteOpenHelper(context, DB_ADI, null, DB_SURUMU) {

    companion object {
        private const val DB_ADI     = "yaprak_analiz.db"
        private const val DB_SURUMU  = 2
        private const val TABLO      = "analizler"
        private const val SUTUN_ID   = "id"
        private const val SUTUN_TARIH = "tarih"
        private const val SUTUN_YUZDE = "hastalik_yuzdesi"
        private const val SUTUN_DURUM = "durum"
        private const val SUTUN_KONUM = "konum"
    }

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            """CREATE TABLE $TABLO (
                $SUTUN_ID    INTEGER PRIMARY KEY AUTOINCREMENT,
                $SUTUN_TARIH TEXT NOT NULL,
                $SUTUN_YUZDE REAL NOT NULL,
                $SUTUN_DURUM TEXT NOT NULL,
                $SUTUN_KONUM TEXT
            )"""
        )
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        if (oldVersion < 2) {
            db.execSQL("ALTER TABLE $TABLO ADD COLUMN $SUTUN_KONUM TEXT DEFAULT 'Konum alinamadi'")
        }
    }

    fun kaydet(hastalikYuzdesi: Float, durum: String, konum: String = "Konum alinamadi"): Long {
        val tarih = SimpleDateFormat("dd.MM.yyyy HH:mm", Locale.getDefault()).format(Date())
        val values = ContentValues().apply {
            put(SUTUN_TARIH, tarih)
            put(SUTUN_YUZDE, hastalikYuzdesi)
            put(SUTUN_DURUM, durum)
            put(SUTUN_KONUM, konum)
        }
        return writableDatabase.insert(TABLO, null, values)
    }

    fun tumKayitlar(): List<AnalizKayit> {
        val liste = mutableListOf<AnalizKayit>()
        val cursor = readableDatabase.query(
            TABLO, null, null, null, null, null, "$SUTUN_ID DESC"
        )
        cursor.use {
            while (it.moveToNext()) {
                liste.add(
                    AnalizKayit(
                        id              = it.getLong(it.getColumnIndexOrThrow(SUTUN_ID)),
                        tarih           = it.getString(it.getColumnIndexOrThrow(SUTUN_TARIH)),
                        hastalikYuzdesi = it.getFloat(it.getColumnIndexOrThrow(SUTUN_YUZDE)),
                        durum           = it.getString(it.getColumnIndexOrThrow(SUTUN_DURUM)),
                        konum           = it.getString(it.getColumnIndexOrThrow(SUTUN_KONUM)) ?: "Konum yok"
                    )
                )
            }
        }
        return liste
    }

    fun kayitSil(id: Long) {
        writableDatabase.delete(TABLO, "$SUTUN_ID = ?", arrayOf(id.toString()))
    }

    fun tumunuSil() {
        writableDatabase.delete(TABLO, null, null)
    }
}
