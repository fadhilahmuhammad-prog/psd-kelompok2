"""Dashboard "Beli Lagi atau Beralih?" - Kelompok 2 (K1), Pengantar Sains Data.

Tata letak ala Power BI World Championship: sidebar gelap, kartu KPI, kotak
Key Insight bergambar di sisi kiri, semua muat dalam satu layar tanpa scroll.
Tema: palet dan font Sociolla (Playfair Display + Lato, pink-rose).

Semua ukuran memakai satuan rem yang mengikuti tinggi dan lebar jendela
browser, jadi tampilan otomatis menyesuaikan layar laptop maupun monitor.

Jalankan:  streamlit run app.py
"""
import base64
import html
import os
from functools import partial

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Beli Lagi atau Beralih? | Dashboard Sociolla",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------- tema
PRIMARY = "#E23B5E"   # pink-merah khas Sociolla
DEEP = "#9E1F42"
DARK = "#2A1F22"
INK = "#241B1E"
MUTED = "#85787C"
LINE = "#EFE3E6"
BG = "#FBF7F6"
BLUSH = "#FDE9EE"
PINK2 = "#F4A6B7"
PLUM = "#6D4C9F"     # pasangan ungu untuk kelas "No" / seri kedua
PEACH = "#F08A5D"
TEAL = "#1F8A8A"
GOLD = "#B08A3E"
GREY = "#CFC3C7"
FONT = "Lato, sans-serif"

BELI_COLORS = {"Yes": PRIMARY, "Maybe": PINK2, "No": PLUM}
TIPE = ["Kombinasi", "Berminyak", "Sensitif", "Kering", "Normal"]
TIPE_COL = [PRIMARY, PEACH, PLUM, TEAL, GOLD]
KELUHAN = ["Kulit Kusam", "Jerawat", "Pori Besar", "Komedo",
           "Kantung Mata", "Flek", "Stretch Mark"]
LAMA = [("< 1 minggu", "&lt;1 mgg"), ("1 minggu - 1 bulan", "1-4 mgg"),
        ("1-3 bulan", "1-3 bln"), ("3-6 bulan", "3-6 bln"),
        ("6 bulan - 1 tahun", "6-12 bln"), ("> 1 tahun", "&gt;1 th")]
SHORT = {"Kepuasan Konsumen": "Kepuasan", "Durasi Penggunaan": "Durasi pakai",
         "Rekomendasi Produk": "Rekomendasi",
         "Niat Pembelian Ulang": "Niat beli ulang"}
PRETTY = {"rating": "Rating", "sub_rating_efektivitas": "Efektivitas",
          "sub_rating_kemasan": "Kemasan", "sub_rating_tekstur": "Tekstur",
          "sub_rating_kualitas_harga": "Kualitas harga",
          "harga_min": "Harga min", "harga_max": "Harga maks",
          "brand": "Brand", "skin_type_main": "Tipe kulit",
          "lama_penggunaan": "Lama pakai"}
_BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR, ASSET_DIR = os.path.join(_BASE, "data"), os.path.join(_BASE, "assets")
PAGES = ["Overview", "Di Balik Ulasan", "Modelling", "Jadi, Beli Lagi?"]
ICONS = [":material/dashboard:", ":material/bar_chart:", ":material/hub:",
         ":material/lightbulb:"]
FOTO = {PAGES[0]: ("foto_handuk.jpg", "center 85%"),
        PAGES[1]: ("foto_roller.jpg", "center 35%"),
        PAGES[2]: ("foto_air.jpg", "center 40%"),
        PAGES[3]: ("foto_produk.jpg", "center 55%")}

