"""
Dashboard: "Maddaloni attraverso i tuoi occhi"
Analisi di co-progettazione dell'immaginario urbano
Autore: Progetto Maddaloni — Dashboard v1.0
Requisiti: pip install streamlit plotly pandas scipy numpy
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
import io

# ─────────────────────────────────────────────
# CONFIGURAZIONE PAGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Maddaloni attraverso i tuoi occhi",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# STILE GLOBALE  (Academic Clean)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Inter:wght@300;400;500&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #fafaf8; }
    .block-container { padding: 2rem 3rem; max-width: 1400px; }

    /* Header */
    .dash-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
        color: white;
        padding: 2.5rem 3rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }
    .dash-header h1 { font-family: 'Playfair Display', serif; font-size: 2.2rem; margin: 0; letter-spacing: 0.02em; }
    .dash-header p  { font-size: 0.95rem; opacity: 0.75; margin: 0.4rem 0 0; }

    /* KPI Cards */
    .kpi-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
    .kpi-card {
        flex: 1; background: white; border-radius: 10px; padding: 1.2rem 1.5rem;
        border-left: 4px solid #0f3460;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .kpi-card .val { font-size: 2rem; font-weight: 600; color: #0f3460; }
    .kpi-card .lab { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: #888; margin-top: 0.2rem; }

    /* Section titles */
    .section-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem; color: #1a1a2e;
        border-bottom: 2px solid #e8e4dc;
        padding-bottom: 0.5rem; margin: 2rem 0 1rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #1a1a2e; }
    [data-testid="stSidebar"] * { color: #e8e4dc !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; border-bottom: 2px solid #e8e4dc; }
    .stTabs [data-baseweb="tab"] {
        background: transparent; border-radius: 6px 6px 0 0;
        font-size: 0.9rem; font-weight: 500; color: #666;
        padding: 0.5rem 1.2rem;
    }
    .stTabs [aria-selected="true"] { background: #0f3460 !important; color: white !important; }

    /* Download button */
    .stDownloadButton > button {
        background: #0f3460; color: white; border: none;
        border-radius: 6px; font-size: 0.85rem; padding: 0.4rem 1rem;
    }
    .stDownloadButton > button:hover { background: #16213e; }

    div[data-testid="metric-container"] { background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# COSTANTI
# ─────────────────────────────────────────────
SEMANTIC_MAP = {
    "Estremamente ruvido":       ("Ruvido/Liscio",          -2),
    "Prevalentemente ruvido":    ("Ruvido/Liscio",          -1),
    "Prevalentemente liscio":    ("Ruvido/Liscio",           1),
    "Estremamente liscio":       ("Ruvido/Liscio",           2),

    "Estremamente tagliente":    ("Tagliente/Morbido",      -2),
    "Prevalentemente tagliente": ("Tagliente/Morbido",      -1),
    "Prevalentemente morbido":   ("Tagliente/Morbido",       1),
    "Estremamente morbido":      ("Tagliente/Morbido",       2),

    "Estremamente pesante":      ("Pesante/Leggero",         -2),
    "Prevalentemente pesante":   ("Pesante/Leggero",         -1),
    "Prevalentemente leggero":   ("Pesante/Leggero",          1),
    "Estremamente leggero":      ("Pesante/Leggero",          2),

    "Estremamente opaco":        ("Opaco/Riflettente",       -2),
    "Prevalentemente opaco":     ("Opaco/Riflettente",       -1),
    "Prevalentemente riflettente":("Opaco/Riflettente",       1),
    "Estremamente riflettente":  ("Opaco/Riflettente",        2),

    "Estremamente selvaggio":    ("Selvaggio/Urbano",        -2),
    "Prevalentemente selvaggio": ("Selvaggio/Urbano",        -1),
    "Prevalentemente urbano":    ("Selvaggio/Urbano",         1),
    "Estremamente urbano":       ("Selvaggio/Urbano",         2),

    "Estremamente antica":       ("Antica/Futuristica",      -2),
    "Prevalentemente antica":    ("Antica/Futuristica",      -1),
    "Prevalentemente futuristica":("Antica/Futuristica",      1),
    "Estremamente futuristica":  ("Antica/Futuristica",       2),

    "Estremamente istituzionale":("Istituzionale/Popolare",  -2),
    "Prevalentemente istituzionale":("Istituzionale/Popolare",-1),
    "Prevalentemente popolare":  ("Istituzionale/Popolare",   1),
    "Estremamente popolare":     ("Istituzionale/Popolare",   2),

    "Estremamente riflessiva":   ("Riflessiva/Impetuosa",    -2),
    "Prevalentemente riflessiva":("Riflessiva/Impetuosa",    -1),
    "Prevalentemente impetuosa": ("Riflessiva/Impetuosa",     1),
    "Estremamente impetuosa":    ("Riflessiva/Impetuosa",     2),

    "Estremamente notturna":     ("Notturna/Solare",         -2),
    "Prevalentemente notturna":  ("Notturna/Solare",         -1),
    "Prevalentemente solare":    ("Notturna/Solare",          1),
    "Estremamente solare":       ("Notturna/Solare",          2),

    "Estremamente statica":      ("Statica/Dinamica",        -2),
    "Prevalentemente statica":   ("Statica/Dinamica",        -1),
    "Prevalentemente dinamica":  ("Statica/Dinamica",         1),
    "Estremamente dinamica":     ("Statica/Dinamica",         2),

    "Estremamente fredda":       ("Fredda/Calda",            -2),
    "Prevalentemente fredda":    ("Fredda/Calda",            -1),
    "Prevalentemente calda":     ("Fredda/Calda",             1),
    "Estremamente calda":        ("Fredda/Calda",             2),

    "Estremamente frammentata":  ("Frammentata/Compatta",    -2),
    "Prevalentemente frammentata":("Frammentata/Compatta",   -1),
    "Prevalentemente compatta":  ("Frammentata/Compatta",     1),
    "Estremamente compatta":     ("Frammentata/Compatta",     2),

    "Estremamente noir":         ("Noir/Musical",            -2),
    "Prevalentemente noir":      ("Noir/Musical",            -1),
    "Prevalentemente musical":   ("Noir/Musical",             1),
    "Estremamente musical":      ("Noir/Musical",             2),

    "Estremamente realistico":   ("Realistico/Fantastico",   -2),
    "Prevalentemente realistico":("Realistico/Fantastico",   -1),
    "Prevalentemente fantastico":("Realistico/Fantastico",    1),
    "Estremamente fantastico":   ("Realistico/Fantastico",    2),
}

DIMENSION_LABELS = {
    "Ruvido/Liscio":           ("Ruvida", "Liscia"),
    "Tagliente/Morbido":       ("Tagliente", "Morbida"),
    "Pesante/Leggero":         ("Pesante", "Leggera"),
    "Opaco/Riflettente":       ("Opaca", "Riflettente"),
    "Selvaggio/Urbano":        ("Selvaggia", "Urbana"),
    "Antica/Futuristica":      ("Antica", "Futuristica"),
    "Istituzionale/Popolare":  ("Istituzionale", "Popolare"),
    "Riflessiva/Impetuosa":    ("Riflessiva", "Impetuosa"),
    "Notturna/Solare":         ("Notturna", "Solare"),
    "Statica/Dinamica":        ("Statica", "Dinamica"),
    "Fredda/Calda":            ("Fredda", "Calda"),
    "Frammentata/Compatta":    ("Frammentata", "Compatta"),
    "Noir/Musical":            ("Noir", "Musical"),
    "Realistico/Fantastico":   ("Realistica", "Fantastica"),
}

RAPPORTO_SHORT = {
    "Abitante (vivo stabilmente qui)":                      "Abitante",
    "Pendolare (lavoro/studio qui, vivo altrove)":          "Pendolare",
    "Servizi/Tempo libero (frequento la città per necessità/svago)": "Visitatore",
    "Sono andat* via (non vivo più qui, ma sono legato/a)": "Ex-residente",
}

PALETTE_DIVERGING = px.colors.diverging.RdBu
COLOR_ACCENT      = "#0f3460"
COLOR_ACCENT2     = "#e94560"
COLOR_BG          = "#fafaf8"

# ─────────────────────────────────────────────
# CARICAMENTO E PREPARAZIONE DATI
# ─────────────────────────────────────────────
@st.cache_data
def load_data(uploaded_file=None, default_path=None):
    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
    elif default_path:
        df_raw = pd.read_csv(default_path)
    else:
        return None, None

    # Rename demografiche
    df = pd.DataFrame()
    df["timestamp"]  = df_raw.iloc[:, 0]
    df["eta"]        = df_raw.iloc[:, 1]
    df["rapporto"]   = df_raw.iloc[:, 2].map(RAPPORTO_SHORT).fillna(df_raw.iloc[:, 2])

    # Mappa semantica → score numerico
    sem_cols = df_raw.columns[3:17]  # 14 colonne percezione attuale
    for col in sem_cols:
        series = df_raw[col].map(lambda v: SEMANTIC_MAP.get(v, (None, None))[1])
        dim    = df_raw[col].map(lambda v: SEMANTIC_MAP.get(v, (v, None))[0])
        # usa la dimensione dal primo valore non nullo
        dim_name = dim.dropna().iloc[0] if not dim.dropna().empty else col
        df[dim_name] = series

    # Personaggio
    df["personaggio"] = df_raw.iloc[:, 17]

    # Desiderata (3 colonne categoriali)
    df["desiderata_1"] = df_raw.iloc[:, 18]
    df["desiderata_2"] = df_raw.iloc[:, 19]
    df["desiderata_3"] = df_raw.iloc[:, 20]

    # Lista dimensioni semantiche
    dim_cols = list(DIMENSION_LABELS.keys())

    return df, dim_cols


# ─────────────────────────────────────────────
# FUNZIONI DI PLOTTING
# ─────────────────────────────────────────────

def fig_to_svg(fig):
    """Export come SVG vettoriale — nessuna dipendenza da Chrome/kaleido.
    SVG è ideale per pubblicazione accademica (vettoriale, scalabile)."""
    return fig.to_image(format="svg")

def styled_fig(fig, height=420):
    fig.update_layout(
        height=height,
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(family="Inter, sans-serif", size=12, color="#333"),
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig

# ── Semantic Profile Bar ──────────────────────
def plot_semantic_profile(df_filt, dim_cols):
    means = df_filt[dim_cols].mean()
    stds  = df_filt[dim_cols].std()

    colors = [COLOR_ACCENT2 if v < 0 else COLOR_ACCENT for v in means.values]

    # Etichette asse y: polo_neg → polo_pos
    labels = [f"{DIMENSION_LABELS[d][0]} ← → {DIMENSION_LABELS[d][1]}" for d in dim_cols]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=means.values,
        y=labels,
        orientation="h",
        marker_color=colors,
        error_x=dict(type="data", array=stds.values, color="#aaa", thickness=1.5, width=4),
        hovertemplate="<b>%{y}</b><br>Media: %{x:.2f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_width=1.5, line_dash="dot", line_color="#999")
    fig.update_layout(
        title="Profilo Semantico Attuale — Media ± Dev.Std.",
        xaxis=dict(range=[-2.5, 2.5], tickvals=[-2,-1,0,1,2],
                   ticktext=["−2","−1","0","+1","+2"], zeroline=False),
        yaxis=dict(automargin=True),
    )
    return styled_fig(fig, height=520)

# ── Heatmap Correlazione ──────────────────────
def plot_correlation_heatmap(df_filt, dim_cols, selected_dims):
    sub = df_filt[selected_dims].dropna()
    corr = sub.corr(method="pearson")

    # etichette abbreviate
    short = [d.split("/")[0] + "/" + d.split("/")[1] for d in selected_dims]

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=short, y=short,
        colorscale="RdBu",
        zmid=0, zmin=-1, zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=11),
        hovertemplate="<b>%{x} × %{y}</b><br>r = %{z:.2f}<extra></extra>",
        colorbar=dict(title="r di Pearson", tickvals=[-1,-0.5,0,0.5,1]),
    ))
    fig.update_layout(
        title="Heatmap di Correlazione (r di Pearson)",
        xaxis=dict(tickangle=-35),
    )
    return styled_fig(fig, height=500)

# ── Radar Chart ───────────────────────────────
def plot_radar(df_filt, dim_cols, group_col, groups):
    categories = dim_cols + [dim_cols[0]]  # chiude il poligono

    fig = go.Figure()
    palette = px.colors.qualitative.Set2

    for i, grp in enumerate(groups):
        sub = df_filt[df_filt[group_col] == grp][dim_cols].mean()
        vals = sub.tolist() + [sub.iloc[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=categories,
            fill="toself",
            name=grp,
            line_color=palette[i % len(palette)],
            fillcolor=palette[i % len(palette)].replace("rgb", "rgba").replace(")", ",0.15)"),
            hovertemplate="<b>" + grp + "</b><br>%{theta}: %{r:.2f}<extra></extra>",
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[-2, 2], tickvals=[-2,-1,0,1,2],
                            tickfont=dict(size=9), gridcolor="#ddd"),
            angularaxis=dict(tickfont=dict(size=10)),
            bgcolor=COLOR_BG,
        ),
        title=f"Radar Chart — Profilo identitario per {group_col}",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        showlegend=True,
    )
    return styled_fig(fig, height=520)

# ── Gap Analysis ──────────────────────────────
def plot_gap_analysis(df_filt):
    # Desiderata: frequenze aggregate sulle 3 colonne
    des_all = pd.concat([
        df_filt["desiderata_1"], df_filt["desiderata_2"], df_filt["desiderata_3"]
    ]).dropna()
    des_freq = des_all.value_counts().reset_index()
    des_freq.columns = ["Aggettivo", "Conteggio"]
    des_freq["Tipo"] = "Desiderata"
    des_freq["Percentuale"] = des_freq["Conteggio"] / des_freq["Conteggio"].sum() * 100

    # Profilo attuale — solo dimensioni con media > 0.5 o < -0.5 (polarizzate)
    means = df_filt[list(DIMENSION_LABELS.keys())].mean()
    attuale_items = []
    for dim, val in means.items():
        if abs(val) >= 0.5:
            pole = DIMENSION_LABELS[dim][1] if val > 0 else DIMENSION_LABELS[dim][0]
            attuale_items.append({"Aggettivo": pole, "Valore_medio": round(abs(val), 2), "Polo": dim})

    # --- Plot doppio ----
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Identità Percepita Attuale — Dimensioni polarizzate (|media|≥0.5)",
                        "Visione Desiderata — Aggettivi per Maddaloni di domani"),
        horizontal_spacing=0.10,
    )

    if attuale_items:
        df_att = pd.DataFrame(attuale_items).sort_values("Valore_medio", ascending=True)
        fig.add_trace(go.Bar(
            x=df_att["Valore_medio"], y=df_att["Aggettivo"],
            orientation="h",
            marker_color=COLOR_ACCENT,
            hovertemplate="<b>%{y}</b> (dim: %{customdata})<br>|Media| = %{x:.2f}<extra></extra>",
            customdata=df_att["Polo"],
            name="Attuale",
        ), row=1, col=1)

    des_top = des_freq.head(12).sort_values("Percentuale", ascending=True)
    fig.add_trace(go.Bar(
        x=des_top["Percentuale"], y=des_top["Aggettivo"],
        orientation="h",
        marker_color=COLOR_ACCENT2,
        hovertemplate="<b>%{y}</b><br>%{x:.1f}% delle scelte<extra></extra>",
        name="Desiderata",
    ), row=1, col=2)

    fig.update_xaxes(title_text="Intensità media assoluta", row=1, col=1)
    fig.update_xaxes(title_text="% scelte", row=1, col=2)
    fig.update_layout(
        title="Gap Analysis — Maddaloni oggi vs. domani",
        showlegend=False,
    )
    return styled_fig(fig, height=480)

# ── Distribuzione per Fascia d'Età ───────────
def plot_age_distribution(df_filt, dim_col):
    eta_order = ["14-18", "19-26", "27-55", "55+"]
    fig = go.Figure()
    palette = px.colors.sequential.Blues[2:]
    for i, eta in enumerate(eta_order):
        sub = df_filt[df_filt["eta"] == eta][dim_col].dropna()
        if len(sub) == 0:
            continue
        fig.add_trace(go.Box(
            y=sub, name=eta,
            boxmean="sd",
            marker_color=palette[min(i, len(palette)-1)],
            line_color=COLOR_ACCENT,
            hovertemplate=f"<b>{eta}</b><br>Valore: %{{y}}<extra></extra>",
        ))
    fig.add_hline(y=0, line_dash="dot", line_color="#aaa")
    labels = DIMENSION_LABELS.get(dim_col, ("−", "+"))
    fig.update_layout(
        title=f"Distribuzione per fascia d'età — {dim_col}",
        yaxis=dict(range=[-2.5, 2.5], tickvals=[-2,-1,0,1,2],
                   ticktext=[labels[0]+"(−2)", "−1", "0", "+1", labels[1]+"(+2)"]),
        xaxis_title="Fascia d'età",
    )
    return styled_fig(fig, height=420)

# ── Personaggio ───────────────────────────────
def plot_personaggio(df_filt):
    counts = df_filt["personaggio"].value_counts().reset_index()
    counts.columns = ["Personaggio", "N"]
    short = counts["Personaggio"].apply(lambda x: x.split("(")[0].strip())
    tooltip = counts["Personaggio"]
    fig = go.Figure(go.Bar(
        x=short, y=counts["N"],
        marker_color=[COLOR_ACCENT, COLOR_ACCENT2, "#2ecc71", "#f39c12"],
        text=counts["N"], textposition="auto",
        hovertext=tooltip, hoverinfo="text+y",
    ))
    fig.update_layout(title="Maddaloni come personaggio — distribuzione", xaxis_title="", yaxis_title="Risposte")
    return styled_fig(fig, height=360)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏛️ Maddaloni<br><span style='font-size:0.8rem;opacity:0.6'>attraverso i tuoi occhi</span>", unsafe_allow_html=True)
    st.markdown("---")

    uploaded = st.file_uploader("📂 Carica CSV del sondaggio", type=["csv"])

    st.markdown("### Filtri")
    # Filtri vuoti per ora, li popolo dopo il caricamento dati

st.markdown("""
<div class="dash-header">
  <h1>🏛️ Maddaloni attraverso i tuoi occhi</h1>
  <p>Dashboard di analisi semantica urbana · Co-progettazione dell'immaginario collettivo · 174 rispondenti · Marzo 2026</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARICAMENTO
# ─────────────────────────────────────────────
DEFAULT_CSV = "Maddaloni_attraverso_i_tuoi_occhi__Risposte__-_Risposte_del_modulo_1__2_.csv"

import os
if uploaded:
    df, dim_cols = load_data(uploaded_file=uploaded)
elif os.path.exists(DEFAULT_CSV):
    df, dim_cols = load_data(default_path=DEFAULT_CSV)
else:
    st.info("⬆️ Carica il file CSV dal pannello laterale per iniziare.")
    st.stop()

if df is None:
    st.error("Errore nel caricamento del file.")
    st.stop()

# ─────────────────────────────────────────────
# FILTRI SIDEBAR (dopo il caricamento)
# ─────────────────────────────────────────────
with st.sidebar:
    eta_opts = sorted(df["eta"].dropna().unique().tolist(), key=lambda x: ["14-18","19-26","27-55","55+"].index(x) if x in ["14-18","19-26","27-55","55+"] else 99)
    sel_eta = st.multiselect("Fascia d'età", eta_opts, default=eta_opts)

    rap_opts = sorted(df["rapporto"].dropna().unique().tolist())
    sel_rap = st.multiselect("Rapporto con la città", rap_opts, default=rap_opts)

    st.markdown("---")
    st.markdown("<small>Dashboard prodotta per ricerca scientifica.<br>Dati aggregati e anonimi.</small>", unsafe_allow_html=True)

