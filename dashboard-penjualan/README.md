# Dashboard Penjualan

Dashboard interaktif untuk memahami penjualan: kategori mana yang paling besar, mana yang paling menguntungkan, bagaimana tren bulanannya, dan wilayah serta produk mana yang paling berpengaruh. Dibuat sebagai proyek latihan kelas Data Analyst UNSIKA Study Club.

## Demo

<!-- Ganti dengan link Streamlit Community Cloud-mu -->
https://nama-kamu.streamlit.app

## Tujuan

Menjawab lima pertanyaan dari data penjualan:

- Kategori produk mana yang menyumbang penjualan terbesar, dan apakah itu juga yang paling menguntungkan?

- Bagaimana tren penjualan dan jumlah transaksi dari bulan ke bulan?

- Produk dan wilayah mana yang paling berpengaruh?

- Apakah harga jual yang tinggi selalu diikuti modal yang tinggi, dan angka mana saja yang saling berhubungan?

- Apakah ada transaksi yang merugi?

## Sumber Data

`data/data.csv` (sama dengan `data-bersih.csv` hasil cleaning pertemuan 4): 129 transaksi penjualan, Januari sampai Maret 2026, satuan rupiah. Data latihan, tidak berisi data pribadi pelanggan.

| Kolom | Isi |
|---|---|
| `id_pesanan` | Nomor pesanan |
| `tanggal` | Tanggal transaksi |
| `nama_produk`, `kategori` | Produk dan kategorinya |
| `harga`, `jumlah`, `modal` | Harga jual, jumlah terjual, dan modal per unit |
| `wilayah` | Kota tempat transaksi |
| `nilai_penjualan`, `untung` | Harga kali jumlah, dan keuntungan |

## Isi Dashboard

**Filter (panel samping):** kategori, wilayah, bulan, dan saklar **Sertakan Laptop Gaming**. Filter yang dikosongkan berarti semua ditampilkan. Saklar Laptop Gaming dipakai untuk memeriksa pengaruh satu transaksi yang jauh di luar kebiasaan.

**Lima angka ringkasan:** total penjualan, total untung, margin untung, jumlah transaksi, dan rata-rata nilai pesanan.

| Tab | Isi |
|---|---|
| **Ringkasan** | Pie chart porsi penjualan per kategori, bar chart margin untung per kategori, line chart tren penjualan per bulan, dan bar chart jumlah transaksi per bulan |
| **Produk dan Wilayah** | Top 5 produk, penjualan per wilayah, dan heatmap wilayah × kategori |
| **Hubungan Angka** | Heatmap korelasi antar angka, dan scatter plot harga jual vs modal (skala log, lengkap dengan garis impas) |
| **Insight** | Temuan otomatis dari data yang sedang tampil, lengkap dengan rekomendasi |
| **Data** | Tabel lengkap dan tombol unduh CSV |

Semua grafik interaktif: arahkan kursor untuk melihat angka, dan tarik untuk zoom.

## Cara Menjalankan

1. Clone repository ini.

2. Buat dan aktifkan virtual environment, lalu instal library:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   Di Mac atau Linux, aktifkan dengan `source .venv/bin/activate`.

3. Jalankan dashboard:

   ```bash
   streamlit run app.py
   ```

4. Buka alamat yang tampil di terminal (biasanya `http://localhost:8501`).

## Insight Utama

- **Penjualan terbesar belum tentu untung terbaik.** Elektronik menyumbang 59,2% penjualan, tapi margin untungnya hanya 15,5%, terendah dari semua kategori. Buku hanya 5,2% dari penjualan, tapi margin 34,3%.

- **Satu transaksi mengubah cerita.** Penjualan Februari turun 57,4% dari Januari, padahal jumlah transaksi stabil (40, 47, 42). Penyebabnya satu transaksi Laptop Gaming di Januari. Tanpa transaksi itu, penjualan Februari justru naik 61,8%.

- **Korelasi bisa menipu.** Harga dan modal berkorelasi 1,00 (hampir sempurna), tapi itu dibentuk satu transaksi Laptop Gaming. Tanpa transaksi itu, korelasinya 0,95.

- **Bandung terlihat sebagai wilayah terbesar** (51,1% penjualan), hampir semuanya dari Elektronik di Bandung, yaitu transaksi Laptop Gaming tadi.

- **Ada 3 transaksi rugi** (harga jual di bawah modal) dengan total kerugian Rp 349.000.

- **Rekomendasi:** dorong kategori bermargin tinggi (Buku, Makanan, Fashion), periksa modal Elektronik, dan tinjau harga jual produk yang rugi.

## Tech Stack

- Python 3.13

- Streamlit (dashboard)

- Pandas (pengolahan data)

- Plotly (grafik interaktif)

## Struktur Folder

```text
dashboard-penjualan/
├── app.py                 kode dashboard
├── data/
│   └── data.csv           dataset
├── requirements.txt       daftar library
├── .gitignore             file yang tidak ikut ke GitHub
├── .streamlit/
│   └── config.toml        pengaturan tampilan (font)
└── README.md
```

## Anggota

- Nama kamu
