# Metode Iterasi (Titik Tetap) — Kalkulator Akar Persamaan Non-Linier

Aplikasi desktop (GUI) berbahasa Python untuk mencari **akar persamaan non-linier** menggunakan **Metode Iterasi (Titik Tetap / Fixed-Point Iteration)** sesuai Materi Praktikum Komputasi Numerik.

Cukup masukkan fungsi $f(x)$ dan $g(x)$ serta tebakan awal $x_0$, lalu aplikasi menampilkan **hasil akar**, **tabel iterasi lengkap**, dan **grafik cobweb (jalur tangga)** secara otomatis.

> **Project Metode Iterasi — Praktikum Komputasi Numerik**
> Kelompok 2

---

## Daftar Isi

1. [Apa itu Metode Iterasi?](#1-apa-itu-metode-iterasi)
2. [Fitur Aplikasi](#2-fitur-aplikasi)
3. [Source yang Diperlukan](#3-source-yang-diperlukan)
4. [Cara Instalasi & Menjalankan](#4-cara-instalasi--menjalankan)
5. [Tata Cara Penggunaan](#5-tata-cara-penggunaan)
6. [Contoh Input dan Output](#6-contoh-input-dan-output)
7. [Cara Membaca Hasil](#7-cara-membaca-hasil)
8. [Struktur Proyek](#8-struktur-proyek)
9. [Pemecahan Masalah](#9-pemecahan-masalah)
10. [Anggota Kelompok 4](#10-anggota-kelompok-4)

---

## 1. Apa itu Metode Iterasi?

Metode Iterasi (Titik Tetap) adalah metode dalam komputasi numerik yang digunakan untuk mencari nilai pendekatan dari suatu solusi persamaan non-linier $f(x) = 0$ dengan cara melakukan perhitungan berulang-ulang sampai mendapatkan hasil yang konvergen / mendekati nilai sebenarnya.

### Prinsip Kerja:
Persamaan $f(x) = 0$ diubah bentuk aljabar menjadi:
$$x = g(x)$$

Lalu ditentukan nilai tebakan awal $x_0$, dan dihitung secara berulang:
- $x_1 = g(x_0)$
- $x_2 = g(x_1)$
- $x_3 = g(x_2)$
- $\dots$
- $x_i = g(x_{i-1})$

### Algoritma (Sesuai Materi):
1. **Definisikan** fungsi $F(x)$ dan $g(x)$.
2. **Tentukan** toleransi error ($e$) dan iterasi maksimum ($N$).
3. **Tentukan** pendekatan awal $x_0$.
4. **Hitung** nilai $x$ iterasi berikutnya dari nilai $g(x)$ sebelumnya: $x_i = g(x_{i-1})$.
5. **Hitung** galat toleransi:
   $$e_{tol} = |g(x_i) - x_i|$$
6. **Kriteria Berhenti**: proses selesai jika $e_{tol} < e$ atau f(x) = 0 (konvergen). Jika sampai iterasi maksimum $N$ belum tercapai, maka nilai pendekatan adalah nilai $x$ pada iterasi terakhir.

---

## 2. Fitur Aplikasi

- **Form Input Terstruktur**:
  - `Fungsi F(X)`
  - `Pilihan Cara g(x)`: Menu dropdown untuk memilih salah satu dari 3 cara penurunan $g(x)$ secara otomatis, atau mode Manual untuk mengetik bebas.
    - **Cara 1**: Isolasi $x^2 \implies x = \sqrt{\frac{-bx - c}{a}}$
    - **Cara 2**: Isolasi $x \implies x = \frac{-ax^2 - c}{b}$
    - **Cara 3**: Faktorisasi $x \implies x = \frac{-c}{ax + b}$
  - `Fungsi g(x)`: Otomatis terisi sesuai Cara yang dipilih (atau dapat diketik manual).
  - `Pendekatan Awal (x₀)`
  - `Toleransi Error (e)`
  - `Iterasi Maksimum (N)`
  - `Jumlah Angka Desimal`
- **Pangkat Otomatis Jadi Superscript**: mengetik `x**2` langsung berubah menjadi `x²`.
- **Tabel Iterasi Lengkap**: menampilkan kolom `r`, `x`, `g(x)`, `f(x)`, `e_tol`, dan `validasi`. Baris solusi disorot dengan warna khusus.
- **Tombol Tampilkan Semua / Sembunyikan**: menampilkan hingga batas konvergensi atau seluruh baris iterasi hingga $N$.
- **Grafik Fungsi f(x) Interaktif**:
  - Kurva utama $y = f(x)$.
  - Titik pendekatan awal $x_0$ pada kurva.
  - Titik akar $(x^*, f(x^*))$ dengan penanda lingkaran merah dan koordinat.
  - Sumbu koordinat $X$ dan $Y$.
  - Fitur zoom (scroll mouse), geser (drag), dan reset (klik ganda).
- **Hasil Perhitungan**: menampilkan nilai akar $x$, $f(x)$, nomor iterasi tercapai, dan kalimat kesimpulan otomatis.
- **Deteksi Divergensi & Error Matematika**: mendeteksi bila fungsi $g(x)$ melompat ke tak hingga atau tidak terdefinisi (misal akar negatif).
- **Mode Terang dan Mode Gelap** (tombol bulan/matahari di sudut kiri atas).

---

## 3. Source yang Diperlukan

| Kebutuhan | Versi yang disarankan | Fungsi |
|---|---|---|
| **Python** | 3.9 atau lebih baru | Bahasa pemrograman utama |
| **PyQt6** | 6.4 atau lebih baru | Tampilan antarmuka desktop (GUI) |
| **Matplotlib** | 3.7 atau lebih baru | Menggambar grafik fungsi dan cobweb |
| **NumPy** | 1.24 atau lebih baru | Perhitungan titik kurva vektor |
| **SymPy** | 1.12 atau lebih baru | Membaca dan mengevaluasi rumus matematika |

---

## 4. Cara Instalasi & Menjalankan

```bash
# 1. Masuk ke folder proyek
cd metode_biseksi

# 2. Pasang library
pip install -r requirements.txt

# 3. Jalankan aplikasi
python main.py
```

---

## 5. Tata Cara Penggunaan

1. Isi form di **Panel Input**:
   - `Fungsi F(X)`: masukkan persamaan awal $f(x) = 0$ (contoh: `x**2 - 6x - 2`).
   - `Pilihan Cara g(x)`: pilih **Cara 1**, **Cara 2**, atau **Cara 3** untuk menurunkan fungsi $g(x)$ secara otomatis, atau pilih **Manual** jika ingin mengetik sendiri.
   - `Fungsi g(x)`: akan otomatis terisi sesuai cara yang dipilih (atau dapat diedit).
   - `Pendekatan Awal (x₀)`: tebakan nilai awal $x$.
   - `Toleransi Error (e)`: nilai batas galat, misal `0,001`.
   - `Iterasi Maksimum (N)`: batas perulangan, misal `10` atau `20`.
   - `Jumlah Angka Desimal`: presisi tampilan, misal `4`.
2. Tekan tombol **Hitung Akar** atau tekan `Enter`.
3. Periksa **Hasil Perhitungan**, baris-baris pada **Tabel Iterasi**, serta kurva $f(x)$ dan titik akarnya di **Grafik Fungsi**.
4. Tekan **Reset** bila ingin membersihkan isian.

---

## 6. Contoh Input dan Output (Sesuai Materi Slide)

### Latihan Slide: $F(x) = x^2 - 6x - 2$, $x_0 = 4$, $e = 0.001$

#### Pilihan Cara 2: $g(x) = \frac{-x^2 + 2}{-6}$
- **Input**:
  - `Fungsi F(X)`: `x**2 - 6x - 2`
  - `Fungsi g(x)`: `(-x**2 + 2)/-6`
  - `Pendekatan Awal (x₀)`: `4`
  - `Toleransi Error (e)`: `0,001`
  - `Iterasi Maksimum (N)`: `10`
  - `Jumlah Angka Desimal)`: `4`
- **Output**:
  - **Akar (x)**: `-0,3167`
  - **Iterasi**: `6`
  - **Kesimpulan**: `Akar fungsi berhasil ditemukan pada iterasi ke-6 dengan nilai x = -0,3167 dan toleransi e_tol < 0,0010.`

#### Pilihan Cara 1: $g(x) = \sqrt{6x + 2}$
- Menemukan akar positif $x \approx 6,3166$ secara konvergen.

---

## 7. Cara Membaca Hasil

- **r**: Nomor putaran iterasi ($1, 2, 3, \dots$).
- **x**: Nilai $x$ pada iterasi sekarang.
- **g(x)**: Nilai evaluasi fungsi iterasi $g(x)$, yang akan menjadi $x$ untuk iterasi berikutnya.
- **f(x)**: Nilai $f(x)$ di titik $x$.
- **e_tol**: Selisih galat $|g(x) - x|$.
- **validasi**: Bernilai **TRUE** bila $e_{tol} < e$ (syarat konvergensi terpenuhi).

---

## 8. Struktur Proyek

```
metode_biseksi/
├── main.py                     # Titik masuk aplikasi
├── requirements.txt            # Dependensi paket Python
├── README FINAL.md             # Dokumentasi panduan lengkap
├── backend/
│   ├── __init__.py
│   └── iteration_solver.py     # Logika Metode Iterasi Titik Tetap, parser, validasi
└── gui/
    ├── __init__.py
    ├── main_window.py          # Window utama & orkestrasi
    ├── input_panel.py          # Panel kiri form input
    ├── result_panel.py         # Panel tengah atas hasil akar
    ├── table_panel.py          # Panel tengah bawah tabel iterasi
    ├── graph_panel.py          # Panel kanan kontainer grafik
    ├── plotter.py              # Logika plotting matplotlib & cobweb
    └── theme.py                # Palet warna terang & gelap
```

---

## 9. Pemecahan Masalah

- **Iterasi Divergen?**
  Metode Iterasi Titik Tetap hanya konvergen jika $|g'(x)| < 1$ di sekitar akar. Jika divergen, cobalah bentuk aljabar $g(x)$ yang lain (seperti variasi pada slide: Cara 1, Cara 2, atau Cara 3).
- **Error Bilangan Negatif di Dalam Akar?**
  Jika $g(x) = \sqrt{\dots}$ menghasilkan nilai negatif pada tebakan $x$, aplikasi akan menangkap error tersebut dengan aman dan memberi tahu di tabel.

---

## 10. Anggota Kelompok 2

**Project Praktikum Komputasi Numerik**
- Muhammad Fathir
- Muhammad Irfan
- Dhawy Azzafran
- Naila Putri Syahnuza
- Kelompok 2
