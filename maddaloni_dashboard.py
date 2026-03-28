"""
Dashboard: "Maddaloni attraverso i tuoi occhi"
Analisi di co-progettazione dell'immaginario urbano — v2.0
Accessibilità: WCAG 2.1 AA | W3C guidelines
Requisiti: pip install streamlit plotly pandas scipy numpy
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats

# ─────────────────────────────────────────────
# PAGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Maddaloni attraverso i tuoi occhi",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# DESIGN SYSTEM — WCAG 2.1 AA
# Regole applicate:
#  • Testo principale #1a1a1a su bianco: 16.7:1 ✓
#  • Testo secondario #595959 su bianco: 7.0:1 ✓
#  • Accento primario #1d5fa6 su bianco: 4.7:1 ✓
#  • Accento negativo #b94a00 su bianco: 4.6:1 ✓
#  • Nessun testo su sfondo colorato senza verifica contrasto
#  • Focus visibile su tutti i controlli
#  • Colore non è l'unico mezzo per trasmettere informazione
# ─────────────────────────────────────────────
C_BG       = "#ffffff"
C_SURFACE  = "#f5f6f8"
C_BORDER   = "#d0d4da"
C_TEXT     = "#1a1a1a"
C_TEXT_SEC = "#595959"
C_PRIMARY  = "#1d5fa6"
C_NEGATIVE = "#b94a00"
C_ZERO     = "#767676"
C_GRID     = "#e4e6ea"

CAT_PALETTE = ["#1d5fa6", "#b94a00", "#1a7a4a", "#7b3fa0",
               "#8a6200", "#1a6d7a", "#a02060", "#4a4a4a"]

st.markdown(f"""
<style>
  html, body, [class*="css"] {{
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    font-size: 16px; color: {C_TEXT}; background: {C_BG};
  }}
  .block-container {{ padding: 1.5rem 2rem 3rem; max-width: 1280px; }}

  .dash-header {{
    background: #1a2e4a; color: #ffffff;
    padding: 1.75rem 2rem; border-radius: 6px;
    margin-bottom: 1.5rem; border-left: 5px solid {C_PRIMARY};
  }}
  .dash-header h1 {{
    font-size: 1.6rem; font-weight: 700; margin: 0 0 0.3rem;
    color: #ffffff; letter-spacing: -0.01em;
  }}
  .dash-header p {{ font-size: 0.9rem; margin: 0; color: #c8d4e3; }}

  .section-title {{
    font-size: 1.1rem; font-weight: 600; color: {C_TEXT};
    border-bottom: 2px solid {C_BORDER};
    padding-bottom: 0.4rem; margin: 1.8rem 0 0.8rem;
  }}
  .method-note {{
    font-size: 0.85rem; color: {C_TEXT_SEC};
    background: {C_SURFACE}; border-left: 3px solid {C_BORDER};
    padding: 0.5rem 0.8rem; border-radius: 0 4px 4px 0; margin-bottom: 1rem;
  }}

  [data-testid="stSidebar"] {{
    background: {C_SURFACE}; border-right: 1px solid {C_BORDER};
  }}
  [data-testid="stSidebar"] label {{
    font-size: 0.85rem; font-weight: 600; color: {C_TEXT};
    text-transform: uppercase; letter-spacing: 0.05em;
  }}

  .stTabs [data-baseweb="tab-list"] {{ border-bottom: 2px solid {C_BORDER}; gap: 0; }}
  .stTabs [data-baseweb="tab"] {{
    font-size: 0.9rem; font-weight: 500; color: {C_TEXT_SEC};
    padding: 0.5rem 1rem; border-radius: 4px 4px 0 0;
    background: transparent; border: none;
  }}
  .stTabs [aria-selected="true"] {{
    color: {C_PRIMARY} !important; font-weight: 700;
    border-bottom: 3px solid {C_PRIMARY} !important;
    background: transparent !important;
  }}

  *:focus-visible {{ outline: 3px solid {C_PRIMARY}; outline-offset: 2px; }}

  div[data-testid="metric-container"] {{
    background: {C_SURFACE}; border-radius: 6px;
    border: 1px solid {C_BORDER}; padding: 0.75rem 1rem;
  }}
  .footer {{
    font-size: 0.8rem; color: {C_TEXT_SEC};
    border-top: 1px solid {C_BORDER}; padding-top: 1rem; margin-top: 2rem;
  }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# COSTANTI DOMINIO
# ─────────────────────────────────────────────
SEMANTIC_MAP = {
    "Estremamente ruvido":          ("Ruvido/Liscio",            -2),
    "Prevalentemente ruvido":       ("Ruvido/Liscio",            -1),
    "Prevalentemente liscio":       ("Ruvido/Liscio",             1),
    "Estremamente liscio":          ("Ruvido/Liscio",             2),
    "Estremamente tagliente":       ("Tagliente/Morbido",        -2),
    "Prevalentemente tagliente":    ("Tagliente/Morbido",        -1),
    "Prevalentemente morbido":      ("Tagliente/Morbido",         1),
    "Estremamente morbido":         ("Tagliente/Morbido",         2),
    "Estremamente pesante":         ("Pesante/Leggero",          -2),
    "Prevalentemente pesante":      ("Pesante/Leggero",          -1),
    "Prevalentemente leggero":      ("Pesante/Leggero",           1),
    "Estremamente leggero":         ("Pesante/Leggero",           2),
    "Estremamente opaco":           ("Opaco/Riflettente",        -2),
    "Prevalentemente opaco":        ("Opaco/Riflettente",        -1),
    "Prevalentemente riflettente":  ("Opaco/Riflettente",         1),
    "Estremamente riflettente":     ("Opaco/Riflettente",         2),
    "Estremamente selvaggio":       ("Selvaggio/Urbano",         -2),
    "Prevalentemente selvaggio":    ("Selvaggio/Urbano",         -1),
    "Prevalentemente urbano":       ("Selvaggio/Urbano",          1),
    "Estremamente urbano":          ("Selvaggio/Urbano",          2),
    "Estremamente antica":          ("Antica/Futuristica",       -2),
    "Prevalentemente antica":       ("Antica/Futuristica",       -1),
    "Prevalentemente futuristica":  ("Antica/Futuristica",        1),
    "Estremamente futuristica":     ("Antica/Futuristica",        2),
    "Estremamente istituzionale":   ("Istituzionale/Popolare",   -2),
    "Prevalentemente istituzionale":("Istituzionale/Popolare",   -1),
    "Prevalentemente popolare":     ("Istituzionale/Popolare",    1),
    "Estremamente popolare":        ("Istituzionale/Popolare",    2),
    "Estremamente riflessiva":      ("Riflessiva/Impetuosa",     -2),
    "Prevalentemente riflessiva":   ("Riflessiva/Impetuosa",     -1),
    "Prevalentemente impetuosa":    ("Riflessiva/Impetuosa",      1),
    "Estremamente impetuosa":       ("Riflessiva/Impetuosa",      2),
    "Estremamente notturna":        ("Notturna/Solare",          -2),
    "Prevalentemente notturna":     ("Notturna/Solare",          -1),
    "Prevalentemente solare":       ("Notturna/Solare",           1),
    "Estremamente solare":          ("Notturna/Solare",           2),
    "Estremamente statica":         ("Statica/Dinamica",         -2),
    "Prevalentemente statica":      ("Statica/Dinamica",         -1),
    "Prevalentemente dinamica":     ("Statica/Dinamica",          1),
    "Estremamente dinamica":        ("Statica/Dinamica",          2),
    "Estremamente fredda":          ("Fredda/Calda",             -2),
    "Prevalentemente fredda":       ("Fredda/Calda",             -1),
    "Prevalentemente calda":        ("Fredda/Calda",              1),
    "Estremamente calda":           ("Fredda/Calda",              2),
    "Estremamente frammentata":     ("Frammentata/Compatta",     -2),
    "Prevalentemente frammentata":  ("Frammentata/Compatta",     -1),
    "Prevalentemente compatta":     ("Frammentata/Compatta",      1),
    "Estremamente compatta":        ("Frammentata/Compatta",      2),
    "Estremamente noir":            ("Noir/Musical",             -2),
    "Prevalentemente noir":         ("Noir/Musical",             -1),
    "Prevalentemente musical":      ("Noir/Musical",              1),
    "Estremamente musical":         ("Noir/Musical",              2),
    "Estremamente realistico":      ("Realistico/Fantastico",    -2),
    "Prevalentemente realistico":   ("Realistico/Fantastico",    -1),
    "Prevalentemente fantastico":   ("Realistico/Fantastico",     1),
    "Estremamente fantastico":      ("Realistico/Fantastico",     2),
}

DIMENSION_LABELS = {
    "Ruvido/Liscio":          ("Ruvida",        "Liscia"),
    "Tagliente/Morbido":      ("Tagliente",     "Morbida"),
    "Pesante/Leggero":        ("Pesante",       "Leggera"),
    "Opaco/Riflettente":      ("Opaca",         "Riflettente"),
    "Selvaggio/Urbano":       ("Selvaggia",     "Urbana"),
    "Antica/Futuristica":     ("Antica",        "Futuristica"),
    "Istituzionale/Popolare": ("Istituzionale", "Popolare"),
    "Riflessiva/Impetuosa":   ("Riflessiva",    "Impetuosa"),
    "Notturna/Solare":        ("Notturna",      "Solare"),
    "Statica/Dinamica":       ("Statica",       "Dinamica"),
    "Fredda/Calda":           ("Fredda",        "Calda"),
    "Frammentata/Compatta":   ("Frammentata",   "Compatta"),
    "Noir/Musical":           ("Noir",          "Musical"),
    "Realistico/Fantastico":  ("Realistica",    "Fantastica"),
}

RAPPORTO_SHORT = {
    "Abitante (vivo stabilmente qui)":                               "Abitante",
    "Pendolare (lavoro/studio qui, vivo altrove)":                   "Pendolare",
    "Servizi/Tempo libero (frequento la città per necessità/svago)": "Visitatore",
    "Sono andat* via (non vivo più qui, ma sono legato/a)":          "Ex-residente",
}

ETA_ORDER = ["14-18", "19-26", "27-55", "55+"]

# ─────────────────────────────────────────────
# CARICAMENTO DATI
# ─────────────────────────────────────────────
@st.cache_data
def load_data(uploaded_file=None, default_path=None):
    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
    elif default_path:
        df_raw = pd.read_csv(default_path)
    else:
        return None, None

    df = pd.DataFrame()
    df["timestamp"] = df_raw.iloc[:, 0]
    df["eta"]       = df_raw.iloc[:, 1]
    df["rapporto"]  = df_raw.iloc[:, 2].map(RAPPORTO_SHORT).fillna(df_raw.iloc[:, 2])

    for col in df_raw.columns[3:17]:
        scores   = df_raw[col].map(lambda v: SEMANTIC_MAP.get(v, (None, None))[1])
        dim_name = df_raw[col].map(lambda v: SEMANTIC_MAP.get(v, (v, None))[0]).dropna()
        name     = dim_name.iloc[0] if not dim_name.empty else col
        df[name] = scores

    df["personaggio"]  = df_raw.iloc[:, 17]
    df["desiderata_1"] = df_raw.iloc[:, 18]
    df["desiderata_2"] = df_raw.iloc[:, 19]
    df["desiderata_3"] = df_raw.iloc[:, 20]

    return df, list(DIMENSION_LABELS.keys())

# ─────────────────────────────────────────────
# HELPER LAYOUT GRAFICI
# ─────────────────────────────────────────────
def base_layout(fig, height=440, title=""):
    fig.update_layout(
        height=height,
        title=dict(text=title, font=dict(size=14, color=C_TEXT), x=0, xanchor="left"),
        paper_bgcolor=C_BG, plot_bgcolor=C_BG,
        font=dict(family="system-ui, -apple-system, sans-serif", size=13, color=C_TEXT),
        margin=dict(l=16, r=24, t=48, b=16),
        xaxis=dict(gridcolor=C_GRID, linecolor=C_BORDER,
                   tickcolor=C_BORDER, zerolinecolor=C_BORDER),
        yaxis=dict(gridcolor=C_GRID, linecolor=C_BORDER,
                   tickcolor=C_BORDER, zerolinecolor=C_BORDER),
        legend=dict(bgcolor=C_SURFACE, bordercolor=C_BORDER, borderwidth=1,
                    font=dict(size=12, color=C_TEXT)),
    )
    return fig

def note(testo):
    st.markdown(f'<div class="method-note">{testo}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GRAFICI
# ─────────────────────────────────────────────

def plot_semantic_profile(df_f, dim_cols):
    """
    Differenziale semantico orizzontale.
    Barra + whiskers ±1 SD. Testo esplicito del polo dominante.
    Non si affida solo al colore: segno e label sempre visibili.
    """
    means = df_f[dim_cols].mean()
    stds  = df_f[dim_cols].std()

    rows = []
    for dim in dim_cols:
        m  = means[dim]
        sd = stds[dim]
        neg_l, pos_l = DIMENSION_LABELS[dim]
        pole = pos_l if m >= 0 else neg_l
        rows.append({
            "mean":    m,
            "sd":      sd,
            "color":   C_PRIMARY if m >= 0 else C_NEGATIVE,
            "label_y": f"{neg_l}  ←  {pos_l}",
            "polo":    f"{'+'  if m>=0 else '−'}{abs(m):.2f}  {pole}",
        })

    df_p = pd.DataFrame(rows).sort_values("mean")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_p["mean"],
        y=df_p["label_y"],
        orientation="h",
        marker_color=df_p["color"],
        error_x=dict(type="data", array=df_p["sd"],
                     color=C_ZERO, thickness=1.5, width=5),
        text=df_p["polo"],
        textposition="outside",
        textfont=dict(size=11, color=C_TEXT_SEC),
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Media: %{x:.2f}<br>SD: %{error_x.array:.2f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_width=1.5, line_color=C_ZERO)
    fig.add_annotation(x=-2.4, y=1.02, xref="x", yref="paper",
                       text="← polo negativo", showarrow=False,
                       font=dict(size=11, color=C_NEGATIVE), xanchor="left")
    fig.add_annotation(x=2.4, y=1.02, xref="x", yref="paper",
                       text="polo positivo →", showarrow=False,
                       font=dict(size=11, color=C_PRIMARY), xanchor="right")
    fig.update_layout(
        xaxis=dict(range=[-2.9, 2.9], tickvals=[-2,-1,0,1,2],
                   ticktext=["−2","−1","0","+1","+2"],
                   zeroline=False, showgrid=True, gridcolor=C_GRID),
        yaxis=dict(automargin=True, tickfont=dict(size=12)),
        bargap=0.35,
    )
    return base_layout(fig, height=560,
                       title="Differenziale Semantico — Media ± Dev.Std.")


def plot_distribution_strip(df_f, dim_col):
    """
    Distribuzione completa delle risposte per fascia d'età.
    Strip plot (punti jitterati) + box con mediana.
    Rende visibile l'eterogeneità reale, non solo la media.
    """
    neg_l, pos_l = DIMENSION_LABELS.get(dim_col, ("−", "+"))
    fig = go.Figure()

    for i, eta in enumerate(ETA_ORDER):
        sub = df_f[df_f["eta"] == eta][dim_col].dropna()
        if len(sub) == 0:
            continue
        col = CAT_PALETTE[i]
        fig.add_trace(go.Box(
            y=sub, x=[eta] * len(sub),
            name=eta,
            boxpoints="all",
            jitter=0.35,
            pointpos=0,
            marker=dict(color=col, size=5, opacity=0.55,
                        line=dict(color=C_BG, width=0.5)),
            line=dict(color=col, width=1.5),
            fillcolor="rgba(0,0,0,0)",
            whiskerwidth=0.5,
            showlegend=False,
            hovertemplate=f"<b>{eta}</b><br>Valore: %{{y}}<extra></extra>",
        ))

    fig.add_hline(y=0, line_dash="dot", line_color=C_ZERO, line_width=1.5)
    tick_labels = {
        -2: f"−2  ({neg_l})", -1: "−1",
         0: "0  (neutro)",    1: "+1",
         2: f"+2  ({pos_l})",
    }
    fig.update_layout(
        xaxis_title="Fascia d'età",
        yaxis=dict(range=[-2.6, 2.6],
                   tickvals=list(tick_labels.keys()),
                   ticktext=list(tick_labels.values()),
                   gridcolor=C_GRID),
        boxmode="group",
    )
    return base_layout(fig, height=440,
                       title=f"Distribuzione risposte — {dim_col}")


def plot_correlation_heatmap(df_f, dim_cols, selected_dims):
    """
    Heatmap Pearson. Scala: arancio (negativo) → bianco (0) → blu (positivo).
    Valori numerici sempre visibili nelle celle.
    """
    sub  = df_f[selected_dims].dropna()
    corr = sub.corr(method="pearson").round(2)
    z    = corr.values.copy().astype(float)
    np.fill_diagonal(z, np.nan)

    colorscale = [[0.0, C_NEGATIVE], [0.5, "#ffffff"], [1.0, C_PRIMARY]]

    fig = go.Figure(go.Heatmap(
        z=z, x=selected_dims, y=selected_dims,
        colorscale=colorscale, zmid=0, zmin=-1, zmax=1,
        text=corr.values,
        texttemplate="%{text:.2f}",
        textfont=dict(size=11, color=C_TEXT),
        hovertemplate="<b>%{x}</b> × <b>%{y}</b><br>r = %{z:.2f}<extra></extra>",
        colorbar=dict(
            title=dict(text="r Pearson", font=dict(size=12, color=C_TEXT)),
            tickvals=[-1, -0.5, 0, 0.5, 1],
            tickfont=dict(size=11, color=C_TEXT),
            outlinewidth=1, outlinecolor=C_BORDER,
        ),
    ))
    fig.update_layout(
        xaxis=dict(tickangle=-40, tickfont=dict(size=11), side="bottom"),
        yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
    )
    return base_layout(fig, height=520,
                       title="Correlazioni tra dimensioni (r di Pearson)")


def plot_radar(df_f, dim_cols, group_col, groups):
    """
    Radar chart. Ogni gruppo: colore + stile linea diverso.
    Distinguibile anche in scala di grigi.
    """
    categories = dim_cols + [dim_cols[0]]
    dashes = ["solid", "dash", "dot", "dashdot"]
    fig = go.Figure()

    for i, grp in enumerate(groups):
        sub  = df_f[df_f[group_col] == grp][dim_cols].mean()
        vals = sub.tolist() + [sub.iloc[0]]
        col  = CAT_PALETTE[i % len(CAT_PALETTE)]

        # fillcolor: converte hex in rgba
        r = int(col[1:3], 16)
        g = int(col[3:5], 16)
        b = int(col[5:7], 16)

        fig.add_trace(go.Scatterpolar(
            r=vals, theta=categories,
            fill="toself", name=grp,
            line=dict(color=col, width=2, dash=dashes[i % len(dashes)]),
            fillcolor=f"rgba({r},{g},{b},0.08)",
            marker=dict(size=5, color=col),
            hovertemplate=f"<b>{grp}</b><br>%{{theta}}: %{{r:.2f}}<extra></extra>",
        ))

    label = "fascia d'età" if group_col == "eta" else "rapporto con la città"
    fig.update_layout(
        polar=dict(
            bgcolor=C_BG,
            radialaxis=dict(
                visible=True, range=[-2, 2],
                tickvals=[-2, -1, 0, 1, 2],
                ticktext=["−2", "−1", "0", "+1", "+2"],
                tickfont=dict(size=10, color=C_TEXT_SEC),
                gridcolor=C_GRID, linecolor=C_BORDER,
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color=C_TEXT),
                linecolor=C_BORDER, gridcolor=C_GRID,
            ),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.22,
            xanchor="center", x=0.5,
            font=dict(size=12, color=C_TEXT),
        ),
    )
    return base_layout(fig, height=540,
                       title=f"Profilo identitario per {label}")


def plot_gap(df_f):
    """
    Gap Analysis: poli dominanti oggi vs aggettivi desiderati.
    Due grafici affiancati con valori sempre espliciti.
    """
    des_all  = pd.concat([df_f["desiderata_1"], df_f["desiderata_2"],
                          df_f["desiderata_3"]]).dropna()
    des_freq = (des_all.value_counts(normalize=True)
                .mul(100).round(1).reset_index())
    des_freq.columns = ["Aggettivo", "Pct"]

    means = df_f[list(DIMENSION_LABELS.keys())].mean()
    att = []
    for dim, val in means.items():
        if abs(val) >= 0.5:
            pole = DIMENSION_LABELS[dim][1] if val >= 0 else DIMENSION_LABELS[dim][0]
            att.append({"Polo": pole, "Int": round(abs(val), 2),
                        "Dim": dim, "Dir": "pos" if val >= 0 else "neg"})
    df_att = (pd.DataFrame(att).sort_values("Int", ascending=True)
              if att else pd.DataFrame())

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            "Oggi — poli dominanti (|media| ≥ 0.5)",
            "Domani — aggettivi desiderati",
        ],
        horizontal_spacing=0.14,
    )

    if not df_att.empty:
        colors_att = [C_PRIMARY if d == "pos" else C_NEGATIVE
                      for d in df_att["Dir"]]
        fig.add_trace(go.Bar(
            x=df_att["Int"], y=df_att["Polo"],
            orientation="h", marker_color=colors_att,
            text=[f"{v:.2f}" for v in df_att["Int"]],
            textposition="outside",
            textfont=dict(size=11, color=C_TEXT),
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Intensità: %{x:.2f} (%{customdata})<extra></extra>",
            customdata=df_att["Dim"],
        ), row=1, col=1)
        fig.update_xaxes(range=[0, 2.5],
                         title_text="Intensità media |scala −2…+2|", row=1, col=1)

    des_top = des_freq.head(10).sort_values("Pct", ascending=True)
    fig.add_trace(go.Bar(
        x=des_top["Pct"], y=des_top["Aggettivo"],
        orientation="h", marker_color=C_PRIMARY,
        text=[f"{v:.1f}%" for v in des_top["Pct"]],
        textposition="outside",
        textfont=dict(size=11, color=C_TEXT),
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>%{x:.1f}% delle scelte<extra></extra>",
    ), row=1, col=2)
    fig.update_xaxes(title_text="% scelte (tutte e 3 le risposte)", row=1, col=2)

    fig.update_layout(
        showlegend=False,
        paper_bgcolor=C_BG, plot_bgcolor=C_BG,
        font=dict(family="system-ui, sans-serif", size=13, color=C_TEXT),
        margin=dict(l=16, r=24, t=56, b=16),
        height=460,
        title=dict(text="Gap Analysis — Oggi vs. Domani",
                   font=dict(size=14, color=C_TEXT), x=0),
    )
    fig.update_yaxes(tickfont=dict(size=12), automargin=True)
    return fig


def plot_personaggio(df_f):
    counts = df_f["personaggio"].value_counts().reset_index()
    counts.columns = ["Personaggio", "N"]
    counts["Label"]   = counts["Personaggio"].str.split("(").str[0].str.strip()
    counts["Tooltip"] = counts["Personaggio"]
    counts = counts.sort_values("N", ascending=False)
    fig = go.Figure(go.Bar(
        x=counts["Label"], y=counts["N"],
        marker_color=CAT_PALETTE[:len(counts)],
        text=counts["N"], textposition="outside",
        textfont=dict(size=12, color=C_TEXT),
        cliponaxis=False,
        hovertext=counts["Tooltip"], hoverinfo="text+y",
    ))
    fig.update_layout(
        xaxis=dict(tickangle=0, tickfont=dict(size=12)),
        yaxis=dict(title="Rispondenti", gridcolor=C_GRID),
        bargap=0.4,
    )
    return base_layout(fig, height=360,
                       title="Maddaloni come personaggio — distribuzione")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏛️ Maddaloni")
    st.caption("attraverso i tuoi occhi")
    st.markdown("---")
    uploaded = st.file_uploader("Carica CSV del sondaggio", type=["csv"])
    st.markdown("---")
    st.markdown("**Filtri campione**")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="dash-header" role="banner">
  <h1>Maddaloni attraverso i tuoi occhi</h1>
  <p>Dashboard di analisi semantica urbana · Co-progettazione dell'immaginario collettivo · 174 rispondenti · Marzo 2026</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARICAMENTO
# ─────────────────────────────────────────────
DEFAULT_CSV = "Maddaloni_attraverso_i_tuoi_occhi__Risposte__-_Risposte_del_modulo_1__2_.csv"

if uploaded:
    df, dim_cols = load_data(uploaded_file=uploaded)
elif os.path.exists(DEFAULT_CSV):
    df, dim_cols = load_data(default_path=DEFAULT_CSV)
else:
    st.info("Carica il file CSV dal pannello laterale per iniziare.")
    st.stop()

if df is None:
    st.error("Errore nel caricamento del file.")
    st.stop()

# ─────────────────────────────────────────────
# FILTRI
# ─────────────────────────────────────────────
with st.sidebar:
    eta_opts = [e for e in ETA_ORDER if e in df["eta"].dropna().unique()]
    sel_eta  = st.multiselect("Fascia d'età", eta_opts, default=eta_opts)
    rap_opts = sorted(df["rapporto"].dropna().unique().tolist())
    sel_rap  = st.multiselect("Rapporto con la città", rap_opts, default=rap_opts)
    st.markdown("---")
    st.caption("Dati aggregati e anonimi.\nMetodologia: Differenziale Semantico (Osgood, 1957).")

df_f   = df[df["eta"].isin(sel_eta) & df["rapporto"].isin(sel_rap)].copy()
n_filt = len(df_f)

# ─────────────────────────────────────────────
# KPI STRIP
# ─────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Rispondenti nel filtro", n_filt,
              delta=f"{n_filt - 174} vs totale" if n_filt != 174 else None)
