# ============================================================
#  app.py — Dashboard Plotly Dash (version corrigée)
#  Projet Huile d'Olive International — MSc2 INSEEC 2026
# ============================================================

import os
import sys

# Ajoute le dossier python/ au path pour importer db.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python'))

import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Charge le .env depuis la racine du projet
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from db import run_query

# ============================================================
# THÈME ET COULEURS
# ============================================================

COLORS = {
    "bg"         : "#0F1923",
    "card"       : "#162231",
    "card_border": "#1E3448",
    "gold"       : "#D4A843",
    "silver"     : "#8FA8C8",
    "bronze"     : "#C4875A",
    "green"      : "#2ECC71",
    "red"        : "#E74C3C",
    "text"       : "#E8EDF2",
    "text_muted" : "#6B8CAE",
    "accent"     : "#1ABC9C",
}

SEGMENT_COLORS = {
    "Gold"  : COLORS["gold"],
    "Silver": COLORS["silver"],
    "Bronze": COLORS["bronze"],
}

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font         =dict(color=COLORS["text"], family="Georgia, serif"),
    xaxis        =dict(gridcolor="#1E3448", linecolor="#1E3448"),
    yaxis        =dict(gridcolor="#1E3448", linecolor="#1E3448"),
    legend       =dict(bgcolor="rgba(0,0,0,0)"),
    margin       =dict(l=40, r=20, t=40, b=40),
)

# ============================================================
# CHARGEMENT DES DONNÉES AU DÉMARRAGE
# ============================================================

def load_all_data() -> dict:
    """Charge toutes les données depuis MySQL au démarrage."""

    df_rfm = run_query("""
        SELECT id_client, nom_societe, pays_client, type_client,
               recence_jours, frequence, valeur_totale, panier_moyen,
               score_rfm, segment_rfm, client_a_risque
        FROM rfm_resultats
        ORDER BY valeur_totale DESC
    """)

    df_ca_pays = run_query("""
        SELECT c.pays_client,
               COUNT(DISTINCT c.id_client)        AS nb_clients,
               COUNT(o.id_commande)               AS nb_commandes,
               ROUND(SUM(o.montant_total), 2)     AS ca_total
        FROM clients c
        INNER JOIN commandes o ON c.id_client = o.id_client
        WHERE o.statut != 'Annulée'
        GROUP BY c.pays_client
        ORDER BY ca_total DESC
        LIMIT 12
    """)

    df_types = run_query("""
        SELECT p.type_huile,
               SUM(cp.quantite_litres)                          AS litres_vendus,
               ROUND(SUM(cp.quantite_litres * cp.prix_unitaire), 2) AS ca_type
        FROM produits p
        INNER JOIN commande_produit cp ON p.id_produit = cp.id_produit
        GROUP BY p.type_huile
        ORDER BY ca_type DESC
    """)

    df_mois = run_query("""
        SELECT DATE_FORMAT(date_commande, '%Y-%m') AS mois,
               COUNT(id_commande)                  AS nb_commandes,
               ROUND(SUM(montant_total), 2)        AS ca_mensuel
        FROM commandes
        WHERE statut != 'Annulée'
        GROUP BY mois
        ORDER BY mois
    """)

    return {
        "rfm"    : df_rfm,
        "ca_pays": df_ca_pays,
        "types"  : df_types,
        "mois"   : df_mois,
    }


print("📊 Chargement des données MySQL...")
DATA = load_all_data()
print("✅ Données chargées.")

# ============================================================
# COMPOSANT KPI CARD
# ============================================================

def kpi_card(title: str, value: str, icon: str, color: str) -> html.Div:
    """Crée une carte KPI stylisée."""
    return html.Div([
        html.Div(icon,  style={"fontSize": "22px", "marginBottom": "6px"}),
        html.Div(value, style={
            "fontSize": "26px", "fontWeight": "700",
            "color": color, "fontFamily": "Georgia, serif",
        }),
        html.Div(title, style={
            "fontSize": "10px", "color": COLORS["text_muted"],
            "marginTop": "4px", "textTransform": "uppercase",
            "letterSpacing": "1.5px",
        }),
    ], style={
        "backgroundColor": COLORS["card"],
        "border"         : f"1px solid {COLORS['card_border']}",
        "borderTop"      : f"3px solid {color}",
        "borderRadius"   : "12px",
        "padding"        : "18px",
        "textAlign"      : "center",
        "flex"           : "1",
        "minWidth"       : "130px",
    })

