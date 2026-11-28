---
name: ai-master-rules-edukasi-recycle-bin
description: >
  File induk aturan AI untuk proyek Game Edukasi Pemilahan Sampah Organik & Anorganik
  (Construct 2 r262 / HTML5 / APK Android - Resolusi 1280 x 720 piksel) untuk Siswa Kelas IV SD.
---

# DAFTAR ATURAN, STANDAR ASET VISUAL, & PEDOMAN TEKNIS CONSTRUCT 2

Dokumen ini menjadi pedoman utama (memori proyek) yang wajib dipatuhi oleh AI setiap kali memproses aset gambar, membuat script utilitas, atau memodifikasi proyek **Edukasi Recycle Bin (Pilah Sampah Yuk!)**.

---

## 1. Spesifikasi Proyek & Target Platform

- **Judul Game**: *Pilah Sampah Yuk! — Game Edukasi Pemilahan Sampah Organik dan Anorganik*
- **Target Pengguna**: Siswa Kelas IV Sekolah Dasar (SD)
- **Game Engine**: Construct 2 (r262) -> Ekspor HTML5 / Cordova / Intel XDK (Android APK)
- **Resolusi Layar Proyek (Viewport / Window Size)**: **`1280 x 720` piksel (Landscape 16:9)**
- **Prinsip Ukuran Aset**: Ukuran ideal setiap aset adalah **1 kali ukuran tampil aslinya di layar (`1:1 display scale`)** dengan **angka piksel genap** agar:
  1. Tampilan tetap tajam di layar HP Android.
  2. Tidak memicu peringatan ukuran berlebih (*oversized texture/image memory warning*) di Construct 2.
  3. Ukuran file APK tetap ringan dan hemat RAM/VRAM perangkat mobile.

---

## 2. Tabel Standar Ukuran Piksel Aset Game (`1280 x 720` px)

Seluruh aset yang disimpan ke dalam `assets/assets real/` dan `assets/Layout_Menu/` **wajib** mengikuti standar ukuran piksel berikut:

| Kategori Aset | Contoh Objek di Game | Ukuran Ideal (Lebar x Tinggi) | Format & Catatan Teknis |
| :--- | :--- | :--- | :--- |
| **Latar Belakang (Background)** | `Bg_Menu`, `Bg_Materi`, `Bg_Gameplay`, `Background.jpg` | **`1280 x 720` px** | **JPG (kualitas 80–85%)**, tanpa area transparan agar ukuran file **di bawah 250 KB**. |
| **Banner Judul Utama** | `Banner_Judul` / `judul_pilah_sampah.png` di Halaman Menu | **`660 x 220` px** | **PNG transparan** (sekitar separuh lebar layar bagian atas). |
| **Papan Dialog & Pop-up** | Pop-up *Benar!* / *Coba Lagi!*, Papan Soal Kuis, Papan Dialog, Papan Skor Akhir | **`640 x 380` px** *(atau `720 x 420` px)* | **PNG transparan**, cukup luas menampung teks soal dan penjelasan tanpa menutupi seluruh layar. |
| **Tombol Menu & Opsi Kuis** | `Btn_Mulai`, `Btn_Materi`, `Btn_Simulasi`, Tombol Pilihan A/B/C | **`380 x 96` px** *(atau `420 x 90` px)* | **PNG transparan**, lebar dan nyaman ditekan jari siswa kelas IV SD. |
| **Tempat Sampah (Bins)** | Tong Organik & Tong Anorganik | **`200 x 260` px** | **PNG transparan**, ukuran cukup besar sebagai target area *drop* sampah. |
| **Karakter Siswa SD (Menu/Dialog)** | Karakter di Menu / Dialog (`Karakter_Menu`) | **`260 x 380` px** | **PNG transparan**, proporsional untuk tampilan menu utama dan narasi dialog. |
| **Karakter Siswa SD (Simulasi)** | Karakter berjalan di Simulasi | **`120 x 160` px** | **PNG transparan**, dibuat lebih kecil agar proporsional dengan halaman sekolah pada mode simulasi. |
| **Objek Sampah** | Kulit jeruk, sisa ikan/nasi, gelas plastik, sedotan, daun layu, ranting (`ObjekSampah`) | **`140 x 140` px** *(atau `150 x 150` px)* | **PNG transparan persegi (`1:1`)** agar seragam saat dimasukkan ke dalam satu Sprite multi-frame. |
| **Tombol Ikon & Navigasi** | Pengaturan, Info/Credits, Keluar, Home, Kembali, Lanjut, Ulang, Suara ON/OFF | **`100 x 100` px** *(atau `90 x 90` px)* | **PNG transparan persegi (`1:1`)**, standar area sentuh tombol ikon di layar ponsel. |
| **Kontrol Arah Simulasi** | Tombol panah D-Pad (Atas, Bawah, Kiri, Kanan) | **`100 x 100` px** | **PNG transparan persegi (`1:1`)** di pojok kiri bawah layar simulasi. |
| **Indikator HUD: Rating Bintang** | `RatingBintang` (1–3 bintang) | **`320 x 120` px** | **PNG transparan** untuk elemen rating bintang. |
| **Indikator HUD: Papan Skor** | Papan Skor kecil (`hud_skor.png`, `hud_waktu_papan.png`) | **`220 x 70` px** | **PNG transparan** untuk informasi skor di bagian atas layar gameplay. |
| **Indikator HUD: Ikon Waktu** | Ikon Waktu / Timer (`hud_waktu.png`) | **`64 x 64` px** | **PNG transparan persegi (`1:1`)** untuk ikon timer di atas layar gameplay. |