with k2:
    st.metric("Fasce d'età", len(sel_eta))
with k3:
    st.metric("Tipi di rapporto", len(sel_rap))
with k4:
    pct_ok = round(df_f[dim_cols].notna().all(axis=1).mean() * 100, 1)
    st.metric("Risposte complete", f"{pct_ok}%")

st.markdown("---")

# ─────────────────────────────────────────────
# TAB
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Profilo semantico",
    "Distribuzione per età",
    "Correlazioni",
    "Radar — segmenti",
    "Gap oggi / domani",
])

# ══════════════════════════════════════════════
# TAB 1 — PROFILO SEMANTICO
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Differenziale Semantico</div>', unsafe_allow_html=True)
    note(
        "Ogni riga è una dimensione bipolare (polo negativo ← → polo positivo). "
        "La barra mostra la media; i whiskers indicano ±1 deviazione standard. "
        "Il testo accanto riporta valore numerico e polo dominante. "
        "Scala: −2 = estremo negativo · 0 = neutro · +2 = estremo positivo."
    )
    st.plotly_chart(plot_semantic_profile(df_f, dim_cols), use_container_width=True)

    st.markdown('<div class="section-title">Statistiche descrittive</div>', unsafe_allow_html=True)
    desc = df_f[dim_cols].describe().T[["count","mean","std","min","max"]].round(3)
    desc.columns = ["N", "Media", "Dev.Std.", "Min", "Max"]
    desc["Polo dominante"] = desc.apply(
        lambda r: ("Neutro" if abs(r["Media"]) < 0.25
                   else DIMENSION_LABELS.get(r.name, ("−","+"))[1 if r["Media"] > 0 else 0]),
        axis=1,
    )
    st.dataframe(desc, use_container_width=True)

    st.markdown('<div class="section-title">Maddaloni come personaggio</div>', unsafe_allow_html=True)
    note("Ogni rispondente ha scelto il personaggio che meglio incarna lo spirito della città. "
         "Passa il cursore sulle barre per la descrizione completa.")
    st.plotly_chart(plot_personaggio(df_f), use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — DISTRIBUZIONE PER ETÀ
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Distribuzione risposte per fascia d\'età</div>',
                unsafe_allow_html=True)
    note(
        "Seleziona una dimensione per vedere come si distribuiscono le risposte. "
        "Il box mostra mediana e IQR; ogni punto è una risposta individuale. "
        "La linea tratteggiata indica il punto neutro della scala (0)."
    )
    dim_sel = st.selectbox("Dimensione da esplorare", dim_cols, key="box_dim")
    st.plotly_chart(plot_distribution_strip(df_f, dim_sel), use_container_width=True)

    with st.expander("Test ANOVA — differenze statistiche tra fasce d'età"):
        note("p < 0.05: le medie tra fasce d'età differiscono in modo statisticamente significativo.")
        rows_anova = []
        for d in dim_cols:
            gd = [df_f[df_f["eta"] == e][d].dropna().values for e in ETA_ORDER]
            gd = [g for g in gd if len(g) > 1]
            if len(gd) >= 2:
                try:
                    f_v, p_v = stats.f_oneway(*gd)
                    rows_anova.append({
                        "Dimensione": d, "F": round(f_v, 3),
                        "p-value": round(p_v, 4),
                        "Significativo (p<0.05)": "Sì" if p_v < 0.05 else "No",
                    })
                except Exception:
                    pass
        if rows_anova:
            st.dataframe(
                pd.DataFrame(rows_anova).sort_values("p-value"),
                use_container_width=True, hide_index=True,
            )