# ============================================================
# OPTIONS DES FILTRES
# ============================================================

TYPE_OPTIONS = [{"label": "Tous les types", "value": "tous"}] + [
    {"label": t, "value": t}
    for t in sorted(DATA["rfm"]["type_client"].dropna().unique())
]

PAYS_OPTIONS = [{"label": "Tous les pays", "value": "tous"}] + [
    {"label": p, "value": p}
    for p in sorted(DATA["rfm"]["pays_client"].dropna().unique())
]

SEGMENT_OPTIONS = [
    {"label": "Tous les segments", "value": "tous"},
    {"label": "⭐ Gold",           "value": "Gold"},
    {"label": "🥈 Silver",         "value": "Silver"},
    {"label": "🥉 Bronze",         "value": "Bronze"},
]

# ============================================================
# LAYOUT
# ============================================================

app = Dash(__name__, title="🫒 Olive Oil Dashboard")

app.layout = html.Div([

    # En-tête
    html.Div([
        html.Div([
            html.Span("🫒", style={"fontSize": "30px", "marginRight": "12px"}),
            html.Div([
                html.H1("Olive Oil Intelligence", style={
                    "margin": "0", "fontSize": "22px",
                    "color": COLORS["text"], "fontFamily": "Georgia, serif",
                    "letterSpacing": "2px",
                }),
                html.P("Analyse RFM & Performance commerciale", style={
                    "margin": "2px 0 0", "fontSize": "11px",
                    "color": COLORS["text_muted"], "letterSpacing": "1px",
                }),
            ]),
        ], style={"display": "flex", "alignItems": "center"}),
        html.Div("MSc2 Manager Data Marketing — INSEEC 2026", style={
            "fontSize": "11px", "color": COLORS["text_muted"],
        }),
    ], style={
        "display": "flex", "justifyContent": "space-between",
        "alignItems": "center", "padding": "18px 32px",
        "backgroundColor": COLORS["card"],
        "borderBottom": f"1px solid {COLORS['card_border']}",
    }),

    # Filtres
    html.Div([
        html.Div([
            html.Label("TYPE DE CLIENT", style={
                "fontSize": "10px", "color": COLORS["text_muted"],
                "letterSpacing": "2px", "marginBottom": "6px", "display": "block",
            }),
            dcc.Dropdown(id="filter-type", options=TYPE_OPTIONS,
                         value="tous", clearable=False),
        ], style={"flex": "1", "minWidth": "200px"}),

        html.Div([
            html.Label("PAYS CLIENT", style={
                "fontSize": "10px", "color": COLORS["text_muted"],
                "letterSpacing": "2px", "marginBottom": "6px", "display": "block",
            }),
            dcc.Dropdown(id="filter-pays", options=PAYS_OPTIONS,
                         value="tous", clearable=False),
        ], style={"flex": "1", "minWidth": "200px"}),

        html.Div([
            html.Label("SEGMENT RFM", style={
                "fontSize": "10px", "color": COLORS["text_muted"],
                "letterSpacing": "2px", "marginBottom": "6px", "display": "block",
            }),
            dcc.Dropdown(id="filter-segment", options=SEGMENT_OPTIONS,
                         value="tous", clearable=False),
        ], style={"flex": "1", "minWidth": "200px"}),

    ], style={
        "display": "flex", "gap": "16px", "flexWrap": "wrap",
        "padding": "18px 32px",
        "backgroundColor": COLORS["card"],
        "borderBottom": f"1px solid {COLORS['card_border']}",
    }),

    # KPIs
    html.Div(id="kpi-row", style={
        "display": "flex", "gap": "16px",
        "padding": "24px 32px", "flexWrap": "wrap",
    }),

    # Graphiques ligne 1
    html.Div([
        html.Div([
            html.H3("Segmentation RFM", style={
                "color": COLORS["text"], "fontSize": "12px",
                "letterSpacing": "2px", "textTransform": "uppercase",
                "marginBottom": "10px",
            }),
            dcc.Graph(id="chart-segments", config={"displayModeBar": False}),
        ], style={
            "flex": "1", "minWidth": "280px",
            "backgroundColor": COLORS["card"],
            "border": f"1px solid {COLORS['card_border']}",
            "borderRadius": "12px", "padding": "18px",
        }),

        html.Div([
            html.H3("CA par pays client", style={
                "color": COLORS["text"], "fontSize": "12px",
                "letterSpacing": "2px", "textTransform": "uppercase",
                "marginBottom": "10px",
            }),
            dcc.Graph(id="chart-pays", config={"displayModeBar": False}),
        ], style={
            "flex": "2", "minWidth": "380px",
            "backgroundColor": COLORS["card"],
            "border": f"1px solid {COLORS['card_border']}",
            "borderRadius": "12px", "padding": "18px",
        }),
    ], style={"display": "flex", "gap": "16px",
              "padding": "0 32px 16px", "flexWrap": "wrap"}),

    # Graphiques ligne 2
    html.Div([
        html.Div([
            html.H3("Types d'huile", style={
                "color": COLORS["text"], "fontSize": "12px",
                "letterSpacing": "2px", "textTransform": "uppercase",
                "marginBottom": "10px",
            }),
            dcc.Graph(id="chart-types", config={"displayModeBar": False}),
        ], style={
            "flex": "1", "minWidth": "280px",
            "backgroundColor": COLORS["card"],
            "border": f"1px solid {COLORS['card_border']}",
            "borderRadius": "12px", "padding": "18px",
        }),

        html.Div([
            html.H3("RFM — Récence vs Valeur", style={
                "color": COLORS["text"], "fontSize": "12px",
                "letterSpacing": "2px", "textTransform": "uppercase",
                "marginBottom": "10px",
            }),
            dcc.Graph(id="chart-scatter", config={"displayModeBar": False}),
        ], style={
            "flex": "2", "minWidth": "380px",
            "backgroundColor": COLORS["card"],
            "border": f"1px solid {COLORS['card_border']}",
            "borderRadius": "12px", "padding": "18px",
        }),
    ], style={"display": "flex", "gap": "16px",
              "padding": "0 32px 16px", "flexWrap": "wrap"}),

    # Graphique ligne 3 — Évolution mensuelle
    html.Div([
        html.Div([
            html.H3("Évolution CA mensuel 2024", style={
                "color": COLORS["text"], "fontSize": "12px",
                "letterSpacing": "2px", "textTransform": "uppercase",
                "marginBottom": "10px",
            }),
            dcc.Graph(id="chart-evolution", config={"displayModeBar": False}),
        ], style={
            "width": "100%",
            "backgroundColor": COLORS["card"],
            "border": f"1px solid {COLORS['card_border']}",
            "borderRadius": "12px", "padding": "18px",
        }),
    ], style={"padding": "0 32px 32px"}),

], style={"backgroundColor": COLORS["bg"], "minHeight": "100vh",
          "fontFamily": "Georgia, serif"})


