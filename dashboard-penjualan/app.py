import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard Penjualan", layout="wide")


@st.cache_data
def baca_data():
    df = pd.read_csv("data/data.csv")
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df["bulan"] = df["tanggal"].dt.to_period("M").astype(str)
    return df


df = baca_data()

st.title("Dashboard Penjualan")
st.caption("Sumber data: data-bersih.csv, 129 transaksi, Januari sampai Maret 2026")

with st.expander("Cuplikan data (5 baris pertama)"):
    st.dataframe(df.head())


# ---------- Filter ----------
# Pilihan dibiarkan kosong = tampilkan semua.
def saring_data(data, kategori, wilayah, bulan, sertakan_laptop):
    hasil = data
    if kategori:
        hasil = hasil[hasil["kategori"].isin(kategori)]
    if wilayah:
        hasil = hasil[hasil["wilayah"].isin(wilayah)]
    if bulan:
        hasil = hasil[hasil["bulan"].isin(bulan)]
    if not sertakan_laptop:
        hasil = hasil[hasil["nama_produk"] != "Laptop Gaming (Bonus)"]
    return hasil


st.sidebar.header("Filter")
pilih_kategori = st.sidebar.multiselect(
    "Kategori", sorted(df["kategori"].unique()), placeholder="Semua kategori"
)
pilih_wilayah = st.sidebar.multiselect(
    "Wilayah", sorted(df["wilayah"].unique()), placeholder="Semua wilayah"
)
pilih_bulan = st.sidebar.multiselect(
    "Bulan", sorted(df["bulan"].unique()), placeholder="Semua bulan"
)
sertakan_laptop = st.sidebar.checkbox("Sertakan Laptop Gaming", value=True)
st.sidebar.caption(
    "Laptop Gaming adalah satu transaksi yang jauh di luar kebiasaan. "
    "Matikan untuk melihat pola tanpa transaksi itu."
)

data_tampil = saring_data(df, pilih_kategori, pilih_wilayah, pilih_bulan, sertakan_laptop)

if data_tampil.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Coba ubah pilihanmu.")
    st.stop()


# ---------- Angka ringkasan ----------
def rupiah(angka):
    return "Rp " + f"{angka:,.0f}".replace(",", ".")


def rupiah_ringkas(angka):
    """Untuk kartu angka yang sempit: 75804000 jadi '75,8 jt'."""
    if angka >= 1_000_000:
        return f"{angka / 1_000_000:.1f}".replace(".", ",") + " jt"
    return f"{angka / 1_000:.0f} rb"


def hitung_kpi(data):
    total = data["nilai_penjualan"].sum()
    untung = data["untung"].sum()
    transaksi = data["id_pesanan"].nunique()
    return total, untung, transaksi, total / transaksi


total, untung, transaksi, rata_rata = hitung_kpi(data_tampil)
margin = untung / total * 100

kol1, kol2, kol3, kol4, kol5 = st.columns(5, gap="small")
# help= menampilkan angka lengkap saat kursor diarahkan ke tanda tanya di kartu
kol1.metric("Penjualan", rupiah_ringkas(total), help=rupiah(total), border=True)
kol2.metric("Untung", rupiah_ringkas(untung), help=rupiah(untung), border=True)
kol3.metric("Margin Untung", f"{margin:.1f}%".replace(".", ","), border=True)
kol4.metric("Jumlah Transaksi", transaksi, border=True)
kol5.metric("Rata-rata Pesanan", rupiah_ringkas(rata_rata), help=rupiah(rata_rata), border=True)
st.caption("Nilai dalam rupiah (jt = juta, rb = ribu). Arahkan kursor ke tanda tanya untuk angka lengkap.")


# ---------- Tab dan grafik ringkasan ----------
def rapikan(fig):
    fig.update_layout(template="simple_white", font_family="Plus Jakarta Sans, sans-serif",
                      margin=dict(t=50, l=10, r=10, b=10))
    return fig


def jumlahkan(data, kolom):
    """Ringkas data per `kolom`: penjualan, untung, jumlah transaksi, dan margin."""
    hasil = (
        data.groupby(kolom, as_index=False)
        .agg(penjualan=("nilai_penjualan", "sum"),
             untung=("untung", "sum"),
             transaksi=("id_pesanan", "nunique"))
        .sort_values("penjualan", ascending=False)
    )
    hasil["penjualan_juta"] = hasil["penjualan"] / 1_000_000
    hasil["margin"] = hasil["untung"] / hasil["penjualan"] * 100
    return hasil


tab_ringkasan, tab_produk, tab_hubungan, tab_insight, tab_data = st.tabs(
    ["Ringkasan", "Produk dan Wilayah", "Hubungan Angka", "Insight", "Data"]
)

per_kategori = jumlahkan(data_tampil, "kategori")
per_bulan = jumlahkan(data_tampil, "bulan").sort_values("bulan")