# ══════════════════════════════════════════════
# TAB 3 — CORRELAZIONI
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Correlazioni tra dimensioni</div>', unsafe_allow_html=True)
    note(
        "Blu: le due dimensioni tendono a muoversi nella stessa direzione. "
        "Arancio: tendenza opposta. Bianco: nessuna relazione lineare. "
        "Il valore numerico è riportato in ogni cella."
    )
    sel_dims = st.multiselect(
        "Seleziona dimensioni (minimo 2)",
        options=dim_cols, default=dim_cols, key="corr_dims",
    )
    if len(sel_dims) < 2:
        st.warning("Seleziona almeno 2 dimensioni.")
    else:
        st.plotly_chart(
            plot_correlation_heatmap(df_f, dim_cols, sel_dims),
            use_container_width=True,
        )
        with st.expander("Tabella correlazioni con p-value"):
            sub = df_f[sel_dims].dropna()
            pairs = []
            for i, a in enumerate(sel_dims):
                for j, b in enumerate(sel_dims):
                    if j > i:
                        r_v, p_v = stats.pearsonr(sub[a], sub[b])
                        pairs.append({
                            "Dim A": a, "Dim B": b,
                            "r": round(r_v, 3), "p-value": round(p_v, 4),
                            "Significativo": "Sì" if p_v < 0.05 else "No",
                        })
            st.dataframe(
                pd.DataFrame(pairs).sort_values("r", key=abs, ascending=False).head(15),
                use_container_width=True, hide_index=True,
            )

