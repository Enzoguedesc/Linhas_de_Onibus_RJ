import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import math

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FluxRio · GPS Urbano",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = (
    "https://dados.mobilidade.rio/gps/sppo?dataInicial=2026-03-09+08:04:00&dataFinal=2026-03-09+08:09:00"
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# ── Valores Python apenas para inline styles e mapa ──────────────────────────
THEMES = {
    True: dict(
        map_tiles = "CartoDB dark_matter",
        danger    = "#ef4444",
        accent    = "#00d4ff",
        accent3   = "#10b981",
        text2     = "#6b82a8",
        text3     = "#3d5278",
    ),
    False: dict(
        map_tiles = "CartoDB Positron",
        danger    = "#ef4444",
        accent    = "#0ea5e9",
        accent3   = "#10b981",
        text2     = "#475569",
        text3     = "#94a3b8",
    ),
}
T = THEMES[st.session_state.dark_mode]

# ── CSS injetado UMA ÚNICA VEZ com CSS variables ──────────────────────────────
# Não usa f-string — troca de tema via JS alterando as vars no :root
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Orbitron:wght@600;700;800;900&display=swap');

/* ── CSS Variables — dark (padrão) ── */
:root {
    --bg:          #080c14;
    --bg2:         #0d1220;
    --card:        #0f1623;
    --card2:       #141e2e;
    --sidebar:     #090d18;
    --border:      #1e2d45;
    --border2:     #243350;
    --text:        #e2eaf8;
    --text2:       #6b82a8;
    --text3:       #3d5278;
    --accent:      #00d4ff;
    --accent2:     #7c3aed;
    --accent3:     #10b981;
    --danger:      #ef4444;
    --warn:        #f59e0b;
    --glow:        rgba(0,212,255,0.15);
    --shadow:      rgba(0,0,0,0.6);
    --shadow2:     rgba(0,212,255,0.08);
    --badge-bg:    rgba(0,212,255,0.08);
    --metric-grad: linear-gradient(135deg, #0f1623 0%, #141e2e 100%);
    --neon:        0 0 20px rgba(0,212,255,0.3), 0 0 60px rgba(0,212,255,0.1);
}

/* ── CSS Variables — light ── */
:root.light {
    --bg:          #f0f4fc;
    --bg2:         #e8edf8;
    --card:        #ffffff;
    --card2:       #f5f8ff;
    --sidebar:     #ffffff;
    --border:      #d1daf0;
    --border2:     #bfcae8;
    --text:        #0f172a;
    --text2:       #475569;
    --text3:       #94a3b8;
    --accent:      #0ea5e9;
    --accent2:     #7c3aed;
    --accent3:     #10b981;
    --danger:      #ef4444;
    --warn:        #f59e0b;
    --glow:        rgba(14,165,233,0.08);
    --shadow:      rgba(15,23,42,0.08);
    --shadow2:     rgba(14,165,233,0.06);
    --badge-bg:    rgba(14,165,233,0.08);
    --metric-grad: linear-gradient(135deg, #ffffff 0%, #f5f8ff 100%);
    --neon:        0 4px 24px rgba(14,165,233,0.15);
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); opacity: 0.5; }

[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 4px 0 24px var(--shadow) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stMarkdown p { color: var(--text2) !important; }

[data-testid="stSelectbox"] > div > div {
    background: var(--card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow) !important;
}

.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    background: var(--card2) !important;
    color: var(--text2) !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.22s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 2px 8px var(--shadow) !important;
}
.stButton > button:hover {
    background: rgba(0,212,255,0.08) !important;
    border-color: rgba(0,212,255,0.4) !important;
    color: var(--accent) !important;
    box-shadow: 0 4px 20px var(--shadow2) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.13), rgba(124,58,237,0.13)) !important;
    border-color: rgba(0,212,255,0.35) !important;
    color: var(--accent) !important;
    box-shadow: 0 4px 20px var(--shadow2) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(0,212,255,0.22), rgba(124,58,237,0.22)) !important;
    border-color: var(--accent) !important;
    box-shadow: var(--neon) !important;
    transform: translateY(-2px) !important;
}