grafik_porsi = px.pie(
    per_kategori, names="kategori", values="penjualan", hole=0.45,
    title="Porsi Penjualan per Kategori",
)
grafik_porsi.update_traces(texttemplate="%{label}<br>%{percent:.1%}")

grafik_margin = px.bar(
    per_kategori.sort_values("margin"), x="margin", y="kategori", orientation="h",
    text_auto=".1f", title="Margin Untung per Kategori (%)",
    labels={"margin": "Margin (%)", "kategori": "Kategori"},
)

grafik_tren = px.line(
    per_bulan, x="bulan", y="penjualan_juta", markers=True,
    title="Tren Penjualan per Bulan",
    labels={"bulan": "Bulan", "penjualan_juta": "Penjualan (Rp juta)"},
)
grafik_tren.update_xaxes(type="category")  # "2026-01" itu teks, bukan tanggal
grafik_tren.update_yaxes(rangemode="tozero")  # sumbu Y mulai dari 0

grafik_transaksi = px.bar(
    per_bulan, x="bulan", y="transaksi", text_auto=True,
    title="Jumlah Transaksi per Bulan",
    labels={"bulan": "Bulan", "transaksi": "Jumlah transaksi"},
)
grafik_transaksi.update_xaxes(type="category")

with tab_ringkasan:
    kiri, kanan = st.columns(2)
    kiri.plotly_chart(rapikan(grafik_porsi), use_container_width=True)
    kanan.plotly_chart(rapikan(grafik_margin), use_container_width=True)

    kiri, kanan = st.columns(2)
    kiri.plotly_chart(rapikan(grafik_tren), use_container_width=True)
    kanan.plotly_chart(rapikan(grafik_transaksi), use_container_width=True)


# ---------- Tab produk dan wilayah ----------
per_produk = jumlahkan(data_tampil, "nama_produk").head(5).sort_values("penjualan")
per_wilayah = jumlahkan(data_tampil, "wilayah")
pivot = pd.pivot_table(
    data_tampil, values="nilai_penjualan", index="wilayah",
    columns="kategori", aggfunc="sum", fill_value=0,
) / 1_000_000

grafik_produk = px.bar(
    per_produk, x="penjualan_juta", y="nama_produk", orientation="h", text_auto=".1f",
    title="5 Produk dengan Penjualan Terbesar",
    labels={"penjualan_juta": "Penjualan (Rp juta)", "nama_produk": "Produk"},
)

grafik_wilayah = px.bar(
    per_wilayah, x="wilayah", y="penjualan_juta", text_auto=".1f",
    title="Penjualan per Wilayah",
    labels={"wilayah": "Wilayah", "penjualan_juta": "Penjualan (Rp juta)"},
)

grafik_heatmap = px.imshow(
    pivot, text_auto=".1f", color_continuous_scale="Blues", aspect="auto",
    title="Penjualan Wilayah x Kategori (Rp juta)",
    labels={"x": "Kategori", "y": "Wilayah", "color": "Rp juta"},
)

with tab_produk:
    kiri, kanan = st.columns(2)
    kiri.plotly_chart(rapikan(grafik_produk), use_container_width=True)
    kanan.plotly_chart(rapikan(grafik_wilayah), use_container_width=True)
    st.plotly_chart(rapikan(grafik_heatmap), use_container_width=True)


# ---------- Tab hubungan antar angka ----------
kolom_angka = ["harga", "jumlah", "modal", "nilai_penjualan", "untung"]

with tab_hubungan:
    if len(data_tampil) < 3:
        st.info("Data terlalu sedikit untuk menghitung korelasi. Coba longgarkan filter.")
    else:
        korelasi = data_tampil[kolom_angka].corr()

        grafik_korelasi = px.imshow(
            korelasi, text_auto=".2f", color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1, aspect="auto", title="Korelasi Antar Angka",
        )

        grafik_scatter = px.scatter(
            data_tampil, x="modal", y="harga", color="kategori", hover_name="nama_produk",
            log_x=True, log_y=True, opacity=0.75,
            title="Harga Jual vs Modal (skala log)",
            labels={"modal": "Modal (Rp)", "harga": "Harga jual (Rp)", "kategori": "Kategori"},
        )
        batas = [data_tampil["modal"].min(), data_tampil["modal"].max()]
        grafik_scatter.add_scatter(  # garis impas: harga jual = modal
            x=batas, y=batas, mode="lines", name="Garis impas",
            line=dict(dash="dash", color="gray"),
        )

        kiri, kanan = st.columns(2)
        kiri.plotly_chart(rapikan(grafik_korelasi), use_container_width=True)
        kanan.plotly_chart(rapikan(grafik_scatter), use_container_width=True)
        st.caption(
            "Korelasi mendekati 1 artinya dua angka naik bersama, mendekati 0 artinya tidak berhubungan. "
            "Garis putus-putus adalah garis impas: titik di bawahnya berarti harga jual di bawah modal (rugi). "
            "Skala log dipakai supaya semua titik terlihat, termasuk Laptop Gaming yang harganya jauh lebih besar."
        )