# ══════════════════════════════════════════════
# TAB 4 — RADAR
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Profilo identitario per segmento</div>',
                unsafe_allow_html=True)
    note(
        "Il radar mostra la media di ogni dimensione per ciascun gruppo. "
        "Ogni gruppo ha colore e stile di linea diversi (distinguibile anche in stampa in bianco e nero). "
        "Scala radiale: −2 (polo negativo) → +2 (polo positivo)."
    )
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        group_col = st.selectbox(
            "Raggruppa per",
            ["eta", "rapporto"],
            format_func=lambda x: "Fascia d'età" if x == "eta" else "Rapporto con la città",
        )
    with col_r2:
        avail = sorted(df_f[group_col].dropna().unique().tolist())
        sel_grp = st.multiselect("Gruppi", avail,
                                 default=avail[:min(4, len(avail))])
    if not sel_grp:
        st.warning("Seleziona almeno un gruppo.")
    else:
        st.plotly_chart(
            plot_radar(df_f, dim_cols, group_col, sel_grp),
            use_container_width=True,
        )

# ══════════════════════════════════════════════
# TAB 5 — GAP ANALYSIS
# ══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">Gap Analysis — Maddaloni oggi vs. domani</div>',
                unsafe_allow_html=True)
    note(
        "Sinistra: poli percepiti come più dominanti nell'identità attuale (intensità media ≥ 0.5). "
        "Destra: aggettivi scelti per la Maddaloni di domani (frequenza % su tutte e tre le scelte). "
        "Il confronto mostra la distanza tra immaginario attuale e aspirato."
    )
    st.plotly_chart(plot_gap(df_f), use_container_width=True)

    st.markdown('<div class="section-title">Frequenze per set di aggettivi</div>',
                unsafe_allow_html=True)
    cg1, cg2, cg3 = st.columns(3)
    labels_set = ["Set A — Estetica", "Set B — Carattere", "Set C — Valori"]
    for col_name, col_g, lbl in zip(
        ["desiderata_1", "desiderata_2", "desiderata_3"],
        [cg1, cg2, cg3], labels_set,
    ):
        with col_g:
            st.markdown(f"**{lbl}**")
            vc = df_f[col_name].value_counts().reset_index()
            vc.columns = ["Aggettivo", "N"]
            vc["%"] = (vc["N"] / n_filt * 100).round(1).astype(str) + "%"
            st.dataframe(vc, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown(
    '<div class="footer" role="contentinfo">'
    'Dashboard sviluppata per ricerca scientifica · '
    'Dati raccolti marzo 2026 · Aggregati e anonimi · '
    'Metodologia: Differenziale Semantico (Osgood, 1957) · '
    'Accessibilità: WCAG 2.1 AA'
    '</div>',
    unsafe_allow_html=True,
)
