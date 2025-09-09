# 🔔 Aplikasi Bel Sekolah Otomatis (Python + Tkinter)

Aplikasi ini adalah **bel sekolah otomatis** berbasis **Python, Tkinter, dan SQLite**, yang dapat memutar suara bel sesuai jadwal yang sudah ditentukan.  
Dilengkapi dengan fitur **CRUD jadwal bel**, **pemilihan file audio (MP3)**, serta **log aktivitas** setiap bel yang dibunyikan.

---

## ✨ Fitur Utama

- 🎶 **Test Suara** → cek apakah audio bisa diputar.
- 📅 **Manajemen Jadwal**  
  - Tambah jadwal (nama, hari, jam, dan file audio).  
  - Edit jadwal yang sudah ada.  
  - Hapus jadwal dengan sekali klik.  
- 📂 **Pemilihan File Audio**  
  - Mendukung file **MP3** (atau format lain yang didukung `playsound`).  
  - Ditampilkan nama file singkat agar rapi di tabel.  
- 🗂️ **Database SQLite**  
  - Menyimpan jadwal bel.  
  - Menyimpan **log bel** (jadwal, waktu bunyi, status sukses/gagal).  
- 🕒 **Otomatis berbunyi sesuai jadwal** dengan sistem thread.  
- 🌍 **Bahasa Indonesia** → hari ditampilkan sesuai format lokal (`Senin - Sabtu`).

---





## ⚙️ Instalasi

1. **Clone repositori**
   ```bash
   git clone https://github.com/username/bel-sekolah.git
   cd bel-sekolah
````

2. **Buat virtual environment (opsional, tapi disarankan)**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Isi file `requirements.txt`:

   ```
   playsound
   ```

   (library lain seperti `tkinter` dan `sqlite3` sudah bawaan Python)

4. **Jalankan aplikasi**

   ```bash
   python bel_app.py
   ```

---

## 📂 Struktur Proyek

```
bel-sekolah/
│── bel_app.py           # file utama aplikasi
│── bel_app.db           # database SQLite (otomatis dibuat)
│── bel/                 # folder audio default
│   └── Bel Sekolah.mp3
│── docs/                # screenshot / dokumentasi
│── requirements.txt
│── README.md
```

---

## 📝 Catatan

* Pastikan **zona waktu komputer** sesuai dengan jam lokal sekolah.
* Gunakan format jam **HH\:MM\:SS** saat input jadwal.
* Jika suara bel tidak keluar, cek:

  * Apakah file audio tersedia.
  * Apakah format audio didukung.
  * Volume komputer aktif.

---

## 📌 Pengembangan Selanjutnya

* Tambahkan **export/import jadwal** ke Excel/CSV.
* Tambahkan **notifikasi visual** ketika bel berbunyi.
* Integrasi dengan **Raspberry Pi** untuk sistem bel fisik.

---

## 👨‍💻 Kontributor

* **Safrizal** – Developer & Maintainer

---

## 📜 Lisensi

Proyek ini menggunakan lisensi **MIT** – silakan gunakan, modifikasi, dan kembangkan sesuai kebutuhan.

```