# Tinggi area konten = 100vh - CHROME. Baris kartu dihitung dari sisa tinggi.
CHROME = "8.6rem"
GAPR = "0.75rem"
ROW_VAR = {  # --row = tinggi satu baris kartu
    PAGES[0]: f"calc((100vh - {CHROME} - 6.4rem - 2 * {GAPR}) / 2)",
    PAGES[1]: f"calc((100vh - {CHROME} - {GAPR}) / 2)",
    PAGES[2]: f"calc((100vh - {CHROME} - {GAPR}) / 2)",
    PAGES[3]: f"calc((100vh - {CHROME} - 9rem - 2 * {GAPR}) / 2)",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&display=swap');
:root { --row: __ROW__; }
html { font-size: clamp(5px, min(1.9vh, 0.95vw), 22px) !important; }
html, body, .stApp, .stApp button, .stApp input { font-family:'Lato',sans-serif; }
.stApp { background:__BG__; color:__INK__; }
header[data-testid="stHeader"], footer, #MainMenu,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display:none !important; }
[data-testid="stMain"], section.main { overflow:hidden !important; }
.block-container { padding:0.9rem 1.4rem 0 1.4rem !important; max-width:100% !important; }
.block-container [data-testid="stVerticalBlock"] { gap:__GAP__; }
[data-testid="stHorizontalBlock"] { gap:__GAP__ !important; }
[data-testid="stMarkdownContainer"] p { margin:0; }
/* Streamlit memberi margin-bawah -1rem untuk mengimbangi margin paragraf; margin itu sudah kita hapus */
[data-testid="stMarkdownContainer"] { margin-bottom:0 !important; }
[data-testid="stColumn"], [data-testid="column"] { min-width:0; }

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] { width:13.5rem !important; min-width:13.5rem !important;
  max-width:13.5rem !important;
  background:linear-gradient(185deg,#33252A 0%,#1B1315 100%); border-right:0; }
section[data-testid="stSidebar"] > div { background:transparent; width:13.5rem !important; }
[data-testid="stSidebarResizeHandle"], [data-testid="stSidebarHeader"] { display:none !important; }
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding:0 1rem; overflow:hidden; }
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding:0 !important; }
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap:.35rem; }
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] label p {
  color:#E3D2D7 !important; font-size:.82rem !important; letter-spacing:.03em; }
.logo-wrap { padding:1.3rem 0 .2rem 0; }
.logo-wrap img { width:9.2rem; display:block; }
.logo-wrap .wm { font-family:'Playfair Display',serif; font-size:2rem; color:#fff; }
.logo-sub { color:__PINK2__; font-size:.68rem; letter-spacing:.18em; text-transform:uppercase;
  margin:.5rem 0 1.2rem 0; font-weight:700; }
section[data-testid="stSidebar"] .stButton button {
  width:100%; justify-content:flex-start; text-align:left; border:0; border-radius:.7rem;
  padding:.4rem .8rem; min-height:0; background:transparent; color:#F1E6E9; font-weight:400;
  box-shadow:none; }
section[data-testid="stSidebar"] .stButton button p { font-size:.98rem !important; color:inherit !important; letter-spacing:0; }
section[data-testid="stSidebar"] .stButton button:hover { background:rgba(255,255,255,.08); color:#fff; }
section[data-testid="stSidebar"] .stButton button[kind="primary"],
section[data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] {
  background:__PRIMARY__; color:#fff; font-weight:700; }
.side-h { color:__PINK2__; font-size:.68rem; letter-spacing:.18em; text-transform:uppercase;
  font-weight:700; margin:1.2rem 0 .1rem 0; }
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background:#3C2D32; border:1px solid #58444B; border-radius:.6rem; min-height:0; font-size:.84rem; }
section[data-testid="stSidebar"] [data-baseweb="select"] input,
section[data-testid="stSidebar"] [data-baseweb="select"] div { color:#fff; }
.side-l { color:#E3D2D7; font-size:.82rem; margin:.4rem 0 .1rem 0; }
section[data-testid="stSidebar"] [data-testid="stPills"] { gap:.35rem; }
section[data-testid="stSidebar"] [data-testid="stPills"] button { min-height:0; padding:.2rem .7rem; border-radius:999px;
  background:#3C2D32; border:1px solid #58444B; color:#F1E6E9; }
section[data-testid="stSidebar"] [data-testid="stPills"] button p { font-size:.82rem !important; color:inherit !important; }
section[data-testid="stSidebar"] [data-testid="stPills"] button[kind="pillsActive"],
section[data-testid="stSidebar"] [data-testid="stPills"] button[aria-checked="true"],
section[data-testid="stSidebar"] [data-testid="stPills"] button[data-testid="stBaseButton-pillsActive"] { background:__PRIMARY__; border-color:__PRIMARY__; color:#fff; }
.st-key-reset button { justify-content:center !important; border:1px solid #58444B !important; margin-top:.3rem; }
.st-key-reset button:disabled { opacity:.35; }
.how { margin-top:.9rem; padding:.7rem .8rem; border-radius:.8rem; background:rgba(255,255,255,.08);
  color:#F1E6E9; font-size:.78rem; line-height:1.4; }
.how b { color:__PINK2__; }
.src { color:#B9A8AE; font-size:.7rem; margin-top:.7rem; line-height:1.4; }

/* ---------- header ---------- */
.hdr { height:5.2rem; overflow:hidden; }
.ttl { font-family:'Playfair Display',serif; font-weight:700; font-size:3.2rem; line-height:1.08; color:__INK__; letter-spacing:-.01em; }
.ttl i { font-style:italic; font-weight:500; color:__PRIMARY__; padding-right:.06em;
  background:linear-gradient(100deg,__DEEP__ 0%,__PRIMARY__ 45%,#F47A97 100%); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.sub { color:__MUTED__; font-size:1.05rem; margin-top:.3rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.chips { display:flex; justify-content:flex-end; align-items:center; gap:.6rem; height:5rem; }
.chip { display:flex; flex-direction:column; justify-content:center; min-width:5.6rem; height:4.3rem; box-sizing:border-box;
  padding:.4rem 1rem; background:#fff; border:1px solid __LINE__; border-radius:1rem; line-height:1.15;
  font-size:.86rem; color:__MUTED__; box-shadow:0 1px 3px rgba(60,20,30,.05); }
.chip b { font-family:'Playfair Display',serif; font-size:1.7rem; font-weight:600; color:__PRIMARY__; line-height:1.1; }

/* ---------- kartu ---------- */
[class*="st-key-card"] {
  background:#fff !important; border:1px solid __LINE__ !important; border-radius:1.1rem !important;
  box-shadow:0 1px 3px rgba(60,20,30,.05); padding:.95rem 1.1rem .8rem 1.1rem !important;
  overflow:hidden !important; box-sizing:border-box; }
[class*="st-key-card"] { transition:box-shadow .2s ease, border-color .2s ease; }
[class*="st-key-card"]:hover { box-shadow:0 10px 26px rgba(226,59,94,.14); border-color:__PINK2__ !important; }
.kpi { transition:box-shadow .2s ease, border-color .2s ease; }
.kpi:hover, .stat:hover { box-shadow:0 10px 26px rgba(226,59,94,.14); border-color:__PINK2__; }
.stat { transition:box-shadow .2s ease, border-color .2s ease; }
[class*="st-key-card"][data-testid="stVerticalBlock"],
[class*="st-key-card"] [data-testid="stVerticalBlock"] { gap:.25rem; }
[class*="st-key-cardr"], [class*="st-key-cardm"], [class*="st-key-cardq"], [class*="st-key-carde"], [class*="st-key-cardt"],
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cardr"]),
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cardm"]),
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cardq"]),
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-carde"]),
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-cardt"]) {
  height:var(--row) !important; flex:0 0 var(--row) !important; }
[class*="st-key-card"] > [data-testid="stElementContainer"] { flex-shrink:0 !important; }
/* grafik mengisi sisa ruang kartu, tidak pernah melebihi kartu */
[data-testid="stMain"] [class*="st-key-card"] > [data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]) {
  flex:1 1 0 !important; min-height:0 !important; height:auto !important; overflow:hidden !important; }
[data-testid="stMain"] [class*="st-key-card"] [data-testid="stPlotlyChart"] { height:100% !important; }
.chead { height:3.1rem; overflow:hidden; }
.cbar { width:1.7rem; height:.2rem; border-radius:.2rem; background:__PRIMARY__; margin-bottom:.4rem; }
.ct { font-family:'Playfair Display',serif; font-size:1.12rem; font-weight:700; color:__INK__; line-height:1.2;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.cs { font-size:.84rem; color:__MUTED__; margin-top:.05rem; white-space:nowrap; overflow:hidden;
  text-overflow:ellipsis; }
.res { height:3rem; overflow:hidden; font-size:.84rem; line-height:1.35; color:__INK__; }
.res b { color:__PRIMARY__; }

/* kpi */
.kpi { position:relative; height:6.4rem; background:#fff; border:1px solid __LINE__; border-radius:1.1rem;
  padding:.8rem 1.1rem; box-sizing:border-box; box-shadow:0 1px 3px rgba(60,20,30,.05); overflow:hidden; }
.kl { font-size:.84rem; font-weight:700; color:__MUTED__;
  white-space:nowrap; }
.kico { position:absolute; right:.9rem; top:.8rem; width:2.1rem; height:2.1rem; border-radius:50%; background:__BLUSH__;
  display:grid; place-items:center; }
.kico svg { width:1.15rem; height:1.15rem; }
.kv { font-family:'Playfair Display',serif; font-size:2rem; line-height:1.15; color:__INK__; margin-top:.1rem; }
.kv small { font-family:'Lato',sans-serif; font-size:.95rem; color:__MUTED__; margin-left:.2rem; }
.ks { font-size:.8rem; color:__PRIMARY__; font-weight:700; white-space:nowrap; }

/* kotak insight bergambar */
.ins { position:relative; overflow:hidden; box-sizing:border-box; height:calc(100vh - __CHROME__);
  border-radius:1.4rem; padding:1.2rem 1.2rem 1.1rem 1.2rem; color:#fff; display:flex; flex-direction:column;
  background:linear-gradient(165deg,__DEEP__ 0%,#B82650 55%,__PRIMARY__ 100%); }
.ins > .ins-bg { position:absolute; inset:0; z-index:0; background-size:cover; opacity:.27; }
.ins > .ins-shade { position:absolute; inset:0; z-index:0;
  background:linear-gradient(180deg,rgba(110,15,45,.5) 0%,rgba(110,15,45,.12) 40%,rgba(70,8,30,.7) 100%); }
.ins > *:not(.ins-bg):not(.ins-shade) { position:relative; z-index:1; }
.tag { display:inline-block; align-self:flex-start; font-size:.8rem; font-weight:700; letter-spacing:.04em;
  padding:.3rem .7rem; border-radius:999px; background:rgba(255,255,255,.22); }
.ins-t { font-family:'Playfair Display',serif; font-weight:700; font-size:1.5rem; line-height:1.15; margin-top:.8rem; }
.ins-big { font-family:'Playfair Display',serif; font-size:2.6rem; line-height:1.05; margin-top:.6rem; color:#FFE3EA; }
.ins-sub { font-size:.84rem; color:#FFE0E7; margin-top:.15rem; }
.ins-how { display:flex; flex-direction:column; gap:.65rem; margin-top:.9rem; }
.ins-row .lb { font-size:max(11.5px,.9rem); font-weight:900;
  color:#FFC2D0; padding-bottom:.15rem; border-bottom:1px solid rgba(255,255,255,.28); }
.ins-row .tx { font-size:max(11.5px,.88rem); line-height:1.4; margin-top:.3rem; color:#FFF6F8; }
.ins-row .tx b { color:#fff; }
.ins-pill { margin-top:auto; font-size:max(11.5px,.88rem); line-height:1.35; font-weight:700; padding:.65rem .8rem;
  border-radius:.9rem; background:rgba(40,0,18,.42); }

/* teks dalam kartu */
.bl { margin:.1rem 0 0 0; padding-left:1.05rem; font-size:max(11.5px,.9rem); line-height:1.38; color:__INK__; }
.bl li { margin-bottom:.35rem; } .bl b { color:__PRIMARY__; }
.goal { display:flex; gap:.6rem; align-items:center; margin-top:.3rem; font-size:max(11.5px,.92rem); line-height:1.3; }
.goal .n { flex:0 0 1.4rem; height:1.4rem; border-radius:50%; background:__BLUSH__; color:__PRIMARY__;
  font-weight:900; font-size:.82rem; display:flex; align-items:center; justify-content:center; }
.lead { font-size:max(11.5px,.92rem); line-height:1.4; margin-top:.1rem; }
.lead b { color:__PRIMARY__; }
.strip { display:flex; gap:.4rem; margin-top:.45rem; }
.strip div { flex:1; background:__BLUSH__; border-radius:.7rem; padding:.3rem .3rem; text-align:center;
  font-size:.68rem; letter-spacing:.04em; color:__MUTED__; text-transform:uppercase; }
.strip b { display:block; font-family:'Playfair Display',serif; font-size:1.15rem; letter-spacing:0;
  color:__PRIMARY__; text-transform:none; }
.flow { display:flex; flex-direction:column; gap:.35rem; margin-top:.1rem; position:relative; }
.step { display:flex; gap:.7rem; align-items:center; position:relative; }
.step:not(:last-child)::after { content:""; position:absolute; left:.78rem; top:1.9rem; height:.95rem; width:2px; background:__PINK2__; }
.step .n { flex:0 0 1.6rem; height:1.6rem; border-radius:50%; background:__PRIMARY__; color:#fff;
  font-weight:900; font-size:.82rem; display:flex; align-items:center; justify-content:center; }
.step .t { font-size:.82rem; line-height:1.25; } .step .t b { display:block; font-size:max(11.5px,.92rem); }
.step .t span { color:__MUTED__; }
.stat { height:9rem; background:#fff; border:1px solid __LINE__; border-radius:1.1rem; padding:.8rem 1.1rem;
  box-sizing:border-box; box-shadow:0 1px 3px rgba(60,20,30,.05); overflow:hidden; }
.stat .sb { overflow:hidden; display:flex; align-items:center; justify-content:space-between; gap:.7rem; margin-top:.2rem; }
.stat .st1 { flex:1; min-width:0; }
.stat .sv { font-family:'Playfair Display',serif; font-size:1.9rem; line-height:1.1; color:__PRIMARY__; }
.stat .sd { font-size:.8rem; line-height:1.25; margin-top:.15rem; color:__INK__; }
.sviz { flex:0 0 5.4rem; display:flex; justify-content:center; }
.mbs { display:flex; gap:.7rem; align-items:flex-end; height:5.2rem; }
.mb { display:flex; flex-direction:column; justify-content:flex-end; align-items:center; height:100%; width:2.3rem; }
.mb b { font-size:max(10.5px,.74rem); color:__INK__; margin-bottom:.15rem; }
.mbv { width:100%; border-radius:.45rem .45rem .2rem .2rem; min-height:.25rem; }
.mb span { font-size:.7rem; color:__MUTED__; margin-top:.2rem; }
.ring { width:4.8rem; height:4.8rem; border-radius:50%; display:grid; place-items:center;
  background:conic-gradient(__PRIMARY__ calc(var(--p) * 1%), __BLUSH__ 0); }
.ring span { width:3.5rem; height:3.5rem; border-radius:50%; background:#fff; display:grid; place-items:center;
  font-family:'Playfair Display',serif; font-size:1.1rem; color:__INK__; }

/* toggle */
[data-testid="stSegmentedControl"] { margin:.1rem 0 .25rem 0; }
[data-testid="stSegmentedControl"] button { padding:.12rem .6rem; min-height:0; background:#fff !important;
  border:1px solid __LINE__ !important; color:__INK__ !important; }
[data-testid="stSegmentedControl"] button p { color:inherit !important; }
[data-testid="stSegmentedControl"] button[kind="segmented_controlActive"],
[data-testid="stSegmentedControl"] button[aria-checked="true"],
[data-testid="stSegmentedControl"] button[data-testid="stBaseButton-segmented_controlActive"] {
  background:__BLUSH__ !important; border-color:__PRIMARY__ !important; color:__PRIMARY__ !important; }
[data-testid="stSegmentedControl"] button p { font-size:.82rem !important; }
</style>
"""
for k, v in {"__BG__": BG, "__INK__": INK, "__GAP__": GAPR, "__CHROME__": CHROME,
             "__PINK2__": PINK2, "__PRIMARY__": PRIMARY, "__MUTED__": MUTED,
             "__LINE__": LINE, "__DEEP__": DEEP, "__BLUSH__": BLUSH}.items():
    CSS = CSS.replace(k, v)


# ---------------------------------------------------------------- helpers
def fmt(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def idn(n):
    return f"{int(n):,}".replace(",", ".")


def esc(s):
    return html.escape(str(s))


@st.cache_data(show_spinner=False)
def _read(path, mtime):
    return pd.read_csv(path)


def load_csv(name):
    p = os.path.join(DATA_DIR, name)
    return _read(p, os.path.getmtime(p)).copy() if os.path.exists(p) else None


@st.cache_data(show_spinner=False)
def img_b64(name):
    p = os.path.join(ASSET_DIR, name)
    if not os.path.exists(p):
        return None
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()


def pct_yes(s):
    return float((s == "Yes").mean() * 100) if len(s) else float("nan")


def safe(x, d=0):
    return "-" if x != x else fmt(x, d)


_n = [0]
_c = [0]


def mix(c1, c2, t):
    """Campur dua warna hex; t=0 memberi c1, t=1 memberi c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    t = max(0.0, min(1.0, t))
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def ramp(values, lo=PINK2, hi=PRIMARY):
    """Warna per nilai: makin besar makin pekat."""
    vmin, vmax = min(values), max(values)
    span = (vmax - vmin) or 1
    return [mix(lo, hi, 0.2 + 0.8 * (v - vmin) / span) for v in values]


def sel_points(ev):
    """Titik yang diklik pengguna pada grafik (kosong jika belum ada)."""
    try:
        return list(ev["selection"]["points"])
    except Exception:
        try:
            return list(ev.selection.points)
        except Exception:
            return []


def plot(fig, legend=None, margin=None, key=None, select=None):
    # select: None, "rerun", atau fungsi yang dipanggil saat titik diklik.
    # Tinggi grafik diatur CSS (mengisi sisa ruang kartu).
    fig.update_layout(
        height=260, margin=margin or dict(l=2, r=10, t=4, b=2),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=12, color=INK), bargap=0.3,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left",
                    x=0, font=dict(size=12, color=INK)),
        legend_title_text="",
        hoverlabel=dict(bgcolor="white", bordercolor=PINK2,
                        font=dict(family=FONT, color=INK, size=13)))
    fig.update_xaxes(zeroline=False, tickfont=dict(size=12, color=INK),
                     linecolor=LINE, automargin=True)
    fig.update_yaxes(zeroline=False, tickfont=dict(size=12, color=INK),
                     automargin=True)
    try:  # sudut batang membulat (Plotly 5.24 ke atas); versi lama melewatinya
        fig.update_traces(marker_cornerradius=6, selector=dict(type="bar"))
    except Exception:
        pass
    if legend:
        fig.update_layout(legend=legend)
    _n[0] += 1
    kw = {"config": {"displayModeBar": False}, "key": key or f"pc{_n[0]}", "theme": None}
    modes = [dict(on_select=select, selection_mode="points"), {}] if select \
        else [{}]
    for sm in modes:
        for extra in ({"width": "stretch"}, {"use_container_width": True}, {}):
            try:
                return st.plotly_chart(fig, **kw, **sm, **extra)
            except TypeError:
                continue
    return None


def card(kind):
    """kind: r = kartu grafik, t = grafik + toggle, e = grafik + satu baris
    keterangan, m = kartu model (toggle + keterangan), q = halaman 4."""
    _c[0] += 1
    for kw in ({"border": True, "key": f"card{kind}{_c[0]}"}, {"border": True}):
        try:
            return st.container(**kw)
        except TypeError:
            continue


def card_head(title, sub=""):
    st.markdown(f'<div class="chead"><div class="cbar"></div>'
                f'<div class="ct">{title}</div><div class="cs">{sub}</div>'
                f'</div>', unsafe_allow_html=True)


def result(txt):
    st.markdown(f'<div class="res">{txt}</div>', unsafe_allow_html=True)


def toggle(options, key):
    try:
        v = st.segmented_control("Tampilan", options, default=options[0],
                                 key=key, label_visibility="collapsed")
    except Exception:
        v = st.radio("Tampilan", options, horizontal=True, key=key,
                     label_visibility="collapsed")
    return v or options[0]


ICON = {  # ikon sederhana untuk kartu KPI (viewBox 24x24)
    "chat": "M4 4h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9l-5 4v-4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z",
    "box": "M12 2l9 4.5v9L12 20l-9-4.5v-9L12 2zm0 2.4L6.2 7.3 12 10.2l5.8-2.9L12 4.4zM5 9.2v5.1l6 3V12.2L5 9.2zm14 0l-6 3v5.1l6-3V9.2z",
    "heart": "M12 21s-8-5.3-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.7-8 11-8 11z",
    "star": "M12 2l3 6.3 6.9.9-5 4.8 1.3 6.9L12 17.6l-6.2 3.3 1.3-6.9-5-4.8 6.9-.9L12 2z",
    "thumb": "M2 10h4v11H2V10zm6 11V10l4-8c1.6 0 2.6 1.1 2.3 2.6L13.6 9H20a2 2 0 0 1 2 2.3l-1.4 8a2 2 0 0 1-2 1.7H8z",
}


def kpi(col, label, value, unit, sub, icon="heart"):
    col.markdown(
        f'<div class="kpi"><div class="kico"><svg viewBox="0 0 24 24" '
        f'fill="{PRIMARY}"><path d="{ICON[icon]}"/></svg></div>'
        f'<div class="kl">{label}</div>'
        f'<div class="kv">{value}<small>{unit}</small></div>'
        f'<div class="ks">{sub}</div></div>', unsafe_allow_html=True)


def insight(page, title, big, bigsub, rows, pill):
    """Kotak Key Insight: angka utama, lalu tiga paragraf pendek."""
    foto, pos = FOTO[page]
    b64 = img_b64(foto)
    bg = (f'<div class="ins-bg" style="background-image:url(data:image/jpeg;'
          f'base64,{b64});background-position:{pos}"></div>' if b64 else "")
    items = "".join(f'<div class="ins-row"><div class="lb">{c}</div>'
                    f'<div class="tx">{t}</div></div>' for c, t in rows)
    st.markdown(
        f'<div class="ins">{bg}<div class="ins-shade"></div>'
        f'<div class="tag">Key insight</div>'
        f'<div class="ins-t">{title}</div><div class="ins-big">{big}</div>'
        f'<div class="ins-sub">{bigsub}</div>'
        f'<div class="ins-how">{items}</div>'
        f'<div class="ins-pill">{pill}</div></div>', unsafe_allow_html=True)


def stat_card(col, label, big, desc, visual):
    col.markdown(
        f'<div class="stat"><div class="kl">{label}</div><div class="sb">'
        f'<div class="st1"><div class="sv">{big}</div>'
        f'<div class="sd">{desc}</div></div>'
        f'<div class="sviz">{visual}</div></div></div>',
        unsafe_allow_html=True)


def minibars(items):
    """items: [(label, nilai 0-1, warna, teks)] jadi batang kecil bergambar."""
    cols = "".join(
        f'<div class="mb"><b>{t}</b><div class="mbv" style="height:'
        f'{max(v, 0.04) * 100:.0f}%;background:{c}"></div>'
        f'<span>{lab}</span></div>' for lab, v, c, t in items)
    return f'<div class="mbs">{cols}</div>'


def ring(pct, text):
    return (f'<div class="ring" style="--p:{pct:.0f}"><span>{text}</span>'
            '</div>')


def hbar(labels, values, color=None, text=None, colors=None, key=None,
         select=None):
    """Bar horizontal dengan warna bergradasi; data urut naik."""
    text = text or [f"{v:.0f}%" for v in values]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker_color=colors or ramp(values), text=text,
        textposition="outside", cliponaxis=False,
        textfont=dict(size=12, color=INK),
        hovertemplate="%{y}: %{text}<extra></extra>"))
    fig.update_xaxes(visible=False, range=[0, max(values) * 1.3])
    fig.update_yaxes(dtick=1)
    return plot(fig, key=key, select=select)


def lolli(labels, values, colors=None, text=None, vmax=None, size=15):
    """Lollipop horizontal: batang tipis dengan titik di ujungnya."""
    text = text or [f"{v:.0f}%" for v in values]
    colors = colors or ramp(values)
    fig = go.Figure()
    fig.add_bar(x=values, y=labels, orientation="h", width=0.12,
                marker_color=colors, hoverinfo="skip", showlegend=False)
    fig.add_scatter(
        x=values, y=labels, mode="markers+text", text=text,
        textposition="middle right", textfont=dict(size=12, color=INK),
        cliponaxis=False, showlegend=False,
        marker=dict(size=size, color=colors, line=dict(color="#fff", width=2.5)),
        hovertemplate="%{y}: %{text}<extra></extra>")
    fig.update_xaxes(visible=False, range=[0, (vmax or max(values)) * 1.3])
    fig.update_yaxes(dtick=1)
    plot(fig)


def donut(labels, values, colors, center=None, pull=None):
    tot = float(sum(values)) or 1.0
    labels = [f"{l}  {v / tot * 100:.0f}%" for l, v in zip(labels, values)]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.68, sort=False,
        pull=pull or 0,
        title=dict(text=center or "", position="middle center",
                   font=dict(size=13, color=INK)),
        domain=dict(x=[0, 0.56], y=[0, 1]),
        marker=dict(colors=colors, line=dict(color="#fff", width=3)),
        textinfo="none",
        hovertemplate="%{label}<br>%{value:,} ulasan<extra></extra>"))
    plot(fig, legend=dict(orientation="v", x=0.62, xanchor="left", y=0.5,
                          yanchor="middle", font=dict(size=12)))


def gauge(value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        number=dict(suffix="%", font=dict(size=38, family="Playfair Display, serif",
                                          color=INK)),
        gauge=dict(axis=dict(range=[0, 100], tickvals=[0, 50, 100], tickwidth=0,
                             tickfont=dict(size=11, color=MUTED)),
                   bar=dict(color=PRIMARY, thickness=0.32), bgcolor=BLUSH,
                   borderwidth=0)))
    plot(fig, margin=dict(l=24, r=24, t=18, b=0))


def treemap(labels, values):
    fig = go.Figure(go.Treemap(
        labels=labels, parents=[""] * len(labels), values=values,
        marker=dict(colors=values, line=dict(width=3, color="#fff"),
                    colorscale=[[0, BLUSH], [0.5, PINK2], [1, "#EE6F8B"]]),
        texttemplate="<b>%{label}</b><br>%{value:.0f}%",
        textfont=dict(size=13, color=INK), pathbar=dict(visible=False),
        hovertemplate="%{label}: %{value:.1f}% ulasan<extra></extra>"))
    plot(fig, margin=dict(l=0, r=0, t=0, b=0))


def efek_hubungan(d):
    """Kekuatan hubungan tiap peubah dengan beli_lagi (0 sampai 1).
    Peubah angka: eta. Peubah kategori: Cramer's V. Harga min dan harga maks
    digabung jadi satu baris (diambil yang lebih besar)."""
    y = d["beli_lagi"]
    rows, harga = [], []
    for col, nama in [("rating", "Rating"),
                      ("sub_rating_efektivitas", "Efektivitas"),
                      ("sub_rating_kemasan", "Kemasan"),
                      ("sub_rating_tekstur", "Tekstur"),
                      ("sub_rating_kualitas_harga", "Kualitas harga"),
                      ("harga_min", "Harga"),
                      ("harga_max", "Harga")]:
        x = d[col].astype(float)
        gm = x.mean()
        ssb = sum(len(v) * (v.mean() - gm) ** 2 for _, v in x.groupby(y))
        sst = ((x - gm) ** 2).sum()
        e = float(np.sqrt(ssb / sst)) if sst else 0.0
        (harga if nama == "Harga" else rows).append((nama, e))
    rows.append(("Harga", max(e for _, e in harga)))
    for col, nama in [("rekomendasi", "Rekomendasi"),
                      ("lama_penggunaan", "Lama pakai")]:
        ct = pd.crosstab(d[col], y).values.astype(float)
        n = ct.sum()
        exp = ct.sum(1, keepdims=True) * ct.sum(0, keepdims=True) / n
        chi2 = ((ct - exp) ** 2 / exp).sum()
        den = n * max(min(ct.shape) - 1, 1)
        rows.append((nama, float(np.sqrt(chi2 / den))))
    return pd.DataFrame(rows, columns=["Peubah", "Kekuatan"]).sort_values(
        "Kekuatan")


def chart_efek(d, size=15):
    ef = efek_hubungan(d)
    warna = [GREY if p == "Harga" else PRIMARY for p in ef["Peubah"]]
    lolli(ef["Peubah"].tolist(), ef["Kekuatan"].round(2).tolist(),
          text=[fmt(v, 2) for v in ef["Kekuatan"]], colors=warna, size=size)
    return ef


def load_klas():
    return (load_csv("klasifikasi_metrics.csv"),
            load_csv("confusion_matrix.csv"),
            load_csv("feature_importance.csv"))


def klas_summary(km, cmx):
    rows = []
    for nama in km["Analisis"].unique():
        c_ = cmx[cmx["Analisis"] == nama]
        tot = c_["Jumlah"].sum()
        akt = c_.groupby("Aktual")["Jumlah"].sum()
        acc = c_.loc[c_["Prediksi"] == c_["Aktual"], "Jumlah"].sum() / tot
        kap = km.loc[km["Analisis"] == nama, "Kappa"].iloc[0]
        rows.append(dict(analisis=nama, acc=acc * 100,
                         nir=akt.max() / tot * 100, kappa=kap))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- data
df_all = load_csv("data_bersih.csv")
if df_all is None:
    st.error("File `data/data_bersih.csv` belum ada.")
    st.stop()

if "page" not in st.session_state:
    st.session_state["page"] = PAGES[0]
page = st.session_state["page"]
st.markdown(CSS.replace("__ROW__", ROW_VAR[page]), unsafe_allow_html=True)


def set_page(name):
    st.session_state["page"] = name


def reset_filters():
    st.session_state["f_tipe"] = []
    st.session_state["f_brand"] = []
    st.session_state["reset_n"] = st.session_state.get("reset_n", 0) + 1


def pick_brand(chart_key):
    """Klik batang brand di grafik = jadikan filter brand."""
    pts = sel_points(st.session_state.get(chart_key))
    if pts:
        lab = pts[0].get("y")
        if lab:
            st.session_state["f_brand"] = [lab]


def nav_button(label, key, active, icon):
    kw = dict(key=key, type="primary" if active else "secondary",
              on_click=set_page, args=(label,))
    for extra in ({"width": "stretch", "icon": icon},
                  {"use_container_width": True, "icon": icon},
                  {"use_container_width": True}, {}):
        try:
            return st.button(label, **kw, **extra)
        except Exception:
            continue


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    lg = img_b64("logo_sociolla_putih.png")
    logo_html = (f'<img src="data:image/png;base64,{lg}" alt="sociolla">'
                 if lg else '<div class="wm">sociolla</div>')
    st.markdown(f'<div class="logo-wrap">{logo_html}</div>'
                '<div class="logo-sub">Analisis ulasan skincare</div>',
                unsafe_allow_html=True)
    for i, p in enumerate(PAGES):
        nav_button(p, f"nav{i}", page == p, ICONS[i])

    st.markdown('<div class="side-h">Filter data</div>',
                unsafe_allow_html=True)
    st.session_state.setdefault("f_tipe", [])
    st.session_state.setdefault("f_brand", [])
    st.markdown('<div class="side-l">Tipe kulit</div>', unsafe_allow_html=True)
    try:
        pilih_tipe = st.pills("Tipe kulit", TIPE, selection_mode="multi",
                              key="f_tipe", label_visibility="collapsed")
    except Exception:
        pilih_tipe = st.multiselect("Tipe kulit", TIPE, placeholder="Semua",
                                    key="f_tipe")
    pilih_tipe = list(pilih_tipe or [])
    pilih_brand = st.multiselect("Brand", sorted(df_all["brand"].unique()),
                                 placeholder="Semua", key="f_brand")
    st.button("Hapus filter", key="reset", on_click=reset_filters,
              disabled=not (pilih_tipe or pilih_brand))
    st.markdown(
        '<div class="how"><b>Cara membaca</b><br>Kotak Key Insight di kiri '
        'merangkum arti grafiknya. Filter berlaku di Overview dan Di '
        'Balik Ulasan.</div>'
        '<div class="src">Sumber: sociolla.com (web scraping)<br>'
        'Kelompok 2 (K1) · Pengantar Sains Data</div>',
        unsafe_allow_html=True)

df = df_all
if pilih_tipe:
    df = df[df[[f"tipe_{t}" for t in pilih_tipe]].sum(axis=1) > 0]
if pilih_brand:
    df = df[df["brand"].isin(pilih_brand)]
filtered = bool(pilih_tipe or pilih_brand)
# data untuk grafik brand: hanya difilter tipe kulit, supaya brand lain tetap bisa diklik
df_t = (df_all[df_all[[f"tipe_{t}" for t in pilih_tipe]].sum(axis=1) > 0]
        if pilih_tipe else df_all)
reset_n = st.session_state.get("reset_n", 0)


def header(title, sub):
    a, b = st.columns([3, 2.4])
    a.markdown(f'<div class="hdr"><div class="ttl">{title}</div>'
               f'<div class="sub">{sub}</div></div>', unsafe_allow_html=True)
    src = df if (filtered and page in PAGES[:2]) else df_all
    nama = "ulasan terpilih" if src is df and filtered and page in PAGES[:2] \
        else "ulasan"
    chips = (f'<div class="chip"><b>{idn(len(src))}</b>{nama}</div>'
             f'<div class="chip"><b>{src["nama_produk"].nunique()}</b>produk</div>'
             f'<div class="chip"><b>{src["brand"].nunique()}</b>brand</div>')
    b.markdown(f'<div class="chips">{chips}</div>', unsafe_allow_html=True)


# ================================================================ HALAMAN 1
def page_overview():
    header("Beli Lagi <i>atau</i> Beralih?",
           "Apa yang membuat orang membeli skincare yang sama lagi, "
           "dilihat dari ulasan Sociolla")
    if len(df) == 0:
        st.warning("Tidak ada ulasan yang cocok dengan filter.")
        return
    n, p_yes = len(df), pct_yes(df["beli_lagi"])
    p_no = (df["beli_lagi"] == "No").mean() * 100
    p_mb = (df["beli_lagi"] == "Maybe").mean() * 100
    p_rec = pct_yes(df["rekomendasi"])
    cl, cr = st.columns([1.25, 3], gap="small")
    with cl:
        tsum = {t: int(df[f"tipe_{t}"].sum()) for t in TIPE}
        tipe_top = max(tsum, key=tsum.get)
        kel_r = sorted(KELUHAN, key=lambda k_: -df["keluhan_" + k_.replace(
            " ", "_")].mean())[:2]
        insight(PAGES[0], "Siapa yang menulis ulasan, dan puaskah mereka?",
                f"{fmt(p_yes, 0)}%", "ingin membeli lagi",
                [("Yang kelihatan",
                  f"Reviewer terbanyak berkulit {tipe_top.lower()}, dengan "
                  f"keluhan {kel_r[0].lower()} dan {kel_r[1].lower()}. "
                  f"Rating rata-ratanya {fmt(df['rating'].mean(), 2)} dari 5."),
                 ("Kenapa begitu",
                  "Orang yang menulis ulasan biasanya sudah cocok dengan "
                  "produknya, jadi nilai tinggi muncul di hampir semua "
                  "produk. Rating saja sulit memisahkan pembeli setia dari "
                  "yang tidak."),
                 ("Lalu apa",
                  f"Yang menarik adalah {fmt(p_mb + p_no, 0)}% sisanya, yang "
                  "ragu atau tidak mau beli lagi. Halaman berikutnya "
                  "mencari tahu apa yang membedakan mereka.")],
                "Kebanyakan pembeli puas, jadi pembedanya harus dicari di "
                "kelompok kecil yang ragu.")
    with cr:
        k = st.columns(5, gap="small")
        kpi(k[0], "Ulasan", idn(n), "", "dari 11.401 data mentah", "chat")
        kpi(k[1], "Produk", idn(df["nama_produk"].nunique()), "",
            f"{df['brand'].nunique()} brand", "box")
        kpi(k[2], "Ingin beli lagi", fmt(p_yes, 0), "%",
            f"Maybe {fmt(p_mb, 0)}% · No {fmt(p_no, 0)}%", "heart")
        kpi(k[3], "Rating rata-rata", fmt(df["rating"].mean(), 2), "/5",
            f"median {fmt(df['rating'].median(), 1)}", "star")
        kpi(k[4], "Rekomendasi", fmt(p_rec, 0), "%",
            f"tidak: {fmt(100 - p_rec, 0)}%", "thumb")

        r1 = st.columns([1.3, 1, 1.15], gap="small")
        with r1[0]:
            with card("r"):
                card_head("Latar belakang dan tujuan",
                          "Kenapa analisis ini dibuat")
                st.markdown(
                    '<div class="lead">Cocok di kulit mereka belum tentu '
                    'cocok di kulit kita. Kami mencari apa yang membuat '
                    'orang <b>membeli lagi</b>.</div>'
                    '<div class="goal"><div class="n">1</div><div>Mengenal '
                    'reviewer dan produknya</div></div>'
                    '<div class="goal"><div class="n">2</div><div>Mencari '
                    'faktor yang mendorong beli ulang</div></div>'
                    '<div class="goal"><div class="n">3</div><div>Membangun '
                    'model dan menyusun saran</div></div>'
                    '<div class="strip"><div><b>11.401</b>ulasan mentah</div>'
                    f'<div><b>{idn(len(df_all))}</b>ulasan bersih</div>'
                    f'<div><b>{df_all["nama_produk"].nunique()}</b>produk'
                    '</div></div>', unsafe_allow_html=True)
        with r1[1]:
            with card("r"):
                card_head("Tipe kulit reviewer",
                          "Satu reviewer bisa punya lebih dari satu")
                donut(TIPE, [tsum[t] for t in TIPE], TIPE_COL,
                      center=f"<b>{idn(n)}</b><br>ulasan",
                      pull=[0.07 if t in pilih_tipe else 0 for t in TIPE])
        with r1[2]:
            with card("t"):
                card_head("Keluhan kulit", "Dari 7 keluhan yang dicatat")
                v = toggle(["Disebut", "Ingin beli lagi"], "t_kel")
                rows = []
                for k_ in KELUHAN:
                    col = "keluhan_" + k_.replace(" ", "_")
                    if v == "Disebut":
                        val = df[col].mean() * 100
                    else:
                        val = pct_yes(df.loc[df[col] == 1, "beli_lagi"])
                    rows.append((k_, 0.0 if val != val else val))
                rows.sort(key=lambda t: t[1])
                lolli([a for a, _ in rows], [b for _, b in rows],
                      vmax=100 if v != "Disebut" else None)

        r2 = st.columns([1.3, 1, 1.15], gap="small")
        with r2[0]:
            with card("t"):
                card_head("Brand paling banyak diulas",
                          "Klik batang untuk memfilter brand")
                v = toggle(["Jumlah ulasan", "Ingin beli lagi"], "t_brand")
                if v == "Jumlah ulasan":
                    br = df_t["brand"].value_counts().head(8).iloc[::-1]
                    labs, vals = br.index.tolist(), br.values.tolist()
                    txt = [idn(x) for x in vals]
                else:
                    g = df_t.groupby("brand")["beli_lagi"].agg(
                        [pct_yes, "size"])
                    g = g[g["size"] >= 30].sort_values("pct_yes").tail(8)
                    labs, vals = g.index.tolist(), g["pct_yes"].round(0).tolist()
                    txt = [f"{x:.0f}%" for x in vals]
                pal = ramp(vals)
                if pilih_brand:
                    pal = [c if b_ in pilih_brand else "#F2D3DA"
                           for b_, c in zip(labs, pal)]
                ck = f"brand_{reset_n}_{v[:3]}"
                hbar(labs, vals, text=txt, colors=pal, key=ck,
                     select=partial(pick_brand, ck))
        with r2[1]:
            with card("e"):
                card_head("Niat beli ulang", "Ulasan yang menjawab Yes")
                gauge(round(p_yes, 1))
                result(f"Dari {idn(n)} ulasan, Maybe {fmt(p_mb, 0)}% dan "
                       f"No {fmt(p_no, 0)}%.")
        with r2[2]:
            with card("e"):
                card_head("Sentimen ulasan", "Dari kata positif dan negatif")
                sm = (df["label_sentimen"].value_counts(normalize=True) * 100
                      ).reindex(["Positif", "Netral", "Negatif"]).fillna(0)
                fig = go.Figure()
                for lab, col, tc in [("Positif", PRIMARY, "#fff"),
                                     ("Netral", PINK2, INK),
                                     ("Negatif", PLUM, "#fff")]:
                    val = float(sm[lab])
                    fig.add_bar(
                        x=[val], y=[""], orientation="h", name=lab,
                        marker_color=col,
                        text=[f"{val:.0f}%" if val >= 8 else ""],
                        textposition="inside", insidetextanchor="middle",
                        textfont=dict(color=tc, size=14),
                        hovertemplate=f"{lab}: {val:.1f}%<extra></extra>")
                fig.update_layout(barmode="stack", bargap=0.2)
                fig.update_xaxes(visible=False, range=[0, 100])
                fig.update_yaxes(visible=False)
                plot(fig)
                result("Skornya dihitung dari kata positif dan negatif di "
                       "teks ulasan, jadi ini pembanding untuk rating.")


# ================================================================ HALAMAN 2
VAR_CMP = {"Rating": "rating", "Efektivitas": "sub_rating_efektivitas",
           "Tekstur": "sub_rating_tekstur", "Kemasan": "sub_rating_kemasan",
           "Kualitas harga": "sub_rating_kualitas_harga"}


def page_eda():
    header("Di Balik <i>Ulasan</i>",
           "Dari data mentah sampai pola awal, lengkap dengan faktor yang "
           "paling erat dengan beli ulang")
    if len(df) == 0:
        st.warning("Tidak ada ulasan yang cocok dengan filter.")
        return
    sel = load_csv("seleksi_peubah.csv")
    tk = load_csv("top_kata.csv")
    rec_y = pct_yes(df.loc[df["rekomendasi"] == "Yes", "beli_lagi"])
    rec_n = pct_yes(df.loc[df["rekomendasi"] == "No", "beli_lagi"])
    ef = efek_hubungan(df)
    eta_h = ef.loc[ef["Peubah"] == "Harga", "Kekuatan"].iloc[0]
    nsig = int(sel["signifikan"].sum()) if sel is not None else 7
    ntot = len(sel) if sel is not None else 9
    lama_y = pct_yes(df.loc[df["lama_penggunaan"] == "> 1 tahun", "beli_lagi"])
    top2 = ef.sort_values("Kekuatan", ascending=False).head(2)

    cl, cr = st.columns([1.25, 3], gap="small")
    with cl:
        insight(PAGES[1], "Apa yang bikin orang beli lagi?",
                f"{safe(rec_y)}% vs {safe(rec_n)}%",
                "ingin beli lagi: yang merekomendasikan vs yang tidak",
                [("Yang kelihatan",
                  "Penulis yang merekomendasikan produk hampir selalu ingin "
                  "beli lagi, sedangkan yang tidak merekomendasikan hampir "
                  f"tidak. Pemakai di atas setahun mencapai {safe(lama_y)}%."),
                 ("Apa itu eta (η)?",
                  "Angka 0 sampai 1 yang menunjukkan seberapa kuat sebuah "
                  "faktor membedakan orang yang mau dan tidak mau beli "
                  "lagi. Dekat 0 berarti tidak ada kaitan. Harga hanya "
                  f"{fmt(eta_h, 2)}: harga produk yang dibeli ulang dan "
                  "yang tidak hampir sama."),
                 ("Kenapa begitu",
                  f"Rekomendasi dan rating (sekitar "
                  f"{fmt(top2['Kekuatan'].min(), 1)}) paling erat karena "
                  "sama-sama mencerminkan rasa puas. Uji ANOVA juga "
                  "menunjukkan harga tidak berbeda nyata (p &gt; 0,05).")],
                "Orang beli lagi kalau puas dan mau merekomendasikan. "
                "Harga tidak menentukan.")
    with cr:
        r1 = st.columns([1.15, 1.25, 1], gap="small")
        with r1[0]:
            with card("r"):
                card_head("Alur preprocessing", "Dari scraping sampai siap "
                          "dianalisis")
                steps = [
                    ("Scraping Sociolla", "11.401 ulasan skincare"),
                    ("Pembersihan data", f"jadi {idn(len(df_all))} ulasan "
                     f"dari {df_all['nama_produk'].nunique()} produk"),
                    ("Pecah kolom", "tipe kulit dan keluhan jadi 0/1"),
                    ("Rapikan teks", "hitung skor sentimen"),
                    ("Seleksi peubah", f"{nsig} dari {ntot} lolos uji "
                     "ANOVA/Chi-square"),
                ]
                items = "".join(
                    f'<div class="step"><div class="n">{i}</div><div class="t">'
                    f'<b>{a}</b><span>{b}</span></div></div>'
                    for i, (a, b) in enumerate(steps, 1))
                st.markdown(f'<div class="flow">{items}</div>',
                            unsafe_allow_html=True)
        with r1[1]:
            with card("r"):
                card_head("Seberapa erat dengan beli ulang?",
                          "η: 0 = tidak ada kaitan, 1 = sangat kuat")
                chart_efek(df, size=13)
        with r1[2]:
            with card("r"):
                card_head("Rekomendasi dan beli ulang",
                          "% niat beli lagi per kelompok")
                ct = (pd.crosstab(df["rekomendasi"], df["beli_lagi"],
                                  normalize="index") * 100)
                fig = go.Figure()
                for cls in ["Yes", "Maybe", "No"]:
                    if cls in ct.columns:
                        fig.add_bar(
                            name=cls, x=["Merekomendasikan" if i == "Yes"
                                         else "Tidak" for i in ct.index],
                            y=ct[cls].tolist(), marker_color=BELI_COLORS[cls],
                            text=[f"{cls} {v:.0f}%" if v >= 8 else ""
                                  for v in ct[cls]], textposition="inside",
                            insidetextanchor="middle",
                            textfont=dict(color="#fff" if cls != "Maybe"
                                          else INK, size=13),
                            hovertemplate="%{x}: %{y:.1f}%<extra>" + cls
                            + "</extra>")
                fig.update_layout(barmode="stack", bargap=0.3, showlegend=False)
                fig.update_yaxes(visible=False)
                plot(fig)
        r2 = st.columns([1.15, 1.25, 1], gap="small")
        with r2[0]:
            with card("t"):
                card_head("Lama pemakaian", "Makin lama, makin yakin?")
                v = toggle(["% ingin beli lagi", "Jumlah ulasan"], "t_lama")
                if v.startswith("%"):
                    g = df.groupby("lama_penggunaan")["beli_lagi"].apply(
                        pct_yes)
                else:
                    g = df["lama_penggunaan"].value_counts()
                lab = [s for k_, s in LAMA if k_ in g.index]
                val = [float(g[k_]) for k_, s in LAMA if k_ in g.index]
                if v.startswith("%"):
                    fig = go.Figure(go.Scatter(
                        x=lab, y=val, mode="lines+markers+text",
                        text=[f"{x:.0f}%" for x in val],
                        textposition="top center", cliponaxis=False,
                        textfont=dict(size=12, color=INK),
                        fill="tozeroy", fillcolor="rgba(226,59,94,0.13)",
                        line=dict(color=PRIMARY, width=3, shape="spline"),
                        marker=dict(size=10, color=PRIMARY,
                                    line=dict(color="#fff", width=2)),
                        hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
                    fig.update_yaxes(visible=False, range=[70, 102])
                    fig.update_xaxes(tickangle=0, tickfont=dict(size=11))
                else:
                    fig = go.Figure(go.Bar(
                        x=lab, y=val, marker_color=ramp(val),
                        text=[idn(x) for x in val], textposition="outside",
                        cliponaxis=False, textfont=dict(size=12, color=INK),
                        hovertemplate="%{x}: %{y:,} ulasan<extra></extra>"))
                    fig.update_yaxes(visible=False, range=[0, max(val) * 1.2])
                    fig.update_xaxes(tickangle=0, tickfont=dict(size=11))
                plot(fig)
        with r2[1]:
            with card("t"):
                card_head("Bandingkan skor tiap kelompok",
                          "Rata-rata skor menurut niat beli ulang")
                v = toggle(list(VAR_CMP), "t_cmp")
                mu = df.groupby("beli_lagi")[VAR_CMP[v]].mean()
                orde = [x for x in ["No", "Maybe", "Yes"] if x in mu.index]
                vals = [float(mu[o]) for o in orde]
                cols = [BELI_COLORS[o] for o in orde]
                fig = go.Figure()
                fig.add_bar(x=orde, y=vals, width=0.1, marker_color=cols,
                            hoverinfo="skip", showlegend=False)
                fig.add_scatter(
                    x=orde, y=vals, mode="markers+text",
                    text=[fmt(a, 2) for a in vals],
                    textposition="middle center",
                    textfont=dict(size=12, color=["#fff" if o != "Maybe"
                                                  else INK for o in orde]),
                    marker=dict(size=36, color=cols,
                                line=dict(color="#fff", width=3)),
                    showlegend=False,
                    hovertemplate="%{x}: %{y:.2f}<extra></extra>")
                fig.update_yaxes(visible=False,
                                 range=[min(vals) - 0.6, 5.25])
                plot(fig)
        with r2[2]:
            with card("r"):
                card_head("Kata yang sering muncul",
                          "% ulasan yang memuatnya")
                if tk is not None:
                    t = tk.head(10)
                    treemap(t["kata"].tolist(), t["persen_review"].tolist())


# ================================================================ HALAMAN 3
def page_model():
    header("Apa Kata <i>Modelnya</i>?",
           "Klasifikasi, FAMD, association rules, dan clustering menjawab "
           "pertanyaan yang sama")
    km, cmx, fim = load_klas()
    ev, kp = load_csv("famd_eigen.csv"), load_csv("famd_peubah.csv")
    rules, cl_ = load_csv("rules.csv"), load_csv("cluster.csv")
    sil = load_csv("cluster_silhouette.csv")
    ks = klas_summary(km, cmx)
    r4 = ks[ks["analisis"] == "Niat Pembelian Ulang"].iloc[0]
    sil2 = float(sil.loc[sil["k"] == 2, "silhouette"].iloc[0])

    cl, cr = st.columns([1.25, 3], gap="small")
    with cl:
        rc0 = km[km["Analisis"] == "Niat Pembelian Ulang"].set_index(
            "Kelas")["Recall"]
        gc = cl_.groupby("cluster")["beli_lagi_rate"].mean() * 100
        rc0 = km[km["Analisis"] == "Niat Pembelian Ulang"].set_index(
            "Kelas")["Recall"]
        gc = cl_.groupby("cluster")["beli_lagi_rate"].mean() * 100
        insight(PAGES[2], "Apa kata keempat model?",
                f"{fmt(r4['acc'], 0)}% vs {fmt(r4['nir'], 0)}%",
                "akurasi model dibanding tebakan 'semua Yes'",
                [("Yang kelihatan",
                  "Klasifikasi cuma unggul tipis dari tebakan mayoritas "
                  f"(Kappa {fmt(r4['kappa'], 2)}). Kelas No dikenali "
                  f"{rc0['No'] * 100:.0f}% dan Maybe "
                  f"{rc0['Maybe'] * 100:.0f}%."),
                 ("Kenapa begitu",
                  "Datanya timpang, sekitar 85% Yes, jadi model sulit belajar "
                  "dari kelas yang kecil. Clustering membagi produk jadi dua "
                  f"kelompok ({fmt(gc.max(), 0)}% vs {fmt(gc.min(), 0)}% "
                  f"beli ulang), tapi silhouette hanya {fmt(sil2, 2)} "
                  "sehingga batasnya kabur."),
                 ("Lalu apa",
                  "Semua model menunjuk ke kepuasan sebagai pembeda. Pakai "
                  "hasilnya sebagai petunjuk arah, belum sebagai alat "
                  "prediksi.")],
                "Pola kepuasan konsisten di keempat model, tetapi data yang "
                "timpang membatasi akurasinya.")
    with cr:
        m1 = st.columns(2, gap="small")
        # ---------------- klasifikasi
        with m1[0]:
            with card("m"):
                card_head("Supervised · Klasifikasi",
                          "Random Forest menebak niat beli ulang")
                v = toggle(["Akurasi", "Peubah penting", "Matriks"], "t_klas")
                if v == "Akurasi":
                    nm = ks["analisis"].map(SHORT).tolist()
                    fig = go.Figure()
                    fig.add_bar(name="Akurasi model", x=nm,
                                y=ks["acc"].round(1).tolist(),
                                marker_color=PRIMARY,
                                text=[f"{a:.0f}%" for a in ks["acc"]],
                                textposition="outside", cliponaxis=False)
                    fig.add_bar(name="Tebakan mayoritas", x=nm,
                                y=ks["nir"].round(1).tolist(),
                                marker_color=GREY,
                                text=[f"{a:.0f}%" for a in ks["nir"]],
                                textposition="outside", cliponaxis=False)
                    fig.update_layout(barmode="group")
                    fig.update_yaxes(visible=False, range=[0, 125])
                    plot(fig)
                    result(f"Akurasi <b>{fmt(r4['acc'])}%</b>, tebakan mayoritas "
                           f"<b>{fmt(r4['nir'])}%</b>. Selisihnya tipis.")
                elif v == "Peubah penting":
                    f4 = fim[fim["Analisis"] == "Niat Pembelian Ulang"].copy()
                    f4["Nama"] = f4["Variabel"].map(PRETTY).fillna(
                        f4["Variabel"])
                    f4 = f4.sort_values("Importance").tail(8)
                    lolli(f4["Nama"].tolist(),
                          f4["Importance"].round(1).tolist(),
                          text=[f"{a:.0f}" for a in f4["Importance"]],
                          size=12)
                    top = f4.iloc[::-1]["Nama"].head(3).tolist()
                    result(f"Tiga peubah teratas: <b>{top[0]}</b>, "
                           f"<b>{top[1]}</b>, dan <b>{top[2]}</b>.")
                else:
                    k4 = cmx[cmx["Analisis"] == "Niat Pembelian Ulang"]
                    kls = ["No", "Maybe", "Yes"]
                    pv = k4.pivot_table(index="Aktual", columns="Prediksi",
                                        values="Jumlah", aggfunc="sum",
                                        fill_value=0).reindex(
                        index=kls, columns=kls, fill_value=0)
                    norm = pv.div(pv.sum(axis=1).replace(0, 1), axis=0)
                    fig = go.Figure(go.Heatmap(
                        z=norm.values, x=kls, y=kls, text=pv.values,
                        texttemplate="%{text}", showscale=False,
                        colorscale=[[0, BLUSH], [1, PRIMARY]], xgap=4, ygap=4,
                        textfont=dict(size=13),
                        hovertemplate="Aktual %{y}, prediksi %{x}: "
                        "%{text}<extra></extra>"))
                    fig.update_yaxes(autorange="reversed", title="Aktual")
                    fig.update_xaxes(title="Prediksi")
                    plot(fig)
                    rc = km[km["Analisis"] == "Niat Pembelian Ulang"
                            ].set_index("Kelas")["Recall"]
                    result(f"Recall: Yes <b>{rc['Yes'] * 100:.0f}%</b>, "
                           f"Maybe {rc['Maybe'] * 100:.0f}%, "
                           f"No {rc['No'] * 100:.0f}%. Kelas yang kecil sulit "
                           "ditebak.")
        # ---------------- FAMD
        with m1[1]:
            with card("m"):
                card_head("Unsupervised · FAMD",
                          "Peta kemiripan ulasan (angka + kategori)")
                v = toggle(["Peta ulasan", "Ragam", "Peubah"], "t_famd")
                d1 = float(ev["persen_ragam"].iloc[0])
                if v == "Peta ulasan":
                    pts = df if len(df) <= 2000 else df.sample(2000,
                                                               random_state=1)
                    fig = go.Figure()
                    for cls in ["Yes", "Maybe", "No"]:
                        s = pts[pts["beli_lagi"] == cls]
                        fig.add_scatter(
                            x=s["Dim1_jitter"], y=s["Dim2_jitter"],
                            mode="markers", name=cls,
                            marker=dict(size=5, opacity=0.55,
                                        color=BELI_COLORS[cls]),
                            hovertemplate=cls + "<extra></extra>")
                    fig.update_xaxes(title="Dim1: kepuasan",
                                     showgrid=True, gridcolor=LINE)
                    fig.update_yaxes(title="Dim2: niat beli ulang",
                                     showgrid=True, gridcolor=LINE)
                    plot(fig)
                    result(f"Dimensi 1 (kepuasan) menjelaskan <b>{fmt(d1)}%</b> "
                           "ragam. Dimensi 2 dibentuk oleh niat beli ulang.")
                elif v == "Ragam":
                    e8 = ev.head(6)
                    x = [f"Dim{int(i)}" for i in e8["dimensi"]]
                    fig = go.Figure()
                    fig.add_bar(name="% ragam", x=x,
                                y=e8["persen_ragam"].round(1).tolist(),
                                marker_color=PRIMARY)
                    fig.add_scatter(name="Kumulatif", x=x,
                                    y=e8["persen_ragam_kumulatif"].round(1)
                                    .tolist(), mode="lines+markers",
                                    line=dict(color=PRIMARY, width=2))
                    fig.update_yaxes(title="% ragam", showgrid=True,
                                     gridcolor=LINE)
                    plot(fig)
                    c3 = float(ev["persen_ragam_kumulatif"].iloc[2])
                    result(f"Tiga dimensi pertama menjelaskan <b>{fmt(c3, 0)}%"
                           "</b> ragam. Setelah dimensi 1, tambahannya "
                           "kecil.")
                else:
                    k2 = kp[(kp["peran"] == "Aktif") & (kp["dimensi"] <= 2)]
                    pv = k2.pivot_table(index="peubah", columns="dimensi",
                                        values="kontribusi_persen")
                    pv = pv.sort_values(1).tail(8)
                    fig = go.Figure()
                    fig.add_bar(name="Dim1", y=pv.index.str.replace("_", " "),
                                x=pv[1].round(1), orientation="h",
                                marker_color=PRIMARY)
                    fig.add_bar(name="Dim2", y=pv.index.str.replace("_", " "),
                                x=pv[2].round(1), orientation="h",
                                marker_color=PRIMARY)
                    fig.update_layout(barmode="group")
                    fig.update_xaxes(title="Kontribusi (%)", showgrid=True,
                                     gridcolor=LINE)
                    plot(fig)
                    result("Dimensi 1 dibentuk <b>rating</b> dan sub-rating. "
                           "Niat beli ulang ikut sebagai peubah aktif.")
        m2 = st.columns(2, gap="small")
        # ---------------- association
        with m2[0]:
            with card("m"):
                card_head("Unsupervised · Association rules",
                          "Pola yang sering muncul bersamaan")
                AN = {"Kata bersamaan": "A_kata_bersamaan",
                      "Pemicu tidak puas": "C_pemicu_ketidakpuasan",
                      "Tier harga": "D_tier_harga"}
                v = toggle(list(AN), "t_assoc")
                r = rules[rules["analisis"] == AN[v]].sort_values(
                    "lift", ascending=False).head(5)
                sep = " → " if v != "Kata bersamaan" else " + "
                t = r.iloc[::-1]
                cc = PLUM if v != "Kata bersamaan" else PRIMARY
                lolli((t["lhs_label"].astype(str) + sep
                       + t["rhs_label"].astype(str)).tolist(),
                      t["lift"].round(1).tolist(), colors=[cc] * len(t),
                      text=[fmt(x, 1) for x in t["lift"]], size=13)
                t0 = r.iloc[0]
                result(f"Terkuat: <b>{esc(t0['lhs_label'])}</b> dan "
                       f"<b>{esc(t0['rhs_label'])}</b> (lift {fmt(t0['lift'])}"
                       "). Lift di atas 1 berarti muncul bersama lebih "
                       "sering dari kebetulan.")
        # ---------------- clustering
        with m2[1]:
            with card("m"):
                card_head("Unsupervised · Clustering",
                          "K-Means mengelompokkan produk yang mirip")
                v = toggle(["Peta produk", "Profil", "Silhouette"], "t_clu")
                cl_["klaster"] = "Klaster " + cl_["cluster"].astype(str)
                g = cl_.groupby("klaster").agg(
                    n=("nama_produk", "size"), bl=("beli_lagi_rate", "mean"),
                    rt=("rating_rata", "mean"), hg=("harga_tengah", "mean"))
                hi, lo = g["bl"].idxmax(), g["bl"].idxmin()
                warna = {hi: PRIMARY, lo: PLUM}
                if v == "Peta produk":
                    fig = go.Figure()
                    for kl in [hi, lo]:
                        s = cl_[cl_["klaster"] == kl]
                        fig.add_scatter(
                            x=s["rating_rata"], y=s["beli_lagi_rate"] * 100,
                            mode="markers", name=f"{kl} ({len(s)})",
                            marker=dict(size=8, opacity=0.75,
                                        color=warna[kl]),
                            text=s["nama_produk"],
                            hovertemplate="%{text}<br>rating %{x:.2f}, beli "
                            "lagi %{y:.0f}%<extra></extra>")
                    fig.update_xaxes(title="Rating rata-rata produk",
                                     showgrid=True, gridcolor=LINE)
                    fig.update_yaxes(title="% beli lagi", showgrid=True,
                                     gridcolor=LINE)
                    ev = plot(fig, key=f"clu_map_{reset_n}", select="rerun")
                    pts = sel_points(ev)
                    shown = None
                    if pts:
                        try:
                            kl = [hi, lo][int(pts[0]["curve_number"])]
                            srow = cl_[cl_["klaster"] == kl].reset_index(
                                drop=True).iloc[int(pts[0]["point_index"])]
                            shown = (f"<b>{esc(srow['nama_produk'])}</b>: "
                                     f"rating {fmt(srow['rating_rata'], 2)}, "
                                     f"beli ulang "
                                     f"{fmt(srow['beli_lagi_rate'] * 100, 0)}% "
                                     f"({kl}).")
                        except Exception:
                            shown = None
                    result(shown or
                           f"Dua kelompok produk: beli ulang <b>"
                           f"{fmt(g.loc[hi, 'bl'] * 100, 0)}%</b> ({hi}) dan "
                           f"<b>{fmt(g.loc[lo, 'bl'] * 100, 0)}%</b> ({lo}). "
                           "Klik satu titik untuk melihat produknya.")
                elif v == "Profil":
                    mets = [("rating_rata", "Rating"),
                            ("efektivitas", "Efektivitas"),
                            ("kemasan", "Kemasan"),
                            ("tekstur", "Tekstur"),
                            ("kualitas_harga", "Kualitas harga")]
                    fig = go.Figure()
                    for kl in [hi, lo]:
                        s = cl_[cl_["klaster"] == kl]
                        fig.add_bar(name=kl, x=[m[1] for m in mets],
                                    y=[s[m[0]].mean() for m in mets],
                                    marker_color=warna[kl],
                                    text=[fmt(s[m[0]].mean(), 2)
                                          for m in mets],
                                    textposition="outside",
                                    cliponaxis=False)
                    fig.update_layout(barmode="group")
                    fig.update_yaxes(visible=False, range=[4.5, 5.0])
                    plot(fig)
                    result("Klaster yang lebih puas unggul di semua sub-rating. "
                           f"Harga tengahnya {fmt(g.loc[hi, 'hg'] / 1000, 0)} "
                           f"rb dan {fmt(g.loc[lo, 'hg'] / 1000, 0)} rb.")
                else:
                    sx = sil["k"].astype(str).tolist()
                    fig = go.Figure(go.Bar(
                        x=sx, y=sil["silhouette"].tolist(),
                        marker_color=[PRIMARY if k_ == 2 else GREY
                                      for k_ in sil["k"]],
                        text=[f"{a:.3f}" for a in sil["silhouette"]],
                        textposition="outside", cliponaxis=False))
                    fig.update_xaxes(title="Jumlah klaster (k)")
                    fig.update_yaxes(visible=False,
                                     range=[0, sil["silhouette"].max() * 1.3])
                    plot(fig)
                    result(f"k=2 paling baik, silhouette <b>{fmt(sil2, 3)}</b>. "
                           "Pemisahannya lemah, jadi anggap ini segmentasi "
                           "awal.")


# ================================================================ HALAMAN 4
def page_insight():
    header("Jadi, <i>Beli Lagi</i>?",
           "Temuan, kesimpulan, dan saran dari seluruh data")
    d = df_all
    rec_y = pct_yes(d.loc[d["rekomendasi"] == "Yes", "beli_lagi"])
    rec_n = pct_yes(d.loc[d["rekomendasi"] == "No", "beli_lagi"])
    lama_y = pct_yes(d.loc[d["lama_penggunaan"] == "> 1 tahun", "beli_lagi"])
    baru = (d["lama_penggunaan"] == "< 1 minggu").mean() * 100
    ef = efek_hubungan(d)
    eta_h = ef.loc[ef["Peubah"] == "Harga", "Kekuatan"].iloc[0]
    eta_r = ef.loc[ef["Peubah"] == "Rating", "Kekuatan"].iloc[0]
    km, cmx, _ = load_klas()
    r4 = klas_summary(km, cmx).query("analisis == 'Niat Pembelian Ulang'"
                                     ).iloc[0]
    cl_ = load_csv("cluster.csv")
    g = cl_.groupby("cluster")["beli_lagi_rate"].mean() * 100
    sil2 = float(load_csv("cluster_silhouette.csv").query("k == 2"
                 )["silhouette"].iloc[0])

    cl, cr = st.columns([1.25, 3], gap="small")
    with cl:
        insight(PAGES[3], "Kenapa orang beli lagi?", "Rasa puas",
                "pendorong utama beli ulang",
                [("Yang kelihatan",
                  f"Pembeli setia adalah yang merekomendasikan produk "
                  f"({fmt(rec_y, 0)}% ingin beli lagi) dan sudah lama "
                  f"memakainya ({fmt(lama_y, 0)}% setelah setahun). Harga "
                  f"nyaris tidak berperan (η {fmt(eta_h, 2)})."),
                 ("Kenapa begitu",
                  "Rekomendasi dan rating mengukur rasa puas, sedangkan lama "
                  "pakai menandakan produknya cocok di kulit. Harga tidak "
                  "membedakan, jadi produk murah belum tentu dibeli ulang."),
                 ("Lalu apa",
                  "Brand bisa fokus ke efektivitas dan tekstur, serta "
                  "mengajak pembeli merekomendasikan. Sociolla bisa "
                  "menampilkan ulasan yang sesuai tipe kulit pembaca.")],
                "Kalau ingin orang beli lagi, buat mereka puas dulu.")
    with cr:
        s = st.columns(3, gap="small")
        stat_card(s[0], "Rekomendasi",
                  f"{fmt(rec_y, 0)}% vs {fmt(rec_n, 0)}%",
                  "ingin beli lagi: yang merekomendasikan vs tidak",
                  minibars([("Ya", rec_y / 100, PRIMARY, f"{rec_y:.0f}%"),
                            ("Tidak", rec_n / 100, PLUM, f"{rec_n:.0f}%")]))
        stat_card(s[1], "Lama pakai", f"{fmt(lama_y, 0)}%",
                  "pemakai di atas setahun ingin beli lagi",
                  ring(lama_y, f"{lama_y:.0f}%"))
        stat_card(s[2], "Harga", f"η {fmt(eta_h, 2)}",
                  "kaitan harga dengan beli ulang, hampir nol",
                  minibars([("Harga", eta_h / 0.6, GREY, fmt(eta_h, 2)),
                            ("Rating", eta_r / 0.6, PRIMARY, fmt(eta_r, 2))]))
        mid = st.columns([1.15, 1], gap="small")
        with mid[0]:
            with card("q"):
                card_head("Faktor penentu beli ulang",
                          "η: 0 = tidak ada kaitan, 1 = sangat kuat")
                chart_efek(d, size=10)
        with mid[1]:
            with card("q"):
                card_head("Kesimpulan", "Menjawab tujuan proyek")
                st.markdown(
                    '<ul class="bl">'
                    '<li>Beli ulang didorong rekomendasi, rating, dan lama '
                    'pakai. Harga tidak ikut menentukan.</li>'
                    f'<li>Produk terbagi dua menurut kepuasan: beli ulang '
                    f'{fmt(g.max(), 0)}% dan {fmt(g.min(), 0)}%.</li>'
                    f'<li>Model hanya unggul tipis dari tebakan mayoritas '
                    f'({fmt(r4["acc"], 0)}% vs {fmt(r4["nir"], 0)}%).</li>'
                    '</ul>', unsafe_allow_html=True)
        bot = st.columns(3, gap="small")
        with bot[0]:
            with card("q"):
                card_head("Saran untuk brand", "Bisa langsung dikerjakan")
                st.markdown(
                    '<ul class="bl">'
                    '<li>Ajak pelanggan menulis ulasan dan '
                    'merekomendasikan.</li>'
                    '<li>Perbaiki efektivitas dan tekstur.</li>'
                    '<li>Tinjau produk di klaster beli ulang rendah.</li>'
                    '</ul>', unsafe_allow_html=True)
        with bot[1]:
            with card("q"):
                card_head("Saran untuk Sociolla", "Untuk pembaca ulasan")
                st.markdown(
                    '<ul class="bl">'
                    '<li>Tampilkan ulasan yang sesuai tipe kulit '
                    'pembaca.</li>'
                    '<li>Pantau keluhan lewat kata kunci ulasan.</li>'
                    '<li>Ajak pengguna menulis lagi setelah lama '
                    'memakai.</li></ul>', unsafe_allow_html=True)
        with bot[2]:
            with card("q"):
                card_head("Hal yang perlu diingat", "Supaya hasil dibaca "
                          "dengan pas")
                st.markdown(
                    '<ul class="bl">'
                    f'<li>{fmt(baru, 0)}% ulasan berasal dari pemakai di '
                    'bawah seminggu.</li>'
                    '<li>Yes sekitar 85%, jadi datanya timpang.</li>'
                    f'<li>Silhouette {fmt(sil2, 2)} tergolong lemah; '
                    'sentimen masih sederhana; hanya satu platform.</li></ul>',
                    unsafe_allow_html=True)


{PAGES[0]: page_overview, PAGES[1]: page_eda, PAGES[2]: page_model,
 PAGES[3]: page_insight}[page]()