[data-testid="metric-container"] {
    background: var(--metric-grad) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.4rem 1.5rem !important;
    box-shadow: 0 4px 24px var(--shadow) !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    opacity: 0;
    transition: opacity 0.25s;
}
[data-testid="metric-container"]:hover {
    border-color: rgba(0,212,255,0.35) !important;
    box-shadow: 0 8px 32px var(--shadow), var(--neon) !important;
    transform: translateY(-4px) !important;
}
[data-testid="metric-container"]:hover::before { opacity: 1; }

[data-testid="stMetricLabel"] > div {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--text2) !important;
}
[data-testid="stMetricValue"] > div {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    letter-spacing: -0.02em !important;
}

[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] * {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1rem 0 !important; }

/* ── Custom components ── */
.brand { display:flex; align-items:center; gap:0.75rem; padding:0.25rem 0 1.25rem 0; }
.brand-icon {
    width:36px; height:36px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius:10px; display:flex; align-items:center; justify-content:center;
    font-size:1.1rem; box-shadow:0 4px 16px var(--shadow2); flex-shrink:0;
}
.brand-name {
    font-family:'Orbitron',sans-serif; font-weight:800; font-size:1.05rem; letter-spacing:0.06em;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.brand-sub { font-size:0.65rem; font-weight:500; letter-spacing:0.12em; text-transform:uppercase; color:var(--text3); }

.s-stat {
    display:flex; align-items:center; justify-content:space-between;
    padding:0.6rem 0.85rem; border-radius:10px;
    background:var(--card2); border:1px solid var(--border); margin-bottom:0.45rem;
    transition:border-color 0.2s;
}
.s-stat:hover { border-color: rgba(0,212,255,0.27); }
.s-stat-label { font-size:0.73rem; font-weight:500; color:var(--text2); }
.s-stat-val { font-family:'JetBrains Mono',monospace; font-size:0.82rem; font-weight:700; color:var(--accent); }

.page-hero {
    padding:1.5rem 2rem; background:var(--card); border:1px solid var(--border);
    border-radius:20px; margin-bottom:1.5rem; box-shadow:0 4px 24px var(--shadow);
    position:relative; overflow:hidden;
}
.page-hero::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg, var(--accent), var(--accent2), var(--accent3));
}
.page-hero::after {
    content:'FLUXRIO'; font-family:'Orbitron',sans-serif; position:absolute;
    right:2rem; top:50%; transform:translateY(-50%); font-size:5rem; font-weight:900;
    color:var(--accent); opacity:0.03; letter-spacing:0.1em; pointer-events:none;
}
.hero-line-number {
    font-family:'Orbitron',sans-serif; font-size:2.6rem; font-weight:900;
    background:linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    line-height:1; letter-spacing:0.04em;
}
.hero-label { font-size:0.7rem; font-weight:600; letter-spacing:0.14em; text-transform:uppercase; color:var(--text3); margin-bottom:0.3rem; }
.hero-meta { font-size:0.82rem; color:var(--text2); margin-top:0.75rem; display:flex; align-items:center; gap:1rem; flex-wrap:wrap; }
.hero-sep { width:4px; height:4px; background:var(--border2); border-radius:50%; }

.live-badge {
    display:inline-flex; align-items:center; gap:0.45rem;
    background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.27);
    color:var(--accent3); border-radius:20px; padding:0.25rem 0.85rem;
    font-size:0.7rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
}
.live-dot {
    width:6px; height:6px; border-radius:50%; background:var(--accent3);
    animation:blink 1.4s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.3;transform:scale(0.7)} }

.pill {
    display:inline-flex; align-items:center; gap:0.3rem;
    background:var(--badge-bg); border:1px solid rgba(0,212,255,0.2);
    color:var(--text2); border-radius:20px; padding:0.2rem 0.7rem;
    font-size:0.72rem; font-weight:500;
}