# Applica filtri
df_f = df[df["eta"].isin(sel_eta) & df["rapporto"].isin(sel_rap)].copy()
n_filt = len(df_f)

# ─────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Rispondenti (filtro attivo)", n_filt, f"{n_filt-174} vs totale" if n_filt != 174 else "Totale")
with k2:
    st.metric("Fasce d'età selezionate", len(sel_eta))
with k3:
    st.metric("Tipi di rapporto", len(sel_rap))
with k4:
    pct_completo = round(df_f[dim_cols].notna().all(axis=1).mean() * 100, 1)
    st.metric("Risposte complete", f"{pct_completo}%")

st.markdown("---")

# ─────────────────────────────────────────────
# TAB PRINCIPALI
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Profilo Semantico",
    "🔥 Heatmap Correlazione",
    "🕸️ Radar Chart",
    "🔭 Gap Analysis",
    "🔬 Analisi per Segmento",
])

# ════════════════════════════════════════════
# TAB 1 — PROFILO SEMANTICO
# ════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Profilo Semantico Attuale</div>', unsafe_allow_html=True)
    st.caption("Ogni barra rappresenta la media del campione su quella dimensione bipolare. Errori standard inclusi. Scala: −2 (polo sinistro) → +2 (polo destro).")

    fig1 = plot_semantic_profile(df_f, dim_cols)
    st.plotly_chart(fig1, use_container_width=True)

    col_dl, _ = st.columns([1, 4])
    with col_dl:
        svg_bytes = fig_to_svg(fig1)
        st.download_button("⬇️ Esporta SVG (vettoriale)", data=svg_bytes, file_name="profilo_semantico.svg", mime="image/svg+xml")

    st.markdown("---")
    st.markdown('<div class="section-title">Statistiche Descrittive</div>', unsafe_allow_html=True)

    desc = df_f[dim_cols].describe().T[["count", "mean", "std", "min", "max"]]
    desc.columns = ["N", "Media", "Dev.Std.", "Min", "Max"]
    desc["Media"]    = desc["Media"].round(3)
    desc["Dev.Std."] = desc["Dev.Std."].round(3)

    # Aggiungi polo dominante
    def polo_dominante(row):
        dim = row.name
        if abs(row["Media"]) < 0.25: return "Neutro"
        pole_idx = 1 if row["Media"] > 0 else 0
        return DIMENSION_LABELS.get(dim, ("−", "+"))[pole_idx]

    desc["Polo dominante"] = desc.apply(polo_dominante, axis=1)
    st.dataframe(desc, use_container_width=True)

    # Personaggio
    st.markdown('<div class="section-title">Maddaloni come Personaggio</div>', unsafe_allow_html=True)
    fig_p = plot_personaggio(df_f)
    st.plotly_chart(fig_p, use_container_width=True)

