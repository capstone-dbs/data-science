# Dashboard Analisis Status Gizi Balita 2023

Dashboard ini dibuat dari notebook `Analisis_Gizi_Balita_2023_Modern_Final_Markdown(1).ipynb`.
Dashboard menjawab 5 pertanyaan analisis:

1. Bagaimana distribusi status gizi balita berdasarkan indikator BB/U pada periode tahun 2021–2024?
2. Apakah terdapat perbedaan status gizi (BB/U, TB/U, dan BB/TB) yang signifikan antara balita laki-laki dan perempuan berdasarkan data gabungan tahun 2021–2024?
3. Pada kelompok usia berapa kondisi TB/U balita mencapai nilai rata-rata Z-Score terendah sepanjang periode tahun 2021–2024?
4. Bagaimana tren pertumbuhan rata-rata berat badan dan tinggi badan balita berdasarkan usia bulan selama tahun 2021–2024?
5. Berapa prevalensi wasting berdasarkan BB/TB pada balita selama tahun 2021–2024, serta kelompok usia dan gender mana yang memiliki prevalensi tertinggi?

## Cara menjalankan

1. Buka terminal di folder ini.
2. Install library:

```bash
pip install -r requirements.txt
```

3. Letakkan file data Excel di folder yang sama dengan `app.py`.
   Nama yang didukung otomatis:
   - `overlldata.xlsx`
   - `Overall Data.xlsx`
   - `overall data.xlsx`
   - `cleaned_data_gizi_balita_2023.csv`

   Atau upload file langsung dari sidebar dashboard.

4. Jalankan Streamlit:

```bash
streamlit run app.py
```

## Kolom yang dibutuhkan

File mentah minimal memiliki kolom:

- `Gender`
- `Age (Month)`
- `Weight`
- `Height`
- `Weight for Age`
- `Height for Age`
- `Weight for Height`
- `Z-Score  W/A`
- `Z-Score H/A`
- `Z-Score W/H`

Dashboard juga bisa membaca data yang sudah bersih dengan nama kolom:

- `Age_Month`
- `WFA_Status`
- `HFA_Status`
- `WFH_Status`
- `ZScore_WA`
- `ZScore_HA`
- `ZScore_WH`

## Fitur dashboard

- KPI total data, stunting, wasting, double burden, dan gizi kritis.
- Filter interaktif: gender, kelompok usia, status TB/U, BB/U, BB/TB, dan rentang usia.
- Visualisasi modern menggunakan Plotly.
- Jawaban otomatis untuk 5 pertanyaan analisis.
- Export data hasil filter ke CSV.
- Uji statistik gender terhadap BB/U dan wasting jika SciPy tersedia.
