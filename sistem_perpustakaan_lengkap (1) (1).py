"""
========================================
SISTEM MANAJEMEN PERPUSTAKAAN PROFESIONAL
========================================
Fitur Lengkap dengan OOP, GUI Tkinter, dan JSON Persistence
========================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json
import os

# ==========================================
# BAGIAN 1: KELAS-KELAS UTAMA (FONDASI OOP)
# ==========================================

# --- MODUL 5: INTERFACE ---
class IValidasi(ABC):
    @abstractmethod
    def cek_kelengkapan(self):
        pass

# --- MODUL 4: ABSTRACT CLASS ---
class EntitasManusia(ABC):
    def __init__(self, id_entitas, nama):
        self.id_entitas = id_entitas
        self.nama = nama
    
    @abstractmethod
    def ambil_data_tuple(self):
        pass

# --- MODUL 3: PEWARISAN (INHERITANCE) ---
class User(EntitasManusia):
    def __init__(self, user_id, username, password, nama, role):
        super().__init__(user_id, nama)
        self.username = username
        self.password = password
        self.role = role
        self.last_login = None

    def login(self, input_username, input_password):
        if self.username == input_username and self.password == input_password:
            self.last_login = datetime.now()
            return True
        return False
        
    def ambil_data_tuple(self):
        return (self.id_entitas, self.username, self.nama, self.role)

# --- MODUL 3 & 5: MULTIPLE INHERITANCE ---
class Anggota(EntitasManusia, IValidasi):
    def __init__(self, id_anggota, nim, nama, email, no_telepon, alamat, status="Aktif"):
        super().__init__(id_anggota, nama)
        self.nim = nim
        self.email = email
        self.no_telepon = no_telepon
        self.alamat = alamat
        self.status = status
        self.denda_menumpuk = 0.0

    def ambil_data_tuple(self):
        return (self.id_entitas, self.nim, self.nama, self.email, self.no_telepon, self.alamat, self.status)
        
    def cek_kelengkapan(self):
        if not all([self.nim, self.nama, self.email, self.no_telepon]):
            return False
        return True
    
    def tambah_denda(self, jumlah_denda):
        self.denda_menumpuk += jumlah_denda
        return self.denda_menumpuk
    
    def bayar_denda(self, jumlah):
        if jumlah <= self.denda_menumpuk:
            self.denda_menumpuk -= jumlah
            return True
        return False

# --- MODUL 1 & 2: CLASS DAN OBJECT ---
class Buku:
    def __init__(self, id_buku, judul, penulis, kategori, penerbit, tahun, stok, isbn="", rating=0, jumlah_tinjau=0):
        self.id_buku = id_buku
        self.judul = judul
        self.penulis = penulis
        self.kategori = kategori
        self.penerbit = penerbit
        self.tahun = int(tahun)
        self.stok = int(stok)
        self.isbn = isbn
        self.rating = rating
        self.jumlah_tinjau = jumlah_tinjau
        self.perbarui_status()

    def perbarui_status(self):
        self.status = "Tersedia" if self.stok > 0 else "Habis"

    def ambil_data_tuple(self):
        self.perbarui_status()
        rating_text = f"{self.rating:.1f}/5 ({self.jumlah_tinjau})" if self.jumlah_tinjau > 0 else "Belum ada rating"
        return (self.id_buku, self.judul, self.penulis, self.kategori, self.penerbit, self.tahun, self.stok, self.status, rating_text)
    
    def kurangi_stok(self):
        if self.stok > 0:
            self.stok -= 1
            self.perbarui_status()
            return True
        return False
    
    def tambah_stok(self):
        self.stok += 1
        self.perbarui_status()

class Peminjaman:
    def __init__(self, id_pinjam, anggota, buku, durasi_hari=7, tgl_pinjam=None, tgl_kembali_sebenarnya=None):
        self.id_pinjam = id_pinjam
        self.anggota = anggota
        self.buku = buku
        self.durasi_hari = durasi_hari
        self.tanggal_pinjam = tgl_pinjam or datetime.now()
        self.tanggal_jatuh_tempo = self.tanggal_pinjam + timedelta(days=durasi_hari)
        self.tanggal_kembali_sebenarnya = tgl_kembali_sebenarnya
        self.status = "Dipinjam"
        self.denda_dibayar = 0.0

    def ambil_data_tuple(self):
        status_denda = "Lunas" if self.denda_dibayar == 0 else f"Rp {self.denda_dibayar:,.0f}"
        return (self.id_pinjam, self.anggota.nama, self.buku.judul,
                self.tanggal_pinjam.strftime("%d/%m/%Y"),
                self.tanggal_jatuh_tempo.strftime("%d/%m/%Y"),
                self.status, status_denda)

    def hitung_denda(self, tarif_perhari=5000):
        if self.tanggal_kembali_sebenarnya is None:
            hari_terlambat = max(0, (datetime.now() - self.tanggal_jatuh_tempo).days)
        else:
            hari_terlambat = max(0, (self.tanggal_kembali_sebenarnya - self.tanggal_jatuh_tempo).days)
        
        denda = hari_terlambat * tarif_perhari
        return denda, hari_terlambat

    def kembalikan_buku(self, tgl_kembali=None):
        self.tanggal_kembali_sebenarnya = tgl_kembali or datetime.now()
        self.status = "Dikembalikan"
        denda, hari_terlambat = self.hitung_denda()
        if denda > 0:
            self.denda_dibayar = denda
        return denda, hari_terlambat

class DendaManager:
    TARIF_PERHARI = 5000  
    DENDA_MAKSIMAL = 100000  

class LaporanGenerator:
    def __init__(self, db_buku, db_anggota, db_peminjaman):
        self.db_buku = db_buku
        self.db_anggota = db_anggota
        self.db_peminjaman = db_peminjaman

    def statistik_perpustakaan(self):
        total_buku = len(self.db_buku)
        total_stok = sum(b.stok for b in self.db_buku)
        total_anggota = len(self.db_anggota)
        total_peminjaman_aktif = sum(1 for p in self.db_peminjaman if p.status == "Dipinjam")
        buku_populer = max(self.db_buku, key=lambda b: b.jumlah_tinjau).judul if self.db_buku else "N/A"
        total_denda = sum(a.denda_menumpuk for a in self.db_anggota)
        
        return {
            'total_buku': total_buku, 'total_stok': total_stok, 'total_anggota': total_anggota,
            'peminjaman_aktif': total_peminjaman_aktif, 'buku_populer': buku_populer, 'total_denda': total_denda
        }


# ==========================================
# BAGIAN 2: SISTEM DATABASE (PERSISTENT JSON)
# ==========================================
class Database:
    def __init__(self):
        self.file_data = "data_perpustakaan.json"
        self.admin_sistem = User(1, "admin", "admin123", "Admin Perpustakaan", "Admin")
        self.database_buku = []
        self.database_anggota = []
        self.database_peminjaman = []
        self.muat_data()

    def muat_data(self):
        if os.path.exists(self.file_data):
            try:
                with open(self.file_data, "r") as f:
                    data = json.load(f)
                    
                    for b in data.get("buku", []):
                        self.database_buku.append(Buku(b["id"], b["judul"], b["penulis"], b["kategori"], b["penerbit"], b["tahun"], b["stok"], b.get("isbn", "")))
                        
                    for a in data.get("anggota", []):
                        angg = Anggota(a["id"], a["nim"], a["nama"], a["email"], a["telepon"], a["alamat"])
                        angg.denda_menumpuk = a.get("denda", 0.0)
                        self.database_anggota.append(angg)
                        
                    for p in data.get("peminjaman", []):
                        anggota = next((a for a in self.database_anggota if a.id_entitas == p["id_anggota"]), None)
                        buku = next((b for b in self.database_buku if b.id_buku == p["id_buku"]), None)
                        
                        if anggota and buku:
                            tgl_pinjam = datetime.strptime(p["tgl_pinjam"], "%Y-%m-%d")
                            tgl_kembali = datetime.strptime(p["tgl_kembali"], "%Y-%m-%d") if p.get("tgl_kembali") else None
                            pinjam = Peminjaman(p["id"], anggota, buku, p["durasi"], tgl_pinjam, tgl_kembali)
                            pinjam.status = p["status"]
                            pinjam.denda_dibayar = p.get("denda_dibayar", 0.0)
                            self.database_peminjaman.append(pinjam)
            except Exception as e:
                print("Error loading database:", e)
                self.init_data_dummy()
        else:
            self.init_data_dummy()
            self.simpan_data()

    def simpan_data(self):
        data = {
            "buku": [{"id": b.id_buku, "judul": b.judul, "penulis": b.penulis, "kategori": b.kategori, "penerbit": b.penerbit, "tahun": b.tahun, "stok": b.stok, "isbn": b.isbn} for b in self.database_buku],
            "anggota": [{"id": a.id_entitas, "nim": a.nim, "nama": a.nama, "email": a.email, "telepon": a.no_telepon, "alamat": a.alamat, "denda": a.denda_menumpuk} for a in self.database_anggota],
            "peminjaman": [{"id": p.id_pinjam, "id_anggota": p.anggota.id_entitas, "id_buku": p.buku.id_buku, "durasi": p.durasi_hari, "tgl_pinjam": p.tanggal_pinjam.strftime("%Y-%m-%d"), "tgl_kembali": p.tanggal_kembali_sebenarnya.strftime("%Y-%m-%d") if p.tanggal_kembali_sebenarnya else None, "status": p.status, "denda_dibayar": p.denda_dibayar} for p in self.database_peminjaman]
        }
        with open(self.file_data, "w") as f:
            json.dump(data, f, indent=4)

    def init_data_dummy(self):
        self.database_buku = [
            Buku("B001", "Pemrograman Python", "Andi Kurniawan", "Teknologi", "Informatika", "2021", 15, "978-1234567890", 4.5, 12),
            Buku("B002", "Basis Data SQL", "Abdul Kadir", "Teknologi", "Andi Publisher", "2019", 8, "978-2234567891", 4.2, 8),
            Buku("B003", "Struktur Data C++", "Nurul Huda", "Teknologi", "Andi Publisher", "2021", 12, "978-3234567892", 4.7, 15),
        ]
        self.database_anggota = [
            Anggota("A001", "2410671034", "Briliant Rizqy", "briliant@email.com", "081234567890", "Jl. Raya No. 123, Jember"),
            Anggota("A002", "2410671047", "Rino Wahyu Murti", "rino@email.com", "081298765432", "Jl. Gatot Subroto, Jember"),
        ]
        pinjam1 = Peminjaman("PIN-001", self.database_anggota[0], self.database_buku[0], 7, datetime.now() - timedelta(days=2))
        self.database_buku[0].kurangi_stok()
        self.database_peminjaman.append(pinjam1)
        
        pinjam2 = Peminjaman("PIN-002", self.database_anggota[1], self.database_buku[1], 7, datetime.now() - timedelta(days=12))
        self.database_buku[1].kurangi_stok()
        self.database_peminjaman.append(pinjam2)


# ==========================================
# BAGIAN 3: GUI APLIKASI UTAMA
# ==========================================
class SistemPerpustakaanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Manajemen Perpustakaan - Admin Panel")
        self.root.geometry("1400x850")
        self.root.configure(bg="#f0f0f5")
        
        self.warna_utama = "#2c3e50"
        self.warna_aksen = "#3498db"
        self.warna_sukses = "#27ae60"
        self.warna_warning = "#e74c3c"
        self.warna_info = "#f39c12"
        
        self.db = Database()
        self._setup_style()
        self.tampilkan_halaman_login()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=28, relief="flat", borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#ecf0f1", relief="flat")
        style.map("Treeview", background=[("selected", self.warna_aksen)], foreground=[("selected", "white")])

    def bersihkan_layar(self):
        for widget in self.root.winfo_children(): widget.destroy()

    def bersihkan_konten(self):
        if hasattr(self, 'main_frame'):
            for widget in self.main_frame.winfo_children(): widget.destroy()

    # ==========================================
    # HALAMAN LOGIN
    # ==========================================
    def tampilkan_halaman_login(self):
        self.bersihkan_layar()
        
        bg_frame = tk.Frame(self.root, bg=self.warna_utama)
        bg_frame.pack(side="left", fill="both", expand=True)
        tk.Label(bg_frame, text="📚 SISTEM MANAJEMEN\nPERPUSTAKAAN", font=("Segoe UI", 28, "bold"), bg=self.warna_utama, fg="white", justify="center").pack(pady=100)
        tk.Label(bg_frame, text="Kelola perpustakaan dengan efisien\ndan profesional", font=("Segoe UI", 12), bg=self.warna_utama, fg="#ecf0f1", justify="center").pack()
        
        form_frame = tk.Frame(self.root, bg="white")
        form_frame.pack(side="right", fill="both", expand=True)
        login_container = tk.Frame(form_frame, bg="white")
        login_container.place(relx=0.5, rely=0.5, anchor="center", width=350, height=400)
        
        tk.Label(login_container, text="Login Admin", font=("Segoe UI", 20, "bold"), bg="white", fg=self.warna_utama).pack(pady=30)
        
        tk.Label(login_container, text="Username", font=("Segoe UI", 10, "bold"), bg="white", fg="#333").pack(anchor="w", padx=25, pady=(10, 5))
        self.ent_username = tk.Entry(login_container, font=("Segoe UI", 11), bg="#f5f5f5", relief="solid", borderwidth=1)
        self.ent_username.pack(fill="x", padx=25, pady=(0, 15), ipady=10)
        self.ent_username.insert(0, "admin")
        
        tk.Label(login_container, text="Password", font=("Segoe UI", 10, "bold"), bg="white", fg="#333").pack(anchor="w", padx=25, pady=(10, 5))
        self.ent_password = tk.Entry(login_container, font=("Segoe UI", 11), bg="#f5f5f5", relief="solid", borderwidth=1, show="•")
        self.ent_password.pack(fill="x", padx=25, pady=(0, 30), ipady=10)
        self.ent_password.insert(0, "admin123")
        
        tk.Button(login_container, text="LOGIN", font=("Segoe UI", 12, "bold"), bg=self.warna_aksen, fg="white", relief="flat", cursor="hand2", command=self.proses_login).pack(fill="x", padx=25, ipady=10)
        self.ent_password.bind('<Return>', lambda e: self.proses_login())

    def proses_login(self):
        username = self.ent_username.get().strip()
        password = self.ent_password.get().strip()
        
        if self.db.admin_sistem.login(username, password):
            self.tampilkan_dashboard()
        else:
            messagebox.showerror("❌ Login Gagal", "Username atau Password salah!")

    # ==========================================
    # DASHBOARD & SIDEBAR
    # ==========================================
    def tampilkan_dashboard(self):
        self.bersihkan_layar()
        self._buat_sidebar()
        self.main_frame = tk.Frame(self.root, bg="#f0f0f5")
        self.main_frame.pack(side="right", fill="both", expand=True)
        self.halaman_dashboard()

    def _buat_sidebar(self):
        sidebar = tk.Frame(self.root, bg=self.warna_utama, width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="📚 PERPUSTAKAAN", font=("Segoe UI", 12, "bold"), bg=self.warna_utama, fg="white").pack(fill="x", padx=15, pady=20)
        
        menu_items = [
            ("🏠 Dashboard", self.halaman_dashboard),
            ("📖 Data Buku", self.halaman_data_buku),
            ("👥 Anggota", self.halaman_data_anggota),
            ("🔄 Peminjaman", self.halaman_peminjaman),
            ("↩️ Pengembalian", self.halaman_pengembalian),
            ("⏰ Denda", self.halaman_denda),
            ("📊 Laporan", self.halaman_laporan),
            ("⚙️ Pengaturan", self.halaman_pengaturan),
        ]
        
        for icon_text, command in menu_items:
            tk.Button(sidebar, text=icon_text, font=("Segoe UI", 10), bg=self.warna_utama, fg="white", relief="flat", anchor="w", padx=20, cursor="hand2", activebackground=self.warna_aksen, command=command).pack(fill="x", pady=8)
        
        tk.Frame(sidebar, height=50, bg=self.warna_utama).pack(fill="both", expand=True)
        tk.Button(sidebar, text="🚪 Logout", font=("Segoe UI", 10, "bold"), bg="#e74c3c", fg="white", relief="flat", cursor="hand2", command=self.tampilkan_halaman_login).pack(fill="x", padx=10, pady=10, ipady=8)

    def halaman_dashboard(self):
        self.bersihkan_konten()
        tk.Label(self.main_frame, text="📊 DASHBOARD", font=("Segoe UI", 18, "bold"), bg="#f0f0f5", fg=self.warna_utama).pack(fill="x", padx=20, pady=15)
        
        laporan = LaporanGenerator(self.db.database_buku, self.db.database_anggota, self.db.database_peminjaman)
        stats = laporan.statistik_perpustakaan()
        
        card_frame = tk.Frame(self.main_frame, bg="#f0f0f5")
        card_frame.pack(fill="x", padx=20, pady=10)
        
        cards = [
            ("📚 Total Buku", str(stats['total_buku']), self.warna_aksen),
            ("📦 Stok Tersedia", str(stats['total_stok']), self.warna_sukses),
            ("👥 Anggota Aktif", str(stats['total_anggota']), self.warna_info),
            ("🔄 Peminjaman Aktif", str(stats['peminjaman_aktif']), self.warna_warning),
        ]
        
        for title, value, warna in cards:
            card = tk.Frame(card_frame, bg=warna, relief="flat")
            card.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            tk.Label(card, text=title, font=("Segoe UI", 10), bg=warna, fg="white").pack(anchor="w", padx=15, pady=10)
            tk.Label(card, text=value, font=("Segoe UI", 24, "bold"), bg=warna, fg="white").pack(anchor="w", padx=15, pady=(0, 10))
        
        info_frame = tk.Frame(self.main_frame, bg="white", relief="flat")
        info_frame.pack(fill="both", padx=20, pady=15, expand=True)
        tk.Label(info_frame, text="📌 Ringkasan Sistem", font=("Segoe UI", 12, "bold"), bg="white", fg=self.warna_utama).pack(anchor="w", padx=15, pady=10)
        
        info_text = f"Buku Paling Populer: {stats['buku_populer']}\nTotal Denda Terbayar: Rp {stats['total_denda']:,.0f}\nStatus Sistem: ✅ Normal tersimpan di JSON"
        tk.Label(info_frame, text=info_text, font=("Segoe UI", 10), bg="white", fg="#555", justify="left").pack(anchor="w", padx=15, pady=10)

    # ==========================================
    # HALAMAN DATA BUKU
    # ==========================================
    def halaman_data_buku(self):
        self.bersihkan_konten()
        header = tk.Frame(self.main_frame, bg="#f0f0f5")
        header.pack(fill="x", padx=20, pady=15)
        
        tk.Label(header, text="📚 DATA BUKU", font=("Segoe UI", 16, "bold"), bg="#f0f0f5", fg=self.warna_utama).pack(side="left")
        tk.Button(header, text="➕ Tambah Buku", font=("Segoe UI", 10, "bold"), bg=self.warna_sukses, fg="white", relief="flat", cursor="hand2", command=self.dialog_tambah_buku).pack(side="right", padx=5)
        
        columns = ("ID", "Judul", "Penulis", "Kategori", "Penerbit", "Tahun", "Stok", "Status", "Rating")
        tree = ttk.Treeview(self.main_frame, columns=columns, height=20)
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        tree.column("#0", width=0, stretch=False)
        for col in columns:
            tree.column(col, anchor="center", width=120)
            tree.heading(col, text=col)
        
        for buku in self.db.database_buku:
            tree.insert("", "end", values=buku.ambil_data_tuple())
            
        def popupmenu(event):
            item = tree.selection()[0] if tree.selection() else None
            if item:
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="🗑️ Hapus Buku", command=lambda: self._hapus_buku(tree))
                menu.post(event.x_root, event.y_root)
        tree.bind("<Button-3>", popupmenu)

    def _hapus_buku(self, tree):
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin menghapus buku ini?"):
            item = tree.selection()[0]
            id_buku = tree.item(item)['values'][0]
            self.db.database_buku = [b for b in self.db.database_buku if b.id_buku != id_buku]
            self.db.simpan_data() # UPDATE JSON
            messagebox.showinfo("✅ Berhasil", "Buku berhasil dihapus!")
            self.halaman_data_buku()

    def dialog_tambah_buku(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Tambah Buku Baru")
        dialog.configure(bg="white")
        
        tk.Label(dialog, text="Informasi Buku", font=("Segoe UI", 14, "bold"), bg="white", fg=self.warna_utama).pack(pady=(20, 5))

        form_frame = tk.Frame(dialog, bg="white")
        form_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        fields = [("ID Buku", "entry"), ("Judul", "entry"), ("Penulis", "entry"), ("Kategori", "combo", ["Teknologi", "Fiksi", "Non-Fiksi", "Referensi"]),
                  ("Penerbit", "entry"), ("Tahun Terbit", "entry"), ("Stok", "entry"), ("ISBN", "entry")]
        
        entries = {}
        for i, field in enumerate(fields):
            tk.Label(form_frame, text=field[0] + ":", font=("Segoe UI", 10, "bold"), bg="white").grid(row=i, column=0, sticky="w", padx=10, pady=6)
            if field[1] == "entry":
                entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=32, bg="#f5f5f5", relief="solid", borderwidth=1)
                entry.grid(row=i, column=1, padx=10, pady=6, ipady=4)
                entries[field[0]] = entry
            elif field[1] == "combo":
                combo = ttk.Combobox(form_frame, values=field[2], state="readonly", width=30, font=("Segoe UI", 10))
                combo.grid(row=i, column=1, padx=10, pady=6)
                entries[field[0]] = combo
        
        def simpan():
            try:
                id_buku = entries["ID Buku"].get().strip()
                judul = entries["Judul"].get().strip()
                penulis = entries["Penulis"].get().strip()
                kategori = entries["Kategori"].get()
                penerbit = entries["Penerbit"].get().strip()
                tahun = entries["Tahun Terbit"].get().strip()
                stok = entries["Stok"].get().strip()
                isbn = entries["ISBN"].get().strip()
                
                if not all([id_buku, judul, penulis, kategori, penerbit, tahun, stok]):
                    messagebox.showwarning("Peringatan", "Semua field harus diisi!")
                    return
                
                tahun_int = int(tahun)
                stok_int = int(stok)
                
                buku_baru = Buku(id_buku, judul, penulis, kategori, penerbit, tahun_int, stok_int, isbn)
                self.db.database_buku.append(buku_baru)
                self.db.simpan_data() # UPDATE JSON
                
                messagebox.showinfo("✅ Berhasil", f"Buku '{judul}' berhasil ditambahkan ke database permanen!")
                dialog.destroy()
                self.halaman_data_buku()
            except ValueError:
                messagebox.showerror("Error", "Tahun Terbit dan Stok harus berupa angka yang valid!")
        
        tk.Button(dialog, text="Simpan Buku Ke Database", font=("Segoe UI", 10, "bold"), bg=self.warna_sukses, fg="white", relief="flat", cursor="hand2", command=simpan).pack(side="bottom", fill="x", padx=30, pady=20, ipady=8)

    # ==========================================
    # HALAMAN DATA ANGGOTA
    # ==========================================
    def halaman_data_anggota(self):
        self.bersihkan_konten()
        header = tk.Frame(self.main_frame, bg="#f0f0f5")
        header.pack(fill="x", padx=20, pady=15)
        
        tk.Label(header, text="👥 DATA ANGGOTA", font=("Segoe UI", 16, "bold"), bg="#f0f0f5", fg=self.warna_utama).pack(side="left")
        tk.Button(header, text="➕ Tambah Anggota", font=("Segoe UI", 10, "bold"), bg=self.warna_sukses, fg="white", relief="flat", cursor="hand2", command=self.dialog_tambah_anggota).pack(side="right", padx=5)
        
        columns = ("ID", "NIM", "Nama", "Email", "Telepon", "Alamat", "Status", "Denda")
        tree = ttk.Treeview(self.main_frame, columns=columns, height=20)
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        tree.column("#0", width=0, stretch=False)
        widths = [60, 90, 150, 180, 130, 180, 80, 100]
        for col, width in zip(columns, widths):
            tree.column(col, anchor="center", width=width)
            tree.heading(col, text=col)
        
        for anggota in self.db.database_anggota:
            denda_text = f"Rp {anggota.denda_menumpuk:,.0f}" if anggota.denda_menumpuk > 0 else "-"
            data = anggota.ambil_data_tuple() + (denda_text,)
            tree.insert("", "end", values=data)
            
        def popupmenu(event):
            item = tree.selection()[0] if tree.selection() else None
            if item:
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="🗑️ Hapus Anggota", command=lambda: self._hapus_anggota(tree))
                menu.post(event.x_root, event.y_root)
        tree.bind("<Button-3>", popupmenu)

    def _hapus_anggota(self, tree):
        if messagebox.askyesno("Konfirmasi", "Hapus anggota ini?"):
            item = tree.selection()[0]
            id_anggota = tree.item(item)['values'][0]
            self.db.database_anggota = [a for a in self.db.database_anggota if a.id_entitas != id_anggota]
            self.db.simpan_data() # UPDATE JSON
            messagebox.showinfo("✅ Berhasil", "Anggota berhasil dihapus!")
            self.halaman_data_anggota()

    def dialog_tambah_anggota(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Tambah Anggota Baru")
        dialog.configure(bg="white")
        
        tk.Label(dialog, text="Informasi Anggota", font=("Segoe UI", 14, "bold"), bg="white", fg=self.warna_utama).pack(pady=(20, 5))

        form_frame = tk.Frame(dialog, bg="white")
        form_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        fields = [("ID Anggota", "entry"), ("NIM/NPM", "entry"), ("Nama Lengkap", "entry"), ("Email", "entry"), ("No. Telepon", "entry"), ("Alamat", "entry")]
        entries = {}
        
        for i, (label, type_field) in enumerate(fields):
            tk.Label(form_frame, text=label + ":", font=("Segoe UI", 10, "bold"), bg="white").grid(row=i, column=0, sticky="w", padx=10, pady=6)
            entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=32, bg="#f5f5f5", relief="solid", borderwidth=1)
            entry.grid(row=i, column=1, padx=10, pady=6, ipady=4)
            entries[label] = entry
        
        def simpan():
            id_anggota = entries["ID Anggota"].get().strip()
            nim = entries["NIM/NPM"].get().strip()
            nama = entries["Nama Lengkap"].get().strip()
            email = entries["Email"].get().strip()
            telepon = entries["No. Telepon"].get().strip()
            alamat = entries["Alamat"].get().strip()
            
            if not all([id_anggota, nim, nama, email, telepon, alamat]):
                messagebox.showwarning("Peringatan", "Semua field harus diisi!")
                return
            
            anggota_baru = Anggota(id_anggota, nim, nama, email, telepon, alamat)
            self.db.database_anggota.append(anggota_baru)
            self.db.simpan_data() # UPDATE JSON
            
            messagebox.showinfo("✅ Berhasil", f"Anggota '{nama}' berhasil ditambahkan ke database permanen!")
            dialog.destroy()
            self.halaman_data_anggota()
        
        tk.Button(dialog, text="Simpan Anggota Ke Database", font=("Segoe UI", 10, "bold"), bg=self.warna_sukses, fg="white", relief="flat", cursor="hand2", command=simpan).pack(side="bottom", fill="x", padx=30, pady=20, ipady=8)

    # ==========================================
    # HALAMAN PEMINJAMAN
    # ==========================================
    def halaman_peminjaman(self):
        self.bersihkan_konten()
        header = tk.Frame(self.main_frame, bg="#f0f0f5")
        header.pack(fill="x", padx=20, pady=15)
        
        tk.Label(header, text="🔄 PEMINJAMAN BUKU", font=("Segoe UI", 16, "bold"), bg="#f0f0f5", fg=self.warna_utama).pack(side="left")
        tk.Button(header, text="➕ Pinjam Buku", font=("Segoe UI", 10, "bold"), bg=self.warna_sukses, fg="white", relief="flat", cursor="hand2", command=self.dialog_pinjam_buku).pack(side="right", padx=5)
        
        columns = ("ID", "Anggota", "Buku", "Tgl Pinjam", "Tgl Kembali", "Status", "Denda")
        tree = ttk.Treeview(self.main_frame, columns=columns, height=20)
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        tree.column("#0", width=0, stretch=False)
        widths = [70, 120, 150, 100, 100, 100, 100]
        for col, width in zip(columns, widths):
            tree.column(col, anchor="center", width=width)
            tree.heading(col, text=col)
        
        for pinjam in self.db.database_peminjaman:
            tree.insert("", "end", values=pinjam.ambil_data_tuple())

    def dialog_pinjam_buku(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Pinjam Buku")
        dialog.geometry("500x350")
        dialog.configure(bg="white")
        
        tk.Label(dialog, text="Pilih Anggota:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w", padx=20, pady=(20, 5))
        anggota_combo = ttk.Combobox(dialog, values=[f"{a.id_entitas} - {a.nama}" for a in self.db.database_anggota], state="readonly", width=40)
        anggota_combo.pack(padx=20, pady=5)
        
        tk.Label(dialog, text="Pilih Buku:", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w", padx=20, pady=(15, 5))
        buku_combo = ttk.Combobox(dialog, values=[f"{b.id_buku} - {b.judul}" for b in self.db.database_buku if b.stok > 0], state="readonly", width=40)
        buku_combo.pack(padx=20, pady=5)
        
        tk.Label(dialog, text="Durasi Peminjaman (hari):", font=("Segoe UI", 9, "bold"), bg="white").pack(anchor="w", padx=20, pady=(15, 5))
        durasi_spin = ttk.Spinbox(dialog, from_=1, to=30, width=10)
        durasi_spin.pack(padx=20, pady=5)
        durasi_spin.set(7)
        
        def simpan():
            if not anggota_combo.get() or not buku_combo.get():
                return messagebox.showwarning("Peringatan", "Pilih anggota dan buku!")
            
            anggota_id = anggota_combo.get().split(" - ")[0]
            buku_id = buku_combo.get().split(" - ")[0]
            durasi = int(durasi_spin.get())
            
            anggota = next((a for a in self.db.database_anggota if a.id_entitas == anggota_id), None)
            buku = next((b for b in self.db.database_buku if b.id_buku == buku_id), None)
            
            id_pinjam = f"PIN-{len(self.db.database_peminjaman) + 1:03d}"
            peminjaman = Peminjaman(id_pinjam, anggota, buku, durasi)
            buku.kurangi_stok()
            self.db.database_peminjaman.append(peminjaman)
            
            self.db.simpan_data()
            
            messagebox.showinfo("✅ Berhasil", f"Peminjaman berhasil!\n\nJatuh Tempo: {peminjaman.tanggal_jatuh_tempo.strftime('%d/%m/%Y')}")
            dialog.destroy()
            self.halaman_peminjaman()
        
        tk.Button(dialog, text="Proses Peminjaman", font=("Segoe UI", 10, "bold"), bg=self.warna_sukses, fg="white", relief="flat", cursor="hand2", command=simpan).pack(pady=20, ipady=8, fill="x", padx=20)

    # ==========================================
    # HALAMAN PENGEMBALIAN
    # ==========================================
    def halaman_pengembalian(self):
        self.bersihkan_konten()
        header = tk.Frame(self.main_frame, bg="#f0f0f5")
        header.pack(fill="x", padx=20, pady=15)
        tk.Label(header, text="↩️ PENGEMBALIAN BUKU", font=("Segoe UI", 16, "bold"), bg="#f0f0f5", fg=self.warna_utama).pack(side="left")
        
        peminjaman_aktif = [p for p in self.db.database_peminjaman if p.status == "Dipinjam"]
        
        if not peminjaman_aktif:
            tk.Label(self.main_frame, text="📭 Tidak ada peminjaman aktif", font=("Segoe UI", 12), bg="#f0f0f5", fg="gray").pack(pady=50)
            return
        
        columns = ("ID", "Anggota", "Buku", "Tgl Pinjam", "Jatuh Tempo", "Terlambat?")
        tree = ttk.Treeview(self.main_frame, columns=columns, height=15)
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        tree.column("#0", width=0, stretch=False)
        widths = [70, 120, 150, 100, 100, 100]
        for col, width in zip(columns, widths):
            tree.column(col, anchor="center", width=width)
            tree.heading(col, text=col)
        
        for pinjam in peminjaman_aktif:
            terlambat = "⚠️ YA" if datetime.now() > pinjam.tanggal_jatuh_tempo else "❌ Tidak"
            data = (pinjam.id_pinjam, pinjam.anggota.nama, pinjam.buku.judul,
                   pinjam.tanggal_pinjam.strftime("%d/%m/%Y"),
                   pinjam.tanggal_jatuh_tempo.strftime("%d/%m/%Y"), terlambat)
            tree.insert("", "end", values=data)
        
        tk.Button(self.main_frame, text="↩️ Kembalikan Buku Terpilih", font=("Segoe UI", 10, "bold"), bg=self.warna_aksen, fg="white", relief="flat", cursor="hand2", command=lambda: self._proses_pengembalian(tree)).pack(pady=10, ipady=8, fill="x", padx=20)

    def _proses_pengembalian(self, tree):
        if not tree.selection():
            messagebox.showwarning("Peringatan", "Pilih peminjaman yang akan dikembalikan dari tabel!")
            return
        
        item = tree.selection()[0]
        id_pinjam = tree.item(item)['values'][0]
        pinjam = next((p for p in self.db.database_peminjaman if p.id_pinjam == id_pinjam), None)
        
        if not pinjam: return

        dialog = tk.Toplevel(self.root)
        dialog.title("Opsi Pengembalian")
        dialog.geometry("400x350")
        dialog.configure(bg="white")

        tk.Label(dialog, text="Detail Pengembalian:", font=("Segoe UI", 12, "bold"), bg="white", fg=self.warna_utama).pack(pady=(15,5))
        tk.Label(dialog, text=f"Buku: {pinjam.buku.judul}\nAnggota: {pinjam.anggota.nama}", font=("Segoe UI", 10), bg="white").pack(pady=5)
        
        def kembalikan_sekarang():
            self._eksekusi_kembali(pinjam, datetime.now(), dialog)

        def kembalikan_custom():
            try:
                tgl_str = entry_tgl.get().strip()
                tgl_custom = datetime.strptime(tgl_str, "%d/%m/%Y")
                self._eksekusi_kembali(pinjam, tgl_custom, dialog)
            except ValueError:
                messagebox.showerror("Error", "Format tanggal salah! Gunakan format DD/MM/YYYY")

        tk.Button(dialog, text="✅ Kembalikan Sekarang (Hari Ini)", font=("Segoe UI", 10, "bold"), bg=self.warna_sukses, fg="white", relief="flat", cursor="hand2", command=kembalikan_sekarang).pack(pady=15, fill="x", padx=30, ipady=8)
        tk.Label(dialog, text="- ATAU KEMBALIKAN DI TANGGAL LAIN -", font=("Segoe UI", 8, "bold"), bg="white", fg="gray").pack(pady=5)
        
        entry_tgl = tk.Entry(dialog, font=("Segoe UI", 11), justify="center", bg="#f5f5f5", relief="solid", borderwidth=1)
        entry_tgl.pack(pady=5, padx=50, fill="x", ipady=5)
        entry_tgl.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        tk.Button(dialog, text="Proses Tanggal Manual", font=("Segoe UI", 9, "bold"), bg=self.warna_aksen, fg="white", relief="flat", cursor="hand2", command=kembalikan_custom).pack(pady=5, fill="x", padx=30, ipady=5)

    def _eksekusi_kembali(self, pinjam, tanggal_pengembalian, dialog):
        denda, hari_terlambat = pinjam.kembalikan_buku(tanggal_pengembalian)
        pinjam.buku.tambah_stok()
        
        if hari_terlambat > 0:
            pinjam.anggota.tambah_denda(denda)
            messagebox.showinfo("⚠️ Pengembalian Terlambat",
                              f"Buku dikembalikan melewati jatuh tempo!\n\n"
                              f"Hari Terlambat: {hari_terlambat} hari\n"
                              f"Denda: Rp {denda:,.0f}\n\n"
                              f"Total Tagihan Anggota: Rp {pinjam.anggota.denda_menumpuk:,.0f}")
        else:
            messagebox.showinfo("✅ Tepat Waktu", f"Terima kasih telah mengembalikan buku {pinjam.buku.judul} dengan tepat waktu!")
        
        self.db.simpan_data()
        dialog.destroy()
        self.halaman_pengembalian()

    # ==========================================
    # HALAMAN DENDA
    # ==========================================
    def halaman_denda(self):
        self.bersihkan_konten()
        tk.Label(self.main_frame, text="⏰ MANAJEMEN DENDA", font=("Segoe UI", 16, "bold"), bg="#f0f0f5", fg=self.warna_utama).pack(fill="x", padx=20, pady=15)
        
        columns = ("ID", "Nama", "Email", "Denda Menumpuk", "Status")
        tree = ttk.Treeview(self.main_frame, columns=columns, height=15)
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        tree.column("#0", width=0, stretch=False)
        widths = [70, 150, 180, 120, 150]
        for col, width in zip(columns, widths):
            tree.column(col, anchor="center", width=width)
            tree.heading(col, text=col)
        
        for anggota in self.db.database_anggota:
            status = "⚠️ Berdenda" if anggota.denda_menumpuk > 0 else "✅ Lunas"
            data = (anggota.id_entitas, anggota.nama, anggota.email, f"Rp {anggota.denda_menumpuk:,.0f}", status)
            tree.insert("", "end", values=data)
            
        tk.Button(self.main_frame, text="💰 Bayar Denda", font=("Segoe UI", 10, "bold"), bg=self.warna_sukses, fg="white", relief="flat", cursor="hand2", command=lambda: self._dialog_bayar_denda(tree)).pack(pady=10, ipady=8, fill="x", padx=20)

    def _dialog_bayar_denda(self, tree):
        if not tree.selection():
            messagebox.showwarning("Peringatan", "Pilih anggota!")
            return
        
        item = tree.selection()[0]
        id_anggota = tree.item(item)['values'][0]
        anggota = next((a for a in self.db.database_anggota if a.id_entitas == id_anggota), None)
        
        if not anggota or anggota.denda_menumpuk == 0:
            return messagebox.showinfo("Info", "Anggota ini tidak memiliki denda")
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Bayar Denda")
        dialog.geometry("400x300")
        dialog.configure(bg="white")
        
        tk.Label(dialog, text=f"Anggota: {anggota.nama}", font=("Segoe UI", 10, "bold"), bg="white").pack(pady=10)
        tk.Label(dialog, text=f"Denda Menumpuk: Rp {anggota.denda_menumpuk:,.0f}", font=("Segoe UI", 10, "bold"), bg="white", fg=self.warna_warning).pack(pady=5)
        tk.Label(dialog, text="Jumlah Pembayaran (Rp):", font=("Segoe UI", 9), bg="white").pack(anchor="w", padx=20, pady=(15, 5))
        
        jumlah_entry = tk.Entry(dialog, font=("Segoe UI", 10), width=20)
        jumlah_entry.pack(padx=20, pady=5)
        
        def proses_bayar():
            try:
                jumlah = float(jumlah_entry.get())
                if jumlah <= 0 or jumlah > anggota.denda_menumpuk:
                    return messagebox.showerror("Error", "Jumlah pembayaran tidak valid!")
                
                if anggota.bayar_denda(jumlah):
                    self.db.simpan_data()
                    messagebox.showinfo("✅ Berhasil", f"Pembayaran diterima!\n\nSisa Denda: Rp {anggota.denda_menumpuk:,.0f}")
                    dialog.destroy()
                    self.halaman_denda()
            except ValueError:
                messagebox.showerror("Error", "Format jumlah tidak valid!")
        
        tk.Button(dialog, text="Terima Pembayaran", font=("Segoe UI", 10, "bold"), bg=self.warna_sukses, fg="white", relief="flat", cursor="hand2", command=proses_bayar).pack(pady=20, ipady=8, fill="x", padx=20)

    # ==========================================
    # HALAMAN LAPORAN & PENGATURAN
    # ==========================================
    def halaman_laporan(self):
        self.bersihkan_konten()
        tk.Label(self.main_frame, text="📊 LAPORAN & STATISTIK", font=("Segoe UI", 16, "bold"), bg="#f0f0f5", fg=self.warna_utama).pack(fill="x", padx=20, pady=15)
        laporan = LaporanGenerator(self.db.database_buku, self.db.database_anggota, self.db.database_peminjaman)
        stats = laporan.statistik_perpustakaan()
        content = tk.Frame(self.main_frame, bg="white", relief="flat")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        laporan_text = f"LAPORAN PERPUSTAKAAN\nTanggal: {datetime.now().strftime('%d/%m/%Y')}\n\nSTATISTIK BUKU\nTotal: {stats['total_buku']}\n"
        text_widget = tk.Text(content, font=("Courier", 10), bg="white", relief="flat", height=20, width=70)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert(1.0, laporan_text)
        text_widget.config(state="disabled")

    def halaman_pengaturan(self):
        self.bersihkan_konten()
        tk.Label(self.main_frame, text="⚙️ PENGATURAN SISTEM", font=("Segoe UI", 16, "bold"), bg="#f0f0f5", fg=self.warna_utama).pack(fill="x", padx=20, pady=15)
        settings = tk.Frame(self.main_frame, bg="white", relief="flat")
        settings.pack(fill="both", expand=True, padx=20, pady=10)
        tk.Label(settings, text="⏰ Tarif Denda", font=("Segoe UI", 12, "bold"), bg="white", fg=self.warna_utama).pack(anchor="w", padx=15, pady=(15, 10))
        tk.Label(settings, text=f"Tarif Per Hari: Rp {DendaManager.TARIF_PERHARI:,.0f}", font=("Segoe UI", 10), bg="white").pack(anchor="w", padx=30, pady=5)

# ==========================================
# MAIN PROGRAM
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = SistemPerpustakaanApp(root)
    root.mainloop()