.section-header { display:flex; align-items:center; gap:0.6rem; margin-bottom:1rem; }
.section-header-icon {
    width:28px; height:28px;
    background:linear-gradient(135deg, rgba(0,212,255,0.13), rgba(124,58,237,0.13));
    border:1px solid rgba(0,212,255,0.2); border-radius:8px;
    display:flex; align-items:center; justify-content:center; font-size:0.85rem;
}
.section-header-title { font-size:0.9rem; font-weight:700; color:var(--text); letter-spacing:0.02em; }

.rank-card {
    display:flex; align-items:center; gap:0.75rem; padding:0.7rem 0.9rem;
    border-radius:12px; background:var(--card2); border:1px solid var(--border);
    margin-bottom:0.45rem; transition:all 0.2s cubic-bezier(0.4,0,0.2,1);
}
.rank-card:hover { background:var(--card); border-color:rgba(0,212,255,0.35); transform:translateX(4px); box-shadow:0 4px 16px var(--shadow); }
.rank-pos { font-family:'JetBrains Mono',monospace; font-size:0.72rem; font-weight:700; color:var(--text3); width:20px; text-align:center; flex-shrink:0; }
.rank-id { font-family:'JetBrains Mono',monospace; font-size:0.8rem; font-weight:600; color:var(--text); flex:1; }
.rank-right { display:flex; flex-direction:column; align-items:flex-end; gap:4px; }
.rank-speed { font-family:'JetBrains Mono',monospace; font-size:0.82rem; font-weight:700; color:var(--accent); }
.rank-bar-track { width:56px; height:4px; background:var(--border); border-radius:2px; overflow:hidden; }
.rank-bar-fill { height:100%; border-radius:2px; background:linear-gradient(90deg, var(--accent), var(--accent2)); }

.time-card {
    background:var(--card2); border:1px solid var(--border); border-radius:14px;
    padding:1rem 1.1rem; margin-bottom:0.6rem; transition:border-color 0.2s;
}
.time-card:hover { border-color: rgba(0,212,255,0.27); }
.time-card-label { font-size:0.67rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:var(--text3); margin-bottom:0.3rem; }
.time-card-value { font-family:'JetBrains Mono',monospace; font-size:1.25rem; font-weight:700; color:var(--text); }

.map-wrapper { background:var(--card); border:1px solid var(--border); border-radius:18px; overflow:hidden; box-shadow:0 8px 32px var(--shadow); }
.map-toolbar { display:flex; align-items:center; justify-content:space-between; padding:0.9rem 1.2rem; border-bottom:1px solid var(--border); background:var(--card2); }
.map-toolbar-title { font-size:0.82rem; font-weight:700; color:var(--text); letter-spacing:0.04em; display:flex; align-items:center; gap:0.5rem; }
.map-legend { display:flex; gap:1.2rem; font-size:0.7rem; color:var(--text2); align-items:center; flex-wrap:wrap; }
.legend-dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:4px; }

.footer { text-align:center; padding:1.5rem; border-top:1px solid var(--border); margin-top:2rem; font-size:0.72rem; color:var(--text3); letter-spacing:0.04em; }
.footer span { color:var(--accent) !important; font-family:'Orbitron',sans-serif !important; font-weight:700 !important; font-size:0.7rem !important; }