# ---------- Tab insight ----------
def buat_insight(data):
    """Menyusun kalimat insight dari data yang sedang tampil. Hasilnya daftar (jenis, teks)."""
    kategori = jumlahkan(data, "kategori")
    wilayah = jumlahkan(data, "wilayah")
    bulan = jumlahkan(data, "bulan").sort_values("bulan")
    margin_total = data["untung"].sum() / data["nilai_penjualan"].sum() * 100
    hasil = []

    # 1. Kategori terbesar, dibandingkan dengan margin untungnya
    besar = kategori.iloc[0]
    persen = besar["penjualan"] / kategori["penjualan"].sum() * 100
    teks = (f"**{besar['kategori']}** menyumbang {persen:.1f}% dari total penjualan, "
            f"dengan margin untung {besar['margin']:.1f}% (rata-rata semua {margin_total:.1f}%).")
    if besar["margin"] < margin_total:
        teks += (" Penjualan terbesar belum tentu untung terbaik: margin kategori ini di bawah rata-rata. "
                 "**Rekomendasi:** cek apakah modalnya bisa ditekan.")
    hasil.append(("info", teks))

    # 2. Kategori dengan margin tertinggi
    if len(kategori) > 1:
        terbaik = kategori.sort_values("margin").iloc[-1]
        hasil.append(("success", f"Margin tertinggi ada di **{terbaik['kategori']}** ({terbaik['margin']:.1f}%). "
                                 "**Rekomendasi:** kategori ini layak didorong lewat promosi."))

    # 3. Wilayah terbesar
    if len(wilayah) > 1:
        top = wilayah.iloc[0]
        porsi = top["penjualan"] / wilayah["penjualan"].sum() * 100
        hasil.append(("info", f"**{top['wilayah']}** adalah wilayah terbesar dengan {porsi:.1f}% penjualan "
                              f"({top['transaksi']} transaksi). Cek apakah angka ini didorong satu transaksi besar."))

    # 4. Tren bulan terakhir dibanding bulan sebelumnya
    if len(bulan) > 1:
        akhir, sebelum = bulan.iloc[-1], bulan.iloc[-2]
        ubah = (akhir["penjualan"] / sebelum["penjualan"] - 1) * 100
        arah = "naik" if ubah >= 0 else "turun"
        teks = (f"Penjualan {akhir['bulan']} {arah} {abs(ubah):.1f}% dari {sebelum['bulan']}, "
                f"sementara jumlah transaksi {sebelum['transaksi']} menjadi {akhir['transaksi']}.")
        if ubah < -20 and akhir["transaksi"] >= sebelum["transaksi"] * 0.8:
            teks += " Transaksi relatif stabil tapi omzet turun: kemungkinan ada transaksi besar di bulan sebelumnya."
        hasil.append(("info", teks))

    # 5. Hubungan harga jual dan modal
    if len(data) >= 3 and data["harga"].nunique() > 1 and data["modal"].nunique() > 1:
        r = data["harga"].corr(data["modal"])
        if abs(r) >= 0.7:
            teks = (f"Harga jual dan modal berhubungan kuat (korelasi {r:.2f}): modal yang makin besar diikuti harga jual yang makin besar. "
                    "Ingat, korelasi bukan sebab-akibat, dan satu transaksi ekstrem bisa membuat angkanya tampak sempurna.")
        else:
            teks = f"Hubungan harga jual dan modal lemah (korelasi {r:.2f}). Cek apakah ada kategori yang harganya tidak mengikuti modal."
        hasil.append(("info", teks))

    # 6. Transaksi rugi (harga jual di bawah modal)
    rugi = data[data["untung"] < 0]
    if len(rugi) > 0:
        hasil.append(("warning", f"Ada **{len(rugi)} transaksi rugi** (harga jual di bawah modal) "
                                 f"dengan total kerugian {rupiah(-rugi['untung'].sum())}. "
                                 "**Rekomendasi:** periksa harga jual produk-produk itu."))
    else:
        hasil.append(("success", "Tidak ada transaksi rugi pada data yang tampil."))
    return hasil


kotak_pesan = {"info": st.info, "success": st.success, "warning": st.warning}

with tab_insight:
    st.subheader("Temuan dari data yang tampil")
    for jenis, teks in buat_insight(data_tampil):
        kotak_pesan[jenis](teks)


# ---------- Tab data ----------
with tab_data:
    st.dataframe(data_tampil, width="stretch")
    st.download_button(
        "Unduh data (CSV)",
        data_tampil.to_csv(index=False).encode("utf-8"),
        file_name="data-penjualan-tampil.csv",
        mime="text/csv",
    )
