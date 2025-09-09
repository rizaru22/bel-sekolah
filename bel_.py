import threading
import tkinter as tk
import sqlite3
import os
from tkinter import messagebox
from playsound import playsound
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime
class BelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Bel Sekolah Sederhana")
       
        self.geometry("500x400")
        self.create_database()
        self.interface()
        
        self.running=True
        threading.Thread(target=self.cek_jadwal, daemon=True).start()
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
  

    def interface(self):
        self.test_suara =tk.Button(self, text="Test Suara", font=("Helvetica", 14), command=self.tes_suara)
        self.test_suara.grid(row=0, column=0,padx=10, pady=10,sticky="w")
        
        self.create_jadwal_btn = tk.Button(self, text="Tambah Jadwal", font=("Helvetica", 14), command=self.open_create_jadwal)
        self.create_jadwal_btn.grid(row=0, column=1,padx=10, pady=10,sticky="e")
        
           # === Nama hari dalam bahasa Indonesia ===
        hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        today = hari_indo[datetime.today().weekday()]  # weekday() -> 0 = Senin ... 6 = Minggu

        self.label_hari = tk.Label(self, text=f"Hari: {today}", font=("Helvetica", 12, "bold"))
        self.label_hari.grid(row=1, column=0, padx=10, pady=(10,0), sticky="w")
        
        self.tree = ttk.Treeview(self, columns=("Nama Jadwal", "Jam", "File Audio"), show='headings')
        # self.tree.heading("ID", text="ID")
        self.tree.heading("Nama Jadwal", text="Nama Jadwal",anchor="w")
        self.tree.heading("Jam", text="Jam",anchor="w")
        # self.tree.heading("Hari", text="Hari")
        self.tree.heading("File Audio", text="File Audio",anchor="w")
        
        self.tree.column("Nama Jadwal", width=100,anchor="w")
        self.tree.column("Jam", width=70,anchor="w")
        self.tree.column("File Audio", width=300,anchor="w")
        
        self.tree.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.delete_btn = tk.Button(self, text="Delete Jadwal", font=("Helvetica", 14), command=self.delete_jadwal)
        self.delete_btn.grid(row=3, column=0, padx=10,pady=10,sticky="w")
        
         # Tombol Edit Jadwal
        
        self.edit_btn = tk.Button(self, text="Edit Jadwal", font=("Helvetica", 14), command=self.edit_jadwal)
        self.edit_btn.grid(row=3, column=1,padx=10, pady=10,sticky="e")


        self.jadwal_hari_ini()
        
    def jalankan_suara(self,file):
        playsound(file)
        
    def tes_suara(self):
        thread = threading.Thread(target=self.jalankan_suara, args=('bel/Bel Sekolah.mp3',), daemon=True)
        thread.start()
        
    def create_database(self):
        koneksi=sqlite3.connect('bel_app.db')
        cursor = koneksi.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS jadwal_bel (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nama_jadwal TEXT NOT NULL,
                            jam TEXT NOT NULL,  -- format HH:MM:SS
                            hari TEXT NOT NULL CHECK(hari IN ('Senin','Selasa','Rabu','Kamis','Jumat','Sabtu')),
                            file_audio TEXT
                            );
                            """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS log_bel (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_jadwal INTEGER NOT NULL,
                            waktu_dibunyikan TEXT NOT NULL DEFAULT (datetime('now')),
                            status TEXT DEFAULT 'sukses' CHECK(status IN ('sukses','gagal')),
                            FOREIGN KEY (id_jadwal) REFERENCES jadwal_bel(id)
                    );
                """)
        
        koneksi.commit()
        koneksi.close()
        
    def open_create_jadwal(self):
        create_window = create_jadwal(self)
        
    def jadwal_hari_ini(self):
        idx=datetime.today().weekday()
        if idx==6:
            self.jadwal_list = []
            
            for row in  self.tree.get_children():
                self.tree.delete(row)
            
        hari_ini = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'][idx]
        koneksi = sqlite3.connect('bel_app.db')
        cursor = koneksi.cursor()
        cursor.execute("SELECT id,nama_jadwal,jam,hari,file_audio FROM jadwal_bel WHERE hari=? ORDER BY jam", (hari_ini,))
        self.jadwal_list = cursor.fetchall()
        koneksi.close()
        
        for row in  self.tree.get_children():
            self.tree.delete(row)
            
        for row in self.jadwal_list:
            jadwal_id=row[0]
            nama_jadwal=row[1]
            jam=row[2]
            
            file_audio=row[4]
            
            file_display=os.path.basename(file_audio) if file_audio else "-"
            
            if len(file_display)>25:
                file_display=file_display[:22]+"..."
            self.tree.insert("", "end",iid=jadwal_id, values=(nama_jadwal, jam, file_display))
    
    def cek_jadwal(self):
        sudah_bunyi = set()  # untuk mencegah bunyi berulang dalam 1 detik

        while self.running:
            try:
                now = datetime.now().strftime("%H:%M:%S")
                if now=="00:00:00":
                    sudah_bunyi.clear()
                    self.jadwal_hari_ini()
                    
                for row in self.jadwal_list:
                    jadwal_id, nama_jadwal, jam, hari, file_audio = row

                    if jam == now and jadwal_id not in sudah_bunyi:
                        if file_audio and os.path.exists(file_audio):
                            threading.Thread(
                                target=self.jalankan_suara,
                                args=(file_audio,),
                                daemon=True
                            ).start()
                            self.simpan_log(jadwal_id, "sukses")
                        else:
                            self.simpan_log(jadwal_id, "gagal")

                        sudah_bunyi.add(jadwal_id)

                import time
                time.sleep(1)

            except Exception as e:
                print("Error cek_jadwal:", e)
                import time
                time.sleep(1)
    
    def simpan_log(self, id_jadwal, status):
        try:
            koneksi = sqlite3.connect('bel_app.db')
            cursor = koneksi.cursor()
            waktu=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO log_bel (id_jadwal,waktu_dibunyikan, status) VALUES (?,?,?)", (id_jadwal,waktu,status))
            koneksi.commit()
            koneksi.close()
        except sqlite3.Error as e:
            print("Database Error:", e)
                        
    def delete_jadwal(self):
        # Cek apakah ada baris yang dipilih
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Pilih jadwal yang ingin dihapus.")
            return

        # Ambil ID dari iid Treeview
        jadwal_id = int(selected_item[0])

        # Konfirmasi
        confirm = messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus jadwal ini?")
        if not confirm:
            return

        try:
            # Hapus dari database
            koneksi = sqlite3.connect("bel_app.db")
            cursor = koneksi.cursor()
            cursor.execute("DELETE FROM jadwal_bel WHERE id=?", (jadwal_id,))
            koneksi.commit()
            koneksi.close()

            # Hapus dari Treeview
            self.tree.delete(selected_item)

            # Refresh list jadwal agar thread pakai data terbaru
            self.jadwal_hari_ini()

            messagebox.showinfo("Sukses", "Jadwal berhasil dihapus.")
        except sqlite3.Error as e:
            messagebox.showerror("Error Database", str(e))

    def edit_jadwal(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Pilih jadwal yang ingin diedit.")
            return

        jadwal_id = int(selected_item[0])

        # Ambil data dari database
        koneksi = sqlite3.connect("bel_app.db")
        cursor = koneksi.cursor()
        cursor.execute("SELECT id, nama_jadwal, jam, hari, file_audio FROM jadwal_bel WHERE id=?", (jadwal_id,))
        row = cursor.fetchone()
        koneksi.close()

        if row:
            EditJadwal(self, row)  # buka window edit

    def on_close(self):
        self.running = False
        self.destroy()
        
class create_jadwal(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Create Jadwal")
        self.geometry("400x300")
    # Supaya window selalu di atas parent
        self.transient(master)  
        self.grab_set()         # user wajib interaksi di sini dulu
        self.focus_force()      # langsung fokus ke window ini

        self.file_audio_path = None
        self.interface()

    def interface(self):
        tk.Label(self, text="Nama Jadwal:").grid(row=0, column=0, padx=10, pady=10,sticky="w")
        self.nama_jadwal_entry = ttk.Combobox(self, values=["Upacara","Apel","Jam Pertama","Jam Ke-2","Jam Ke-3","Jam Ke-4","Jam Ke-5","Jam Ke-6","Jam Ke-7","Jam Ke-8","Jam Ke-9", "Jam Istirahat", "Jam Pulang"])
        self.nama_jadwal_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        tk.Label(self, text="Jam (HH:MM:SS):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.jam_entry = tk.Entry(self)
        self.jam_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        tk.Label(self, text="Hari:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.hari_entry = ttk.Combobox(self, values=["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"])
        self.hari_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        tk.Label(self, text="File Audio:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.browse_button = tk.Button(self, text="Cari File", command=self.pilih_file)
        self.browse_button.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        # self.label_hasil=tk.Label(self, text="File:",width=40, anchor="w", wraplength=250)
        # self.label_hasil.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        self.save_button = tk.Button(self, text="Simpan", command=self.save_jadwal)
        self.save_button.grid(row=5, column=1,columnspan=2, pady=20)
        
    def pilih_file(self):
        file_path = filedialog.askopenfilename(
            title="Pilih File",
            filetypes=(("File MP3", "*.mp3"), ("Semua File", "*.*"))
        )
        if file_path:
            self.file_audio_path = file_path
            self.file_name=os.path.basename(file_path)
            self.browse_button.config(text=f"{self.file_name}")

    def save_jadwal(self):
        nama_jadwal = self.nama_jadwal_entry.get()
        jam = self.jam_entry.get()
        hari = self.hari_entry.get()
        file_audio = self.file_audio_path

        if not nama_jadwal or not jam or not hari:
            messagebox.showerror("Error", "Please fill all required fields.")
            return

        koneksi = sqlite3.connect('bel_app.db')
        cursor = koneksi.cursor()
        
        try:
            cursor.execute("INSERT INTO jadwal_bel (nama_jadwal, jam, hari, file_audio) VALUES (?, ?, ?, ?)",
                           (nama_jadwal, jam, hari, file_audio))
            koneksi.commit()
            messagebox.showinfo("Success", "Jadwal saved successfully.")
            self.master.jadwal_hari_ini()  # Refresh jadwal in main app
            koneksi.close()
            self.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

class EditJadwal(tk.Toplevel):
    def __init__(self, master, jadwal_data):
        super().__init__(master)
        self.title("Edit Jadwal")
        self.geometry("400x300")
        self.transient(master)
        self.grab_set()
        self.focus_force()

        self.jadwal_id, nama, jam, hari, file_audio = jadwal_data
        self.file_audio_path = file_audio

        # Form input
        tk.Label(self, text="Nama Jadwal:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.nama_entry = ttk.Combobox(self, values=["Upacara","Apel","Jam Pertama","Jam Ke-2","Jam Ke-3","Jam Ke-4","Jam Ke-5","Jam Ke-6","Jam Ke-7","Jam Ke-8","Jam Ke-9","Jam Istirahat","Jam Pulang"])
        self.nama_entry.set(nama)
        self.nama_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        tk.Label(self, text="Jam (HH:MM:SS):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.jam_entry = tk.Entry(self)
        self.jam_entry.insert(0, jam)
        self.jam_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        tk.Label(self, text="Hari:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.hari_entry = ttk.Combobox(self, values=["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"])
        self.hari_entry.set(hari)
        self.hari_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        tk.Label(self, text="File Audio:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.browse_btn = tk.Button(self, text="Ganti File", command=self.pilih_file)
        self.browse_btn.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        if file_audio:
            self.browse_btn.config(text=os.path.basename(file_audio))

        self.save_btn = tk.Button(self, text="Update", command=self.update_jadwal)
        self.save_btn.grid(row=5, column=1, pady=20)

    def pilih_file(self):
        file_path = filedialog.askopenfilename(
            title="Pilih File",
            filetypes=(("File MP3", "*.mp3"), ("Semua File", "*.*"))
        )
        if file_path:
            self.file_audio_path = file_path
            self.browse_btn.config(text=os.path.basename(file_path))

    def update_jadwal(self):
        nama = self.nama_entry.get()
        jam = self.jam_entry.get()
        hari = self.hari_entry.get()
        file_audio = self.file_audio_path

        if not nama or not jam or not hari:
            messagebox.showerror("Error", "Lengkapi semua field.")
            return

        try:
            koneksi = sqlite3.connect("bel_app.db")
            cursor = koneksi.cursor()
            cursor.execute(
                "UPDATE jadwal_bel SET nama_jadwal=?, jam=?, hari=?, file_audio=? WHERE id=?",
                (nama, jam, hari, file_audio, self.jadwal_id)
            )
            koneksi.commit()
            koneksi.close()

            self.master.jadwal_hari_ini()  # refresh tabel
            messagebox.showinfo("Sukses", "Jadwal berhasil diperbarui.")
            self.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error Database", str(e))


if __name__ == "__main__":
    app = BelApp()
    app.mainloop()