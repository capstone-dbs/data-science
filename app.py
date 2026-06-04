from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

try:
    from scipy import stats
    SCIPY_OK = True
except Exception:
    SCIPY_OK = False

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="Dashboard Gizi Balita 2021–2024",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "overlldata.xlsx"

AGE_ORDER = [
    "0-12 bulan", "13-24 bulan", "25-36 bulan",
    "37-48 bulan", "49-60 bulan"
]

WFA_LABEL_MAP = {
    "Normal": "Normal",
    "Underfed": "Kurang Gizi",
    "Malnutrition": "Malnutrisi",
    "Overnutrition": "Gizi Lebih",
}
HFA_LABEL_MAP = {
    "Not Stunted": "Tidak Stunted",
    "Stunted": "Stunted",
}
WFH_LABEL_MAP = {
    "Normal": "Normal",
    "Thin": "Kurus",
    "Very Thin": "Sangat Kurus",
    "Obese": "Obesitas",
}

# ============================================================
# STYLE
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
[data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > section,
.main, .main > div, [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"] {
    background-color: #0d1117 !important;
}
[data-testid="stHeader"] { background-color: #0d1117 !important; }
[data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] span { color: #c9d1d9 !important; }
.block-container { padding: 1.5rem 2rem 2rem 2rem; max-width: 100%; background-color: #0d1117 !important; }
.hero-banner { background:#161b22; border:1px solid #30363d; border-left:4px solid #238636; border-radius:8px; padding:20px 28px; margin-bottom:20px; display:flex; align-items:center; gap:20px; }
.hero-badge { background:#238636; color:#fff; font-family:'IBM Plex Mono', monospace; font-size:11px; font-weight:600; letter-spacing:.05em; padding:4px 10px; border-radius:4px; white-space:nowrap; }
.hero-title { font-family:'IBM Plex Mono', monospace; font-size:20px; font-weight:600; color:#f0f6fc; margin:0 0 3px 0; }
.hero-sub { font-size:13px; color:#8b949e; margin:0; }
.metric-row { display:grid; grid-template-columns: repeat(5, 1fr); gap:10px; margin-bottom:20px; }
.metric-row-4 { display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-bottom:20px; }
.metric-box { background:#161b22; border:1px solid #30363d; border-radius:8px; padding:14px 16px; position:relative; overflow:hidden; }
.metric-box::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:8px 8px 0 0; }
.metric-box.c-green::before{background:#238636}.metric-box.c-blue::before{background:#1f6feb}.metric-box.c-yellow::before{background:#d29922}.metric-box.c-red::before{background:#da3633}.metric-box.c-purple::before{background:#8957e5}.metric-box.c-gray::before{background:#6e7681}
.metric-label { font-family:'IBM Plex Mono', monospace; font-size:10px; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:#8b949e; margin:0 0 6px 0; }
.metric-value { font-family:'IBM Plex Mono', monospace; font-size:26px; font-weight:600; color:#f0f6fc; margin:0 0 3px 0; line-height:1; }
.metric-pct { font-size:11px; color:#8b949e; margin:0; }
.section-header { display:flex; align-items:center; gap:10px; margin:0 0 12px 0; padding-bottom:8px; border-bottom:1px solid #21262d; }
.section-dot { width:7px; height:7px; border-radius:50%; background:#238636; flex-shrink:0; }
.section-title { font-family:'IBM Plex Mono', monospace; font-size:11px; font-weight:600; color:#8b949e; letter-spacing:.1em; margin:0; text-transform:uppercase; }
.chart-card { background:#161b22; border:1px solid #30363d; border-radius:8px; padding:16px; margin-bottom:14px; }
.answer-box { background:#161b22; border:1px solid #30363d; border-left:4px solid #238636; border-radius:8px; padding:14px 16px; margin-bottom:12px; color:#c9d1d9; font-size:13px; line-height:1.55; }
.answer-box b { color:#f0f6fc; }
.note-box { background:#0d1f36; border-left:3px solid #1f6feb; border-radius:0 6px 6px 0; padding:9px 12px; margin-top:10px; font-size:12px; color:#79c0ff; line-height:1.5; }
.stTabs [data-baseweb="tab-list"] { background:#161b22 !important; border-bottom:1px solid #30363d !important; gap:0 !important; padding:0 !important; }
.stTabs [data-baseweb="tab"] { font-family:'IBM Plex Mono', monospace !important; font-size:11px !important; font-weight:600 !important; letter-spacing:.06em !important; color:#6e7681 !important; background:transparent !important; border:none !important; border-bottom:2px solid transparent !important; border-radius:0 !important; padding:11px 22px !important; }
.stTabs [aria-selected="true"] { color:#f0f6fc !important; border-bottom:2px solid #238636 !important; background:transparent !important; }
.stTabs [data-baseweb="tab-panel"] { background-color:#0d1117 !important; padding-top:20px !important; }
.sidebar-hdr { font-family:'IBM Plex Mono', monospace; font-size:9px; font-weight:600; letter-spacing:.12em; text-transform:uppercase; color:#6e7681; padding:6px 0 4px 0; border-bottom:1px solid #30363d; margin-bottom:8px; }
.status-pill { display:inline-flex; align-items:center; gap:5px; font-family:'IBM Plex Mono', monospace; font-size:10px; color:#3fb950; padding:3px 8px; background:#0a1f10; border:1px solid #238636; border-radius:20px; margin-top:6px; }
.status-dot { width:5px; height:5px; border-radius:50%; background:#3fb950; }
div[data-testid="stMarkdownContainer"] p { color:#c9d1d9; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================
def fmt_int(x):
    return f"{int(x):,}".replace(",", ".")

def fmt_pct(x):
    return f"{float(x):.1f}%"

def fmt_p(x):
    try:
        x = float(x)
        if x < 0.001:
            return "< 0.001"
        return f"{x:.4f}"
    except Exception:
        return "-"

def clean_number(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace("nan", "", regex=False)
        .str.strip(),
        errors="coerce"
    )

def fix_weight_robust(value):
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        return value
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.day + (value.month / 10)
    value_str = str(value).strip()
    parsed_date = pd.to_datetime(value_str, errors="coerce")
    if pd.notna(parsed_date) and ("/" in value_str or "-" in value_str):
        return parsed_date.day + (parsed_date.month / 10)
    return pd.to_numeric(value_str.replace(",", "."), errors="coerce")

def make_age_group(x):
    if pd.isna(x):
        return np.nan
    x = float(x)
    if x <= 12:
        return "0-12 bulan"
    if x <= 24:
        return "13-24 bulan"
    if x <= 36:
        return "25-36 bulan"
    if x <= 48:
        return "37-48 bulan"
    return "49-60 bulan"

def section(title):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-dot"></div>
        <p class="section-title">{title}</p>
    </div>""", unsafe_allow_html=True)

def answer(text):
    st.markdown(f'<div class="answer-box">{text}</div>', unsafe_allow_html=True)

def note(text):
    st.markdown(f'<div class="note-box">{text}</div>', unsafe_allow_html=True)

LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono, monospace", size=11, color="#c9d1d9"),
    title=dict(font=dict(size=13, color="#f0f6fc", family="IBM Plex Mono, monospace")),
    margin=dict(l=20, r=20, t=44, b=22),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
    colorway=["#238636", "#1f6feb", "#da3633", "#d29922", "#8957e5", "#0d9585", "#58a6ff"],
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(size=10)),
)

def L(fig, h=370, title=""):
    fig.update_layout(height=h, title_text=title, **LAYOUT)
    return fig

# ============================================================
# LOAD & PREPROCESS
# ============================================================
with st.sidebar:
    st.markdown('<div class="sidebar-hdr">Sumber Data</div>', unsafe_allow_html=True)

if not DATA_PATH.exists():
    st.error(f"File tidak ditemukan: `{DATA_PATH.name}`")
    st.info("Taruh `overlldata.xlsx` satu folder dengan `app.py`.")
    st.stop()

raw = pd.read_excel(DATA_PATH)
df = raw.copy()
df.columns = [" ".join(str(c).strip().split()) for c in df.columns]

if "No." in df.columns:
    df = df.drop(columns=["No."])

rename_map = {
    "Age (Month)": "Age_Month",
    "Z-Score W/A": "ZScore_WA",
    "Z-Score H/A": "ZScore_HA",
    "Z-Score W/H": "ZScore_WH",
    "Weight for Age": "WFA_Status",
    "Height for Age": "HFA_Status",
    "Weight for Height": "WFH_Status",
}
df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

for col in list(df.columns):
    cc = col.lower().replace(" ", "").replace("-", "").replace("/", "").replace("_", "")
    if cc in ["agemonth", "agebulan"]:
        df = df.rename(columns={col: "Age_Month"})
    elif cc in ["zscorewa", "zscorew/a"]:
        df = df.rename(columns={col: "ZScore_WA"})
    elif cc in ["zscoreha", "zscoreh/a"]:
        df = df.rename(columns={col: "ZScore_HA"})
    elif cc in ["zscorewh", "zscorew/h"]:
        df = df.rename(columns={col: "ZScore_WH"})

required = ["Gender", "Age_Month", "Weight", "Height", "WFA_Status", "HFA_Status", "WFH_Status", "ZScore_WA", "ZScore_HA", "ZScore_WH"]
missing_cols = [c for c in required if c not in df.columns]
if missing_cols:
    st.error("Kolom wajib belum ditemukan: " + ", ".join(missing_cols))
    st.write("Kolom yang tersedia:", list(df.columns))
    st.stop()

df["Weight"] = df["Weight"].apply(fix_weight_robust)
for col in ["Age_Month", "Weight", "Height", "ZScore_WA", "ZScore_HA", "ZScore_WH"]:
    df[col] = clean_number(df[col])

df["Gender"] = df["Gender"].astype(str).str.strip().replace({
    "M": "Laki-laki", "F": "Perempuan",
    "L": "Laki-laki", "P": "Perempuan",
    "Male": "Laki-laki", "Female": "Perempuan",
    "male": "Laki-laki", "female": "Perempuan",
    "laki-laki": "Laki-laki", "perempuan": "Perempuan",
    "Laki laki": "Laki-laki", "Perempuan": "Perempuan",
})

for col in ["WFA_Status", "HFA_Status", "WFH_Status"]:
    df[col] = df[col].astype(str).str.strip()

# Cleaning dilakukan di belakang layar agar tampilan fokus ke 5 pertanyaan, bukan ke data mentah.
df = df.dropna(subset=required).copy()
invalid_condition = (
    (df["Weight"] > 40) |
    (df["Weight"] < 1.5) |
    (df["Height"] < 40) |
    (df["Height"] > 130) |
    (df["ZScore_WA"] < -10) | (df["ZScore_WA"] > 10) |
    (df["ZScore_HA"] < -10) | (df["ZScore_HA"] > 10) |
    (df["ZScore_WH"] < -10) | (df["ZScore_WH"] > 10)
)
df = df[~invalid_condition].copy().reset_index(drop=True)

df["Age_Group"] = df["Age_Month"].apply(make_age_group)
df["Age_Group"] = pd.Categorical(df["Age_Group"], categories=AGE_ORDER, ordered=True)
df["Gender_Label"] = df["Gender"]
df["Status_BBU_Label"] = df["WFA_Status"].map(WFA_LABEL_MAP).fillna(df["WFA_Status"])
df["Status_TBU_Label"] = df["HFA_Status"].map(HFA_LABEL_MAP).fillna(df["HFA_Status"])
df["Status_BBTB_Label"] = df["WFH_Status"].map(WFH_LABEL_MAP).fillna(df["WFH_Status"])
df["Is_Stunted"] = df["HFA_Status"].eq("Stunted")
df["Is_Wasting"] = df["WFH_Status"].isin(["Thin", "Very Thin"])
df["Is_Undernutrition"] = df["WFA_Status"].isin(["Underfed", "Malnutrition"])
df["Is_Severe_Stunted"] = df["ZScore_HA"] < -3
df["Double_Burden"] = df["Is_Stunted"] & df["Is_Wasting"]
df["Gizi_Kritis"] = df["WFA_Status"].eq("Malnutrition") & df["HFA_Status"].eq("Stunted")
df["BMI"] = df["Weight"] / ((df["Height"] / 100) ** 2)
df["Total_ZScore"] = df["ZScore_WA"] + df["ZScore_HA"] + df["ZScore_WH"]

with st.sidebar:
    st.markdown(f"""
    <div class="status-pill">
        <div class="status-dot"></div>
        {fmt_int(len(df))} baris final
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-hdr" style="margin-top:18px;">Filter</div>', unsafe_allow_html=True)

    if "Tahun" in df.columns:
        tahun_all = sorted(df["Tahun"].dropna().unique().tolist())
        sel_tahun = st.multiselect("Tahun", tahun_all, default=tahun_all)
    else:
        sel_tahun = None
        st.caption("Kolom Tahun tidak ditemukan.")

    gender_all = sorted(df["Gender_Label"].dropna().unique().tolist())
    sel_gender = st.multiselect("Gender", gender_all, default=gender_all)

    age_all = [x for x in AGE_ORDER if x in df["Age_Group"].dropna().astype(str).unique()]
    sel_age = st.multiselect("Kelompok Usia", age_all, default=age_all)

    bbu_all = sorted(df["Status_BBU_Label"].dropna().unique().tolist())
    sel_bbu = st.multiselect("Status BB/U", bbu_all, default=bbu_all)

    tbu_all = sorted(df["Status_TBU_Label"].dropna().unique().tolist())
    sel_tbu = st.multiselect("Status TB/U", tbu_all, default=tbu_all)

    bbtb_all = sorted(df["Status_BBTB_Label"].dropna().unique().tolist())
    sel_bbtb = st.multiselect("Status BB/TB", bbtb_all, default=bbtb_all)

mask = (
    df["Gender_Label"].isin(sel_gender) &
    df["Age_Group"].astype(str).isin(sel_age) &
    df["Status_BBU_Label"].isin(sel_bbu) &
    df["Status_TBU_Label"].isin(sel_tbu) &
    df["Status_BBTB_Label"].isin(sel_bbtb)
)
if sel_tahun is not None:
    mask = mask & df["Tahun"].isin(sel_tahun)

data = df[mask].copy()
if data.empty:
    st.warning("Data kosong setelah filter.")
    st.stop()

# ============================================================
# GLOBAL KPI
# ============================================================
total = len(data)
normal_bbu = int(data["WFA_Status"].eq("Normal").sum())
under = int(data["Is_Undernutrition"].sum())
stunted = int(data["Is_Stunted"].sum())
wasting = int(data["Is_Wasting"].sum())
double_burden = int(data["Double_Burden"].sum())
gizi_kritis = int(data["Gizi_Kritis"].sum())

normal_pct = normal_bbu / total * 100
under_pct = under / total * 100
stunted_pct = stunted / total * 100
wasting_pct = wasting / total * 100

period_text = "2021–2024"
if "Tahun" in data.columns and data["Tahun"].notna().any():
    period_text = f"{int(data['Tahun'].min())}–{int(data['Tahun'].max())}"

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-badge">GIZI · {period_text}</div>
    <div>
        <p class="hero-title">Dashboard Analisis Status Gizi Balita</p>
        <p class="hero-sub"> </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="metric-row">
    <div class="metric-box c-gray"><p class="metric-label">Total Balita</p><p class="metric-value">{fmt_int(total)}</p><p class="metric-pct">Data final terfilter</p></div>
    <div class="metric-box c-green"><p class="metric-label">Normal BB/U</p><p class="metric-value">{fmt_int(normal_bbu)}</p><p class="metric-pct">{fmt_pct(normal_pct)}</p></div>
    <div class="metric-box c-yellow"><p class="metric-label">Under/Malnutrisi</p><p class="metric-value">{fmt_int(under)}</p><p class="metric-pct">{fmt_pct(under_pct)}</p></div>
    <div class="metric-box c-red"><p class="metric-label">Stunted TB/U</p><p class="metric-value">{fmt_int(stunted)}</p><p class="metric-pct">{fmt_pct(stunted_pct)}</p></div>
    <div class="metric-box c-blue"><p class="metric-label">Wasting BB/TB</p><p class="metric-value">{fmt_int(wasting)}</p><p class="metric-pct">{fmt_pct(wasting_pct)}</p></div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# TABS — FOKUS 5 PERTANYAAN
# ============================================================
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "RINGKASAN",
    "BB/U",
    "GENDER",
    "Z-SCORE TB/U",
    "PERTUMBUHAN",
    "WASTING"
])

# ============================================================
# RINGKASAN
# ============================================================
with tab0:
    section("Ringkasan Lengkap 5 Pertanyaan")

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        temp = data["Status_BBU_Label"].value_counts().reset_index()
        temp.columns = ["Status", "Jumlah"]
        fig = px.pie(temp, names="Status", values="Jumlah", hole=0.55, title="P1 · Komposisi BB/U")
        fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="#0d1117", width=2)))
        st.plotly_chart(L(fig, h=320), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        temp = data["Status_TBU_Label"].value_counts().reset_index()
        temp.columns = ["Status", "Jumlah"]
        fig = px.pie(temp, names="Status", values="Jumlah", hole=0.55, title="Komposisi TB/U")
        fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="#0d1117", width=2)))
        st.plotly_chart(L(fig, h=320), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        temp = data["Status_BBTB_Label"].value_counts().reset_index()
        temp.columns = ["Status", "Jumlah"]
        fig = px.pie(temp, names="Status", values="Jumlah", hole=0.55, title="P5 · Komposisi BB/TB")
        fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="#0d1117", width=2)))
        st.plotly_chart(L(fig, h=320), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    c4, c5 = st.columns(2, gap="medium")
    with c4:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        key = pd.DataFrame({
            "Indikator": ["Normal BB/U", "Under/Malnutrisi", "Stunted", "Wasting", "Double Burden", "Gizi Kritis"],
            "Persen": [normal_pct, under_pct, stunted_pct, wasting_pct, double_burden/total*100, gizi_kritis/total*100]
        })
        fig = px.bar(key, x="Indikator", y="Persen", color="Indikator", text=key["Persen"].map(lambda v: f"{v:.1f}%"), title="Persentase Indikator Utama")
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(L(fig, h=360), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        age_prev = data.groupby("Age_Group", observed=True, as_index=False).agg(
            Stunting=("Is_Stunted", "mean"),
            Wasting=("Is_Wasting", "mean"),
            Undernutrisi=("Is_Undernutrition", "mean"),
        )
        age_long = age_prev.melt(id_vars="Age_Group", var_name="Indikator", value_name="Persen")
        age_long["Persen"] *= 100
        fig = px.bar(age_long, x="Age_Group", y="Persen", color="Indikator", barmode="group", title="Ringkasan Risiko per Kelompok Usia")
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(L(fig, h=360), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    top_bbu = data["Status_BBU_Label"].value_counts().idxmax()
    answer(f"<b>Ringkasan:</b> Dataset final berisi <b>{fmt_int(total)}</b> balita. Status BB/U paling dominan adalah <b>{top_bbu}</b>. Prevalensi stunting sebesar <b>{fmt_pct(stunted_pct)}</b>, wasting sebesar <b>{fmt_pct(wasting_pct)}</b>, dan under/malnutrisi sebesar <b>{fmt_pct(under_pct)}</b>.")

# ============================================================
# P1
# ============================================================
with tab1:
    section("Pertanyaan 1 · Bagaimana distribusi status gizi berdasarkan BB/U?")
    c1, c2 = st.columns([2, 3], gap="medium")
    bbu = data["Status_BBU_Label"].value_counts().reset_index()
    bbu.columns = ["Status BB/U", "Jumlah"]
    bbu["Persentase"] = bbu["Jumlah"] / total * 100

    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig = px.pie(bbu, names="Status BB/U", values="Jumlah", hole=0.55, title="Komposisi Status BB/U")
        fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="#0d1117", width=2)))
        st.plotly_chart(L(fig, h=390), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig = px.bar(bbu, x="Status BB/U", y="Jumlah", color="Status BB/U", text=bbu["Persentase"].map(lambda v: f"{v:.1f}%"), title="Jumlah dan Persentase BB/U")
        fig.update_traces(textposition="outside", marker_line_width=0)
        st.plotly_chart(L(fig, h=390), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    top_bbu = bbu.iloc[0]
    under_row = bbu[bbu["Status BB/U"].isin(["Kurang Gizi", "Malnutrisi"])]
    under_sum = int(under_row["Jumlah"].sum()) if not under_row.empty else 0
    answer(f"<b>Jawaban 1:</b> Status BB/U paling banyak adalah <b>{top_bbu['Status BB/U']}</b> sebanyak <b>{fmt_int(top_bbu['Jumlah'])}</b> balita ({top_bbu['Persentase']:.1f}%). Kelompok kurang gizi dan malnutrisi berjumlah <b>{fmt_int(under_sum)}</b> balita ({under_sum/total*100:.1f}%).")

# ============================================================
# P2
# ============================================================
with tab2:
    section("Pertanyaan 2 · Apakah status gizi berbeda berdasarkan gender?")
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        gender_bbu = pd.crosstab(data["Gender_Label"], data["Status_BBU_Label"], normalize="index") * 100
        gender_bbu = gender_bbu.reset_index().melt(id_vars="Gender_Label", var_name="Status", value_name="Persen")
        fig = px.bar(gender_bbu, x="Gender_Label", y="Persen", color="Status", barmode="group", text=gender_bbu["Persen"].map(lambda v: f"{v:.1f}%"), title="Proporsi BB/U per Gender")
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(L(fig, h=380), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        gender_risk = data.groupby("Gender_Label", as_index=False).agg(
            Stunting=("Is_Stunted", "mean"),
            Wasting=("Is_Wasting", "mean"),
            Undernutrisi=("Is_Undernutrition", "mean"),
        )
        gender_risk_long = gender_risk.melt(id_vars="Gender_Label", var_name="Indikator", value_name="Persen")
        gender_risk_long["Persen"] *= 100
        fig = px.bar(gender_risk_long, x="Gender_Label", y="Persen", color="Indikator", barmode="group", text=gender_risk_long["Persen"].map(lambda v: f"{v:.1f}%"), title="Prevalensi Risiko per Gender")
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(L(fig, h=380), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    if SCIPY_OK and data["Gender_Label"].nunique() >= 2:
        section("Uji Statistik Gender")
        c3, c4 = st.columns(2, gap="medium")
        chi_rows = []
        for col, label in [("Status_BBU_Label", "BB/U"), ("Status_TBU_Label", "TB/U"), ("Status_BBTB_Label", "BB/TB")]:
            table = pd.crosstab(data["Gender_Label"], data[col])
            if table.shape[0] > 1 and table.shape[1] > 1:
                chi2, p, dof, expected = stats.chi2_contingency(table)
                chi_rows.append({"Indikator": label, "Chi-Square": round(chi2, 4), "df": dof, "p-value": p, "Kesimpulan": "Signifikan" if p < 0.05 else "Tidak signifikan"})
        chi_df = pd.DataFrame(chi_rows)
        chi_show = chi_df.copy()
        if not chi_show.empty:
            chi_show["p-value"] = chi_show["p-value"].map(fmt_p)
        with c3:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.dataframe(chi_show, use_container_width=True, hide_index=True)
            note("Chi-Square menjawab apakah distribusi status gizi kategorikal berbeda menurut gender.")
            st.markdown('</div>', unsafe_allow_html=True)

        t_rows = []
        for col, label in [("ZScore_WA", "Z-Score BB/U"), ("ZScore_HA", "Z-Score TB/U"), ("ZScore_WH", "Z-Score BB/TB")]:
            male = data.loc[data["Gender_Label"].eq("Laki-laki"), col].dropna()
            female = data.loc[data["Gender_Label"].eq("Perempuan"), col].dropna()
            if len(male) > 1 and len(female) > 1:
                t_stat, p_val = stats.ttest_ind(male, female, equal_var=False)
                t_rows.append({"Indikator": label, "Rata-rata Laki-laki": round(male.mean(), 3), "Rata-rata Perempuan": round(female.mean(), 3), "t-statistic": round(t_stat, 4), "p-value": p_val, "Kesimpulan": "Signifikan" if p_val < 0.05 else "Tidak signifikan"})
        t_df = pd.DataFrame(t_rows)
        t_show = t_df.copy()
        if not t_show.empty:
            t_show["p-value"] = t_show["p-value"].map(fmt_p)
        with c4:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.dataframe(t_show, use_container_width=True, hide_index=True)
            note("T-Test membandingkan rata-rata Z-Score laki-laki dan perempuan.")
            st.markdown('</div>', unsafe_allow_html=True)

        sig = chi_df[chi_df["p-value"] < 0.05]["Indikator"].tolist() if not chi_df.empty else []
        sig_text = ", ".join(sig) if sig else "tidak ada indikator yang signifikan"
        answer(f"<b>Jawaban 2:</b> Berdasarkan uji Chi-Square, <b>{sig_text}</b> pada batas p-value &lt; 0,05. Grafik proporsi memperlihatkan perbandingan risiko gizi antara laki-laki dan perempuan.")
    else:
        answer("<b>Jawaban 2:</b> Grafik gender sudah tersedia, tetapi uji statistik belum dapat ditampilkan karena library scipy belum tersedia atau variasi gender tidak cukup.")

# ============================================================
# P3
# ============================================================
with tab3:
    section("Pertanyaan 3 · Pada usia berapa rata-rata Z-Score TB/U paling rendah?")
    c1, c2 = st.columns(2, gap="medium")
    hfa_age = data.groupby("Age_Group", observed=True, as_index=False)["ZScore_HA"].mean().sort_values("Age_Group")
    monthly_hfa = data.groupby("Age_Month", as_index=False)["ZScore_HA"].mean().sort_values("Age_Month")

    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig = px.bar(hfa_age, x="Age_Group", y="ZScore_HA", text=hfa_age["ZScore_HA"].map(lambda v: f"{v:.2f}"), title="Rata-rata Z-Score TB/U per Kelompok Usia")
        fig.add_hline(y=-2, line_dash="dash", line_color="#d29922", annotation_text="-2 SD")
        fig.update_traces(textposition="outside", marker_line_width=0)
        st.plotly_chart(L(fig, h=380), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig = px.line(monthly_hfa, x="Age_Month", y="ZScore_HA", markers=True, title="Rata-rata Z-Score TB/U per Usia Bulan")
        fig.add_hline(y=-2, line_dash="dash", line_color="#d29922", annotation_text="-2 SD")
        st.plotly_chart(L(fig, h=380), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        severe_age = data.groupby("Age_Group", observed=True, as_index=False).agg(Severe_Stunted=("Is_Severe_Stunted", "mean"))
        severe_age["Persen"] = severe_age["Severe_Stunted"] * 100
        fig = px.bar(severe_age, x="Age_Group", y="Persen", text=severe_age["Persen"].map(lambda v: f"{v:.1f}%"), title="Severe Stunted (< -3 SD) per Kelompok Usia")
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(L(fig, h=350), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig = px.box(data, x="Age_Group", y="ZScore_HA", color="Age_Group", title="Sebaran Z-Score TB/U per Kelompok Usia")
        fig.add_hline(y=-2, line_dash="dash", line_color="#d29922")
        st.plotly_chart(L(fig, h=350), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    min_group = hfa_age.loc[hfa_age["ZScore_HA"].idxmin()]
    min_month = monthly_hfa.loc[monthly_hfa["ZScore_HA"].idxmin()]
    answer(f"<b>Jawaban 3:</b> Kelompok usia dengan rata-rata Z-Score TB/U terendah adalah <b>{min_group['Age_Group']}</b> dengan nilai <b>{min_group['ZScore_HA']:.2f}</b>. Jika dilihat per bulan, titik terendah berada pada usia sekitar <b>{int(min_month['Age_Month'])} bulan</b> dengan nilai <b>{min_month['ZScore_HA']:.2f}</b>.")

# ============================================================
# P4
# ============================================================
with tab4:
    section("Pertanyaan 4 · Bagaimana tren berat badan dan tinggi badan berdasarkan usia?")
    c1, c2 = st.columns(2, gap="medium")
    monthly_growth = data.groupby("Age_Month", as_index=False).agg(Berat_Badan=("Weight", "mean"), Tinggi_Badan=("Height", "mean")).sort_values("Age_Month")
    age_growth = data.groupby("Age_Group", observed=True, as_index=False).agg(Berat_Badan=("Weight", "mean"), Tinggi_Badan=("Height", "mean"), BMI=("BMI", "mean")).sort_values("Age_Group")

    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        long = monthly_growth.melt(id_vars="Age_Month", var_name="Indikator", value_name="Rata-rata")
        fig = px.line(long, x="Age_Month", y="Rata-rata", color="Indikator", markers=False, title="Rata-rata BB dan TB per Usia Bulan")
        st.plotly_chart(L(fig, h=390), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        long = age_growth.melt(id_vars="Age_Group", var_name="Indikator", value_name="Rata-rata")
        fig = px.bar(long, x="Age_Group", y="Rata-rata", color="Indikator", barmode="group", text=long["Rata-rata"].map(lambda v: f"{v:.1f}"), title="Rata-rata BB, TB, dan BMI per Kelompok Usia")
        fig.update_traces(textposition="outside", marker_line_width=0)
        st.plotly_chart(L(fig, h=390), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig = px.scatter(data, x="Height", y="Weight", color="Status_TBU_Label", opacity=0.55, title="Scatter Berat Badan vs Tinggi Badan")
        fig.update_traces(marker=dict(size=5, line=dict(width=0)))
        st.plotly_chart(L(fig, h=360), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        num_cols = ["Age_Month", "Weight", "Height", "BMI", "ZScore_WA", "ZScore_HA", "ZScore_WH", "Total_ZScore"]
        corr = data[num_cols].corr(numeric_only=True)
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", aspect="auto", title="Heatmap Korelasi Numerik")
        fig.update_layout(height=360, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=44, b=22))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    corr_weight = data["Age_Month"].corr(data["Weight"])
    corr_height = data["Age_Month"].corr(data["Height"])
    answer(f"<b>Jawaban 4:</b> Berat badan dan tinggi badan cenderung meningkat seiring bertambahnya usia. Korelasi usia dengan berat badan adalah <b>{corr_weight:.2f}</b>, sedangkan korelasi usia dengan tinggi badan adalah <b>{corr_height:.2f}</b>.")

# ============================================================
# P5
# ============================================================
with tab5:
    section("Pertanyaan 5 · Bagaimana prevalensi wasting dan kelompok paling berisiko?")
    st.markdown(f"""
    <div class="metric-row-4">
        <div class="metric-box c-blue"><p class="metric-label">Wasting</p><p class="metric-value">{fmt_int(wasting)}</p><p class="metric-pct">{fmt_pct(wasting / total * 100)}</p></div>
        <div class="metric-box c-purple"><p class="metric-label">Double Burden</p><p class="metric-value">{fmt_int(double_burden)}</p><p class="metric-pct">{fmt_pct(double_burden / total * 100)}</p></div>
        <div class="metric-box c-red"><p class="metric-label">Gizi Kritis</p><p class="metric-value">{fmt_int(gizi_kritis)}</p><p class="metric-pct">{fmt_pct(gizi_kritis / total * 100)}</p></div>
        <div class="metric-box c-yellow"><p class="metric-label">Severe Stunted</p><p class="metric-value">{fmt_int(data['Is_Severe_Stunted'].sum())}</p><p class="metric-pct">{fmt_pct(data['Is_Severe_Stunted'].mean() * 100)}</p></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    wasting_age_gender = data.groupby(["Age_Group", "Gender_Label"], observed=True).agg(
        Jumlah_Data=("Is_Wasting", "count"),
        Jumlah_Wasting=("Is_Wasting", "sum"),
        Prevalensi=("Is_Wasting", "mean")
    ).reset_index()
    wasting_age_gender["Prevalensi (%)"] = wasting_age_gender["Prevalensi"] * 100

    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        fig = px.bar(wasting_age_gender, x="Age_Group", y="Prevalensi (%)", color="Gender_Label", barmode="group", text=wasting_age_gender["Prevalensi (%)"].map(lambda v: f"{v:.1f}%"), title="Prevalensi Wasting per Usia dan Gender")
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(L(fig, h=390), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        risk_age = data.groupby("Age_Group", observed=True, as_index=False).agg(
            Wasting=("Is_Wasting", "sum"),
            Double_Burden=("Double_Burden", "sum"),
            Gizi_Kritis=("Gizi_Kritis", "sum")
        )
        risk_long = risk_age.melt(id_vars="Age_Group", var_name="Indikator", value_name="Jumlah")
        fig = px.bar(risk_long, x="Age_Group", y="Jumlah", color="Indikator", barmode="group", text="Jumlah", title="Jumlah Kasus Risiko per Kelompok Usia")
        fig.update_traces(textposition="outside", marker_line_width=0)
        st.plotly_chart(L(fig, h=390), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        bbtb = data["Status_BBTB_Label"].value_counts().reset_index()
        bbtb.columns = ["Status BB/TB", "Jumlah"]
        fig = px.pie(bbtb, names="Status BB/TB", values="Jumlah", hole=0.55, title="Komposisi Status BB/TB")
        fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="#0d1117", width=2)))
        st.plotly_chart(L(fig, h=350), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if "Tahun" in data.columns:
            year_wasting = data.groupby("Tahun", as_index=False).agg(Wasting=("Is_Wasting", "mean"), Double_Burden=("Double_Burden", "mean"))
            year_long = year_wasting.melt(id_vars="Tahun", var_name="Indikator", value_name="Persen")
            year_long["Persen"] *= 100
            fig = px.line(year_long, x="Tahun", y="Persen", color="Indikator", markers=True, title="Tren Wasting dan Double Burden per Tahun")
            fig.update_yaxes(ticksuffix="%")
            st.plotly_chart(L(fig, h=350), use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Kolom Tahun tidak tersedia.")
        st.markdown('</div>', unsafe_allow_html=True)

    top_risk = wasting_age_gender.sort_values("Prevalensi (%)", ascending=False).iloc[0]
    answer(f"<b>Jawaban 5:</b> Prevalensi wasting total adalah <b>{fmt_pct(wasting / total * 100)}</b>. Kelompok dengan prevalensi wasting tertinggi adalah <b>{top_risk['Gender_Label']} usia {top_risk['Age_Group']}</b>, yaitu sekitar <b>{top_risk['Prevalensi (%)']:.1f}%</b>.")