# ════════════════════════════════════════════
# TAB 2 — HEATMAP CORRELAZIONE
# ════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Heatmap di Correlazione tra Dimensioni</div>', unsafe_allow_html=True)
    st.caption("Seleziona le dimensioni da mettere in relazione. La scala cromatica va da −1 (correlazione inversa, rosso) a +1 (correlazione diretta, blu).")

    selected_dims = st.multiselect(
        "Seleziona dimensioni da correlare",
        options=dim_cols,
        default=dim_cols,
        key="corr_dims",
    )

    if len(selected_dims) < 2:
        st.warning("Seleziona almeno 2 dimensioni.")
    else:
        fig2 = plot_correlation_heatmap(df_f, dim_cols, selected_dims)
        st.plotly_chart(fig2, use_container_width=True)

        col_dl2, _ = st.columns([1, 4])
        with col_dl2:
            svg_bytes2 = fig_to_svg(fig2)
            st.download_button("⬇️ Esporta SVG (vettoriale)", data=svg_bytes2, file_name="heatmap_correlazione.svg", mime="image/svg+xml")

        # Top correlazioni
        st.markdown('<div class="section-title">Correlazioni più significative</div>', unsafe_allow_html=True)
        sub = df_f[selected_dims].dropna()
        corr_m = sub.corr()
        pairs = []
        for i, a in enumerate(selected_dims):
            for j, b in enumerate(selected_dims):
                if j > i:
                    r, p = stats.pearsonr(sub[a], sub[b])
                    pairs.append({"Dimensione A": a, "Dimensione B": b,
                                  "r": round(r, 3), "p-value": round(p, 4)})
        df_pairs = pd.DataFrame(pairs).sort_values("r", key=abs, ascending=False).head(10)
        df_pairs["Significativo (p<0.05)"] = df_pairs["p-value"] < 0.05
        st.dataframe(df_pairs, use_container_width=True)