# ============================================================
# CALLBACK PRINCIPAL
# ============================================================

@app.callback(
    Output("kpi-row",       "children"),
    Output("chart-segments","figure"),
    Output("chart-pays",    "figure"),
    Output("chart-types",   "figure"),
    Output("chart-scatter", "figure"),
    Output("chart-evolution","figure"),
    Input("filter-type",    "value"),
    Input("filter-pays",    "value"),
    Input("filter-segment", "value"),
)
def update_dashboard(type_client: str, pays: str, segment: str):
    """
    Met à jour tout le dashboard selon les filtres sélectionnés.

    Args:
        type_client : filtre sur le type de client
        pays        : filtre sur le pays client
        segment     : filtre sur le segment RFM
    """

    # ── Filtrage ──────────────────────────────────────────────
    df = DATA["rfm"].copy()
    if type_client != "tous":
        df = df[df["type_client"] == type_client]
    if pays != "tous":
        df = df[df["pays_client"] == pays]
    if segment != "tous":
        df = df[df["segment_rfm"] == segment]

    # ── Calcul KPIs depuis les données filtrées ────────────────
    ca_total       = df["valeur_totale"].sum()
    panier_moyen   = df["panier_moyen"].mean() if len(df) > 0 else 0
    nb_clients     = len(df)
    clients_risque = int(df["client_a_risque"].sum())
    gold_count     = len(df[df["segment_rfm"] == "Gold"])
    total_cmd      = int(df["frequence"].sum())

    kpis = html.Div([
        kpi_card("Chiffre d'affaires", f"{ca_total:,.0f} €",    "💶", COLORS["gold"]),
        kpi_card("Clients analysés",   str(nb_clients),          "👥", COLORS["accent"]),
        kpi_card("Panier moyen",       f"{panier_moyen:,.0f} €", "🛒", COLORS["silver"]),
        kpi_card("Clients Gold",       str(gold_count),          "⭐", COLORS["gold"]),
        kpi_card("Commandes",          str(total_cmd),           "📦", COLORS["accent"]),
        kpi_card("Clients à risque",   str(clients_risque),      "⚠️", COLORS["red"]),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "width": "100%"})

    # ── Graphique 1 : Segments RFM ────────────────────────────
    seg = df["segment_rfm"].value_counts().reset_index()
    seg.columns = ["segment", "nb"]
    fig_seg = go.Figure(go.Bar(
        x            = seg["segment"],
        y            = seg["nb"],
        marker_color = [SEGMENT_COLORS.get(s, COLORS["accent"]) for s in seg["segment"]],
        text         = seg["nb"],
        textposition = "outside",
        textfont     = dict(color=COLORS["text"]),
    ))
    fig_seg.update_layout(**LAYOUT_BASE, height=280, showlegend=False)

    # ── Graphique 2 : CA par pays ─────────────────────────────
    df_pays = DATA["ca_pays"].copy()
    if pays != "tous":
        df_pays = df_pays[df_pays["pays_client"] == pays]

    fig_pays = go.Figure(go.Bar(
        x            = df_pays["ca_total"],
        y            = df_pays["pays_client"],
        orientation  = "h",
        marker_color = COLORS["accent"],
        text         = df_pays["ca_total"].apply(lambda x: f"{x:,.0f} €"),
        textposition = "outside",
        textfont     = dict(color=COLORS["text"], size=10),
    ))
    fig_pays.update_layout(**{
        **LAYOUT_BASE,
        "height": 280,
        "yaxis": dict(gridcolor="#1E3448", linecolor="#1E3448", autorange="reversed"),
    })

    # ── Graphique 3 : Types d'huile pie ───────────────────────
    fig_types = go.Figure(go.Pie(
        labels       = DATA["types"]["type_huile"],
        values       = DATA["types"]["ca_type"],
        hole         = 0.4,
        marker_colors= [COLORS["gold"], COLORS["accent"],
                        COLORS["silver"], COLORS["bronze"]],
    ))
    fig_types.update_layout(**LAYOUT_BASE, height=280)

    # ── Graphique 4 : Scatter RFM ─────────────────────────────
    if len(df) == 0:
        fig_scatter = go.Figure()
        fig_scatter.update_layout(**LAYOUT_BASE, height=280)
    else:
        fig_scatter = px.scatter(
            df,
            x          = "recence_jours",
            y          = "valeur_totale",
            color      = "segment_rfm",
            size       = "frequence",
            hover_name = "nom_societe",
            color_discrete_map=SEGMENT_COLORS,
            labels={
                "recence_jours": "Récence (jours)",
                "valeur_totale": "Valeur totale (€)",
                "segment_rfm"  : "Segment",
            },
        )
        fig_scatter.update_layout(**LAYOUT_BASE, height=280)

    # ── Graphique 5 : Évolution mensuelle ─────────────────────
    fig_evo = go.Figure()
    fig_evo.add_trace(go.Scatter(
        x         = DATA["mois"]["mois"],
        y         = DATA["mois"]["ca_mensuel"],
        mode      = "lines+markers",
        line      = dict(color=COLORS["gold"], width=2),
        marker    = dict(color=COLORS["gold"], size=7),
        fill      = "tozeroy",
        fillcolor = "rgba(212,168,67,0.1)",
        name      = "CA mensuel (€)",
    ))
    fig_evo.add_trace(go.Bar(
        x            = DATA["mois"]["mois"],
        y            = DATA["mois"]["nb_commandes"],
        name         = "Nb commandes",
        marker_color = COLORS["accent"],
        opacity      = 0.4,
        yaxis        = "y2",
    ))
    fig_evo.update_layout(**{
        **LAYOUT_BASE,
        "height"   : 260,
        "yaxis"    : dict(title="CA mensuel (€)", gridcolor="#1E3448"),
        "yaxis2"   : dict(title="Nb commandes", overlaying="y",
                          side="right", gridcolor="rgba(0,0,0,0)"),
        "hovermode": "x unified",
    })

    return kpis, fig_seg, fig_pays, fig_types, fig_scatter, fig_evo


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":
    print("\n🫒 Dashboard Olive Oil — démarrage...")
    print("👉 Ouvre : http://127.0.0.1:8050\n")
    app.run(debug=True, port=8050)