---

## 3. Tiga Aturan Teknis Wajib Sebelum Memasukkan Aset ke Construct 2

1. **Gunakan Selalu Angka Piksel Genap**:
   - Pastikan lebar (`width`) dan tinggi (`height`) gambar **selalu bernilai genap** (misalnya `140 x 140`, `380 x 96`, `640 x 380` — **bukan** angka ganjil seperti `141 x 143`).
   - Angka genap memastikan titik pusat (`Origin -> Middle`) jatuh tepat di koordinat bulat sehingga gambar tidak tampak buram (*blur* / *sub-pixel rendering*) di layar HP.

2. **Samakan Ukuran Kanvas untuk Objek Satu Grup (Multi-Frame)**:
   - Untuk aset yang digabung ke dalam satu objek Sprite berbeda frame di Construct 2—seperti semua gambar sampah di `ObjekSampah` (`140 x 140` px), tombol `Suara ON & OFF` (`100 x 100` px), tombol navigasi (`100 x 100` px), serta `RatingBintang` (`320 x 120` px)—**wajib disimpan dalam ukuran piksel kanvas yang sama persis** agar ukurannya tidak berubah-ubah atau bergeser saat pergantian frame di tengah permainan.

3. **Hapus Latar Putih Sebelum Masuk Construct 2**:
   - Jangan mengandalkan alat *Magic Wand* dan *Crop* bawaan Construct 2 r262 karena sering menyisakan piksel transparan tipis (*halo* putih) atau merusak warna putih di dalam gambar.
   - Bersihkan latar putih terlebih dahulu menggunakan tool proyek `hapus-bg.py` / `hapus-bg.bat` (menggunakan *exterior flood-fill* + *edge anti-aliasing* + *color decontamination* sehingga warna putih internal seperti baju seragam SD, nasi, mata, gelas plastik, dan teks tetap utuh), lalu ubah ukurannya sesuai tabel standar di atas.
   - Saat diimpor ke Construct 2, pengguna cukup klik **Open** dan langsung atur **Origin -> Middle**.

---

## 4. Struktur Folder & Perkakas Proyek (`dev-menu` & `hapus-bg`)

- `run.bat` / `dev-menu.bat` / `dev-menu.ps1`:
  - `run.bat` otomatis membuka VS Code ke folder proyek (detached via `code.cmd`) dan menjalankan `dev-menu.bat` di jendela terminal yang sama.
  - Menu peluncur pengembangan proyek (semua tab terminal baru dibuka di jendela Windows Terminal aktif via `wt -w 0 new-tab`, dilengkapi pengecekan anti-duplikat):
    - `[1]` Buka Semua (Construct 2 + Tab Terminal `OpenCode`, `OMP`, `Root CMD` di WT yang sama + 4 tab File Explorer + Browser Gemini & ChatGPT)
    - `[2]` Construct 2 (`D:\Apps\Construct 2\Construct2.exe`)
    - `[3]` Browser AI (Tab Gemini + Tab ChatGPT, anti-duplikat)
    - `[4]` / `[E]` File Explorer (1 jendela dengan 4 tab: `root`, `assets`, `docs`, `Downloads`, reuse jendela jika sudah terbuka)
    - `[5]` Hapus Background Gambar (GUI `hapus-bg.py`)
    - `[6]` Tab Terminal Baru (`OpenCode`, `OMP`, `Root CMD` di jendela Windows Terminal yang sama)
- `hapus-bg.py` & `hapus-bg.bat`:
  - Tool GUI & CLI untuk menghapus background gambar menjadi PNG transparan serta memotong/menyesuaikan ukuran kanvas dengan angka piksel genap.
- `assets/Layout_Menu/`:
  - Berisi aset siap pakai untuk halaman Menu Utama (`Background.jpg` ukuran `1280x720` < 250 KB, `judul_pilah_sampah.png` ukuran `660x220`, tombol menu `380x96`, dan tombol ikon `100x100`).
- `assets/assets real/`:
  - Berisi seluruh pecahan aset gameplay, sampah (`140x140`), navigasi (`100x100`), pop-up & papan dialog/pertanyaan (`640x380`), karakter menu (`260x380`) & simulasi (`120x160`), serta indikator HUD (`320x120`, `220x70`, `64x64`).