# ════════════════════════════════════════════
# TAB 3 — RADAR CHART
# ════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Radar Chart — Profilo Identitario per Segmento</div>', unsafe_allow_html=True)
    st.caption("Confronta i profili semantici medi tra diverse categorie di rispondenti. Scala radiale: −2 (polo negativo) → +2 (polo positivo).")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        group_col = st.selectbox("Raggruppa per", ["eta", "rapporto"], format_func=lambda x: "Fascia d'età" if x == "eta" else "Rapporto con la città")
    with col_r2:
        avail_groups = sorted(df_f[group_col].dropna().unique().tolist())
        sel_groups = st.multiselect("Gruppi da visualizzare", avail_groups, default=avail_groups[:min(4, len(avail_groups))])

    if not sel_groups:
        st.warning("Seleziona almeno un gruppo.")
    else:
        fig3 = plot_radar(df_f, dim_cols, group_col, sel_groups)
        st.plotly_chart(fig3, use_container_width=True)

        col_dl3, _ = st.columns([1, 4])
        with col_dl3:
            svg_bytes3 = fig_to_svg(fig3)
            st.download_button("⬇️ Esporta SVG (vettoriale)", data=svg_bytes3, file_name="radar_chart.svg", mime="image/svg+xml")

# ════════════════════════════════════════════
# TAB 4 — GAP ANALYSIS
# ════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Gap Analysis — Maddaloni oggi vs. Maddaloni di domani</div>', unsafe_allow_html=True)
    st.caption("Confronto tra le dimensioni percepite come più polarizzate nel presente e gli aggettivi scelti per la città desiderata.")

    fig4 = plot_gap_analysis(df_f)
    st.plotly_chart(fig4, use_container_width=True)

    col_dl4, _ = st.columns([1, 4])
    with col_dl4:
        svg_bytes4 = fig_to_svg(fig4)
        st.download_button("⬇️ Esporta SVG (vettoriale)", data=svg_bytes4, file_name="gap_analysis.svg", mime="image/svg+xml")

    # Tabella desiderata
    st.markdown('<div class="section-title">Frequenze degli Aggettivi Desiderati</div>', unsafe_allow_html=True)
    col_g1, col_g2, col_g3 = st.columns(3)
    for i, (col_name, col_g) in enumerate(zip(["desiderata_1", "desiderata_2", "desiderata_3"],
                                               [col_g1, col_g2, col_g3])):
        with col_g:
            vc = df_f[col_name].value_counts().reset_index()
            vc.columns = ["Aggettivo", "N"]
            vc["% sul filtro"] = (vc["N"] / n_filt * 100).round(1).astype(str) + "%"
            st.caption(f"Set {i+1}")
            st.dataframe(vc, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════
# TAB 5 — ANALISI PER SEGMENTO
# ════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">Analisi per Segmento — Distribuzione Boxplot</div>', unsafe_allow_html=True)
    st.caption("Seleziona una dimensione per vedere come si distribuisce nelle diverse fasce d'età. I box mostrano mediana, IQR e deviazione standard.")

    dim_sel_box = st.selectbox("Dimensione da analizzare", dim_cols, key="box_dim")
    fig5 = plot_age_distribution(df_f, dim_sel_box)
    st.plotly_chart(fig5, use_container_width=True)

    col_dl5, _ = st.columns([1, 4])
    with col_dl5:
        svg_bytes5 = fig_to_svg(fig5)
        st.download_button("⬇️ Esporta SVG (vettoriale)", data=svg_bytes5, file_name=f"distribuzione_{dim_sel_box.replace('/','_')}.svg", mime="image/svg+xml")

    # ANOVA semplice
    st.markdown('<div class="section-title">Test ANOVA — differenze tra fasce d\'età</div>', unsafe_allow_html=True)
    st.caption("Verifica se le medie per fascia d'età differiscono statisticamente (p < 0.05 → differenza significativa).")
    anova_rows = []
    for d in dim_cols:
        groups_data = [df_f[df_f["eta"] == e][d].dropna().values for e in ["14-18","19-26","27-55","55+"]]
        groups_data = [g for g in groups_data if len(g) > 1]
        if len(groups_data) >= 2:
            try:
                f, p = stats.f_oneway(*groups_data)
                anova_rows.append({"Dimensione": d, "F": round(f, 3), "p-value": round(p, 4), "Significativo": "✅" if p < 0.05 else "—"})
            except Exception:
                pass
    if anova_rows:
        df_anova = pd.DataFrame(anova_rows).sort_values("p-value")
        st.dataframe(df_anova, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small style='color:#aaa;'>Dashboard sviluppata per il progetto di co-progettazione dell'immaginario urbano · "
    "Dati raccolti marzo 2026 · Tutti i dati sono aggregati e anonimi · "
    "Metodologia: Differenziale Semantico (Osgood, 1957)</small>",
    unsafe_allow_html=True
)