p { color: var(--text) !important; }
label { color: var(--text2) !important; font-size: 0.78rem !important; font-weight: 500 !important; }
h1,h2,h3,h4,h5,h6 { color: var(--text) !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text2) !important; }
.stAlert { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Troca de tema via JS — altera apenas :root, sem re-injetar CSS ────────────
theme_class = "" if st.session_state.dark_mode else "light"
st.markdown(f"""
<script>
    (function() {{
        var root = document.documentElement;
        root.className = root.className.replace(/\\blight\\b/g, '').trim();
        if ("{theme_class}" === "light") root.classList.add("light");
    }})();
</script>
""", unsafe_allow_html=True)


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner="⬡  Sincronizando com a API de Mobilidade do Rio...")
def load_data() -> pd.DataFrame:
    df = pd.read_json(API_URL)
    df["latitude"]  = df["latitude"].str.replace(",", ".", regex=False).astype(float)
    df["longitude"] = df["longitude"].str.replace(",", ".", regex=False).astype(float)
    for col in ["datahora", "datahoraenvio", "datahoraservidor"]:
        df[f"{col}_gregoriana"] = pd.to_datetime(df[col], unit="ms")
    df = df.drop(columns=["datahora", "datahoraenvio", "datahoraservidor"])
    return df


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    dφ = math.radians(lat2 - lat1)
    dλ = math.radians(lon2 - lon1)
    a  = math.sin(dφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(dλ/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def calc_dist(grp: pd.DataFrame) -> float:
    g = grp.sort_values("datahora_gregoriana")
    lt, ln = g["latitude"].values, g["longitude"].values
    return sum(haversine(lt[i-1], ln[i-1], lt[i], ln[i]) for i in range(1, len(lt)))


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">⬡</div>
        <div class="brand-text">
            <div class="brand-name">FluxRio</div>
            <div class="brand-sub">GPS · Mobilidade Urbana</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    icon  = "☀️" if st.session_state.dark_mode else "🌙"
    label = "Modo Claro" if st.session_state.dark_mode else "Modo Escuro"
    if st.button(f"{icon}  {label}", use_container_width=True, type="primary"):
        st.session_state.dark_mode = not st.session_state.dark_mode

    st.divider()

    if st.button("↻  Atualizar Dados", use_container_width=True):
        st.cache_data.clear()

    df = load_data()

    st.divider()

    st.markdown("<label>LINHA DO ÔNIBUS</label>", unsafe_allow_html=True)
    linhas = sorted(df["linha"].unique().tolist(), key=str)
    linha_sel = st.selectbox(
        "Linha", options=linhas,
        index=linhas.index("630") if "630" in linhas else 0,
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("<label>VISÃO GERAL · TODAS AS LINHAS</label>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="s-stat"><span class="s-stat-label">⬡ Registros totais</span><span class="s-stat-val">{len(df):,}</span></div>
    <div class="s-stat"><span class="s-stat-label">⬡ Linhas ativas</span><span class="s-stat-val">{df['linha'].nunique()}</span></div>
    <div class="s-stat"><span class="s-stat-label">⬡ Frota monitorada</span><span class="s-stat-val">{df['ordem'].nunique():,}</span></div>
    <div class="s-stat"><span class="s-stat-label">⬡ Vel. máx. global</span><span class="s-stat-val">{df['velocidade'].max()} km/h</span></div>
    <div class="s-stat"><span class="s-stat-label">⬡ Sincronizado às</span><span class="s-stat-val">{datetime.now().strftime('%H:%M:%S')}</span></div>
    """, unsafe_allow_html=True)


# ── Filter & compute ──────────────────────────────────────────────────────────
df_f      = df[df["linha"] == linha_sel].copy()
vel_med   = round(df_f["velocidade"].mean(), 1) if not df_f.empty else 0
vel_max   = int(df_f["velocidade"].max())        if not df_f.empty else 0
n_bus     = df_f["ordem"].nunique()
dist_tot  = 0.0
bus_stats = []

for bid, grp in df_f.groupby("ordem"):
    d = calc_dist(grp)
    dist_tot += d
    bus_stats.append({
        "ordem":     bid,
        "vel_media": round(grp["velocidade"].mean(), 1),
        "vel_max":   int(grp["velocidade"].max()),
        "dist_km":   round(d, 2),
        "registros": len(grp),
    })

df_stats = pd.DataFrame(bus_stats).sort_values("vel_media", ascending=False)
parados  = int((df_stats["dist_km"] == 0).sum()) if not df_stats.empty else 0
mov_pct  = round((1 - parados / n_bus) * 100, 1) if n_bus > 0 else 0


# ── HERO ──────────────────────────────────────────────────────────────────────
t_ini = df_f["datahora_gregoriana"].min().strftime("%H:%M") if not df_f.empty else "--"
t_fim = df_f["datahora_gregoriana"].max().strftime("%H:%M") if not df_f.empty else "--"

st.markdown(f"""
<div class="page-hero">
    <div style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:1rem;">
        <div>
            <div class="hero-label">Linha selecionada</div>
            <div class="hero-line-number">{linha_sel}</div>
            <div class="hero-meta">
                <span class="live-badge"><span class="live-dot"></span>Tempo Real</span>
                <span class="hero-sep"></span>
                <span class="pill">📍 Rio de Janeiro, RJ</span>
                <span class="pill">🗓 09 Mar 2026</span>
                <span class="pill">⏱ {t_ini} → {t_fim}</span>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:0.68rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:{T['text3']}; margin-bottom:0.3rem;">Em movimento</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:2rem; font-weight:700; color:{T['accent3']};">{mov_pct}%</div>
            <div style="font-size:0.72rem; color:{T['text2']}; margin-top:0.2rem;">{n_bus} veículos · {len(df_f)} registros GPS</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── METRICS ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4, gap="medium")
c1.metric("⚡  Velocidade Média",  f"{vel_med} km/h",    help="Média de todos os registros GPS da linha")
c2.metric("🏎  Velocidade Máxima", f"{vel_max} km/h",    help="Pico de velocidade registrado na janela de tempo")
c3.metric("📏  Distância Total",   f"{dist_tot:.2f} km", help="Soma das distâncias percorridas (fórmula Haversine)")
c4.metric("🚌  Ônibus na Linha",   f"{n_bus} veículos",  help="Total de veículos com registros na linha selecionada")

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)


# ── MAP + PANEL ───────────────────────────────────────────────────────────────
col_map, col_panel = st.columns([3, 1], gap="large")

with col_map:
    st.markdown(f"""
    <div class="map-wrapper">
        <div class="map-toolbar">
            <div class="map-toolbar-title">⬡ &nbsp; Mapa de Trajetórias — Linha {linha_sel}</div>
            <div class="map-legend">
                <span><span class="legend-dot" style="background:#ef4444"></span>Parado</span>
                <span><span class="legend-dot" style="background:#4f8ef7"></span>Lento</span>
                <span><span class="legend-dot" style="background:#10b981"></span>Rápido</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df_f.empty:
        st.warning("Nenhum registro encontrado para esta linha.")
    else:
        clat = df_f["latitude"].mean()
        clon = df_f["longitude"].mean()
        mapa = folium.Map(location=[clat, clon], zoom_start=13, tiles=T["map_tiles"])

        for _, r in df_f.iterrows():
            cor = "#ef4444" if r["velocidade"] == 0 else ("#10b981" if r["velocidade"] > 30 else "#4f8ef7")
            folium.CircleMarker(
                location=[r["latitude"], r["longitude"]],
                radius=3.5, color=cor, fill=True, fill_opacity=0.7, weight=0,
                tooltip=f"🚌 {r['ordem']}  ·  ⚡ {r['velocidade']} km/h",
            ).add_to(mapa)

        palette = ["#00d4ff","#7c3aed","#10b981","#f59e0b","#ef4444","#06b6d4","#a855f7","#34d399"]
        for idx, (bid, grp) in enumerate(df_f.groupby("ordem")):
            g   = grp.sort_values("datahora_gregoriana")
            tr  = g[["latitude","longitude"]].values.tolist()
            cor = palette[idx % len(palette)]
            if len(tr) > 1:
                folium.PolyLine(tr, color=cor, weight=3, opacity=0.85, tooltip=f"🚌 {bid}").add_to(mapa)
                folium.Marker(tr[0],
                    tooltip=f"▶ Início · {bid} · {g['datahora_gregoriana'].iloc[0].strftime('%H:%M:%S')}",
                    icon=folium.Icon(color="green", icon="play", prefix="fa")).add_to(mapa)
                folium.Marker(tr[-1],
                    tooltip=f"⏹ Fim · {bid} · {g['datahora_gregoriana'].iloc[-1].strftime('%H:%M:%S')}",
                    icon=folium.Icon(color="red", icon="stop", prefix="fa")).add_to(mapa)

        st_folium(mapa, use_container_width=True, height=460)

with col_panel:
    st.markdown("""
    <div class="section-header">
        <div class="section-header-icon">🏆</div>
        <div class="section-header-title">Ranking de Velocidade</div>
    </div>
    """, unsafe_allow_html=True)

    if not df_stats.empty:
        ref = df_stats["vel_media"].max() or 1
        for pos, (_, r) in enumerate(df_stats.head(5).iterrows(), 1):
            pct   = int(r["vel_media"] / ref * 100)
            medal = "🥇" if pos == 1 else ("🥈" if pos == 2 else ("🥉" if pos == 3 else f"#{pos}"))
            st.markdown(f"""
            <div class="rank-card">
                <div class="rank-pos">{medal}</div>
                <div class="rank-id">{r['ordem']}</div>
                <div class="rank-right">
                    <div class="rank-speed">{r['vel_media']} km/h</div>
                    <div class="rank-bar-track"><div class="rank-bar-fill" style="width:{pct}%"></div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)


# ── JANELA DE COLETA — horizontal abaixo do mapa ─────────────────────────────
if not df_f.empty:
    t0  = df_f["datahora_gregoriana"].min()
    t1  = df_f["datahora_gregoriana"].max()
    dur = str(t1 - t0).split(".")[0]
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:0.75rem; margin-bottom:1.5rem;">
        <div class="time-card" style="margin-bottom:0;">
            <div class="time-card-label">⏱ Início da Coleta</div>
            <div class="time-card-value">{t0.strftime('%H:%M:%S')}</div>
            <div style="font-size:0.68rem; color:{T['text3']}; margin-top:0.2rem;">{t0.strftime('%d/%m/%Y')}</div>
        </div>
        <div class="time-card" style="margin-bottom:0;">
            <div class="time-card-label">⏹ Fim da Coleta</div>
            <div class="time-card-value">{t1.strftime('%H:%M:%S')}</div>
            <div style="font-size:0.68rem; color:{T['text3']}; margin-top:0.2rem;">{t1.strftime('%d/%m/%Y')}</div>
        </div>
        <div class="time-card" style="margin-bottom:0;">
            <div class="time-card-label">⌛ Duração Total</div>
            <div class="time-card-value">{dur}</div>
            <div style="font-size:0.68rem; color:{T['text3']}; margin-top:0.2rem;">hh:mm:ss</div>
        </div>
        <div class="time-card" style="margin-bottom:0;">
            <div class="time-card-label">🔴 Ônibus Parados</div>
            <div class="time-card-value" style="color:{T['danger']};">{parados}</div>
            <div style="font-size:0.68rem; color:{T['text3']}; margin-top:0.2rem;">0 km no período</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)


# ── ESTATÍSTICAS POR ÔNIBUS ───────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <div class="section-header-icon">📊</div>
    <div class="section-header-title">Estatísticas por Ônibus</div>
</div>
""", unsafe_allow_html=True)

if not df_stats.empty:
    st.dataframe(
        df_stats.reset_index(drop=True),
        use_container_width=True, height=320,
        column_config={
            "ordem":     st.column_config.TextColumn("🚌 Ônibus"),
            "vel_media": st.column_config.ProgressColumn(
                "⚡ Vel. Média", min_value=0, max_value=100, format="%.1f km/h"),
            "vel_max":   st.column_config.NumberColumn("🏎 Vel. Máx.",  format="%d km/h"),
            "dist_km":   st.column_config.NumberColumn("📏 Distância",  format="%.2f km"),
            "registros": st.column_config.NumberColumn("📡 Registros GPS"),
        },
    )


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    <span>FluxRio</span> &nbsp;·&nbsp; GPS Mobilidade Urbana &nbsp;·&nbsp;
    Fonte: dados.mobilidade.rio &nbsp;·&nbsp;
    {'🌙 Escuro' if st.session_state.dark_mode else '☀️ Claro'} &nbsp;·&nbsp;
    {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
</div>
""", unsafe_allow_html=True)