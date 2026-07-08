package com.bitirme.yaprakanaliz

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class HistoryActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var tvBos: TextView
    private lateinit var dbHelper: DatabaseHelper
    private lateinit var adapter: AnalizAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_history)

        supportActionBar?.apply {
            title = "Analiz Gecmisi"
            setDisplayHomeAsUpEnabled(true)
        }

        recyclerView = findViewById(R.id.recyclerView)
        tvBos = findViewById(R.id.tvBos)
        dbHelper = DatabaseHelper(this)

        recyclerView.layoutManager = LinearLayoutManager(this)
        listeGuncelle()

        findViewById<android.widget.Button>(R.id.btnTumunuSil).setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle("Tüm Kayıtları Sil")
                .setMessage("Tüm analiz geçmişi silinsin mi?")
                .setPositiveButton("Evet") { _, _ ->
                    dbHelper.tumunuSil()
                    listeGuncelle()
                    Toast.makeText(this, "Tüm kayıtlar silindi", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("Hayır", null)
                .show()
        }
    }

    private fun listeGuncelle() {
        val kayitlar = dbHelper.tumKayitlar()
        if (kayitlar.isEmpty()) {
            recyclerView.visibility = View.GONE
            tvBos.visibility = View.VISIBLE
        } else {
            recyclerView.visibility = View.VISIBLE
            tvBos.visibility = View.GONE
            adapter = AnalizAdapter(kayitlar.toMutableList()) { kayit ->
                dbHelper.kayitSil(kayit.id)
                listeGuncelle()
            }
            recyclerView.adapter = adapter
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }

    override fun onDestroy() {
        super.onDestroy()
        dbHelper.close()
    }
}

class AnalizAdapter(
    private val liste: MutableList<AnalizKayit>,
    private val onSil: (AnalizKayit) -> Unit
) : RecyclerView.Adapter<AnalizAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvDurum: TextView  = view.findViewById(R.id.tvDurumItem)
        val tvYuzde: TextView  = view.findViewById(R.id.tvYuzdeItem)
        val tvTarih: TextView  = view.findViewById(R.id.tvTarihItem)
        val tvKonum: TextView  = view.findViewById(R.id.tvKonumItem)
        val btnSil: ImageButton = view.findViewById(R.id.btnSilItem)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_analiz, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val kayit = liste[position]
        holder.tvDurum.text = kayit.durum
        holder.tvYuzde.text = "Hastalik: %.1f%%".format(kayit.hastalikYuzdesi)
        holder.tvTarih.text = kayit.tarih
        holder.tvKonum.text = if (kayit.konum.isNotEmpty() && kayit.konum != "Konum alinamadi")
            "📍 ${kayit.konum}" else "📍 Konum yok"
        holder.tvDurum.setTextColor(durumRengi(holder.itemView, kayit.durum))
        holder.btnSil.setOnClickListener { onSil(kayit) }
    }

    override fun getItemCount() = liste.size

    private fun durumRengi(view: View, durum: String): Int {
        val ctx = view.context
        return when (durum) {
            "Yaprak Saglikli" -> ctx.getColor(android.R.color.holo_green_dark)
            "Hafif Hastalik"  -> ctx.getColor(android.R.color.holo_orange_light)
            "Orta Hastalik"   -> ctx.getColor(android.R.color.holo_orange_dark)
            else              -> ctx.getColor(android.R.color.holo_red_dark)
        }
    }
}
