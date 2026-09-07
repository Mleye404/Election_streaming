"""
Election Streaming - Dashboard temps réel

Lit directement les tables PostgreSQL alimentées en continu par le
pipeline Spark (spark/app.py). Aucune donnée fictive : si les tables
sont vides (pipeline pas encore démarré / aucun vote traité), le
dashboard l'indique clairement plutôt que d'afficher des chiffres
inventés.
"""

import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False


# =====================================
# Configuration
# =====================================

st.set_page_config(
    page_title="Election Streaming Dashboard",
    page_icon="🗳️",
    layout="wide",
)

REFRESH_MS = 3000  # 3 secondes

PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "elections")
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

DB_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

TABLES = [
    "votes_par_candidat",
    "votes_par_region",
    "votes_par_parti",
    "participation_diaspora",
]


# =====================================
# Style
# =====================================

st.markdown(
    """
    <style>
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #dc2626;
        color: white;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .live-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: white;
        animation: pulse 1.4s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    div[data-testid="stMetric"] {
        background-color: rgba(120, 120, 120, 0.08);
        border-radius: 12px;
        padding: 14px 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================
# Connexion PostgreSQL
# =====================================

@st.cache_resource
def get_engine():
    return create_engine(DB_URL, pool_pre_ping=True)


@st.cache_data(ttl=1)
def load_table(table_name: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(f"SELECT * FROM {table_name}", conn)


# =====================================
# En-tête
# =====================================

header_left, header_right = st.columns([4, 1])

with header_left:
    st.title("🗳️ Election Streaming Dashboard")
    st.caption("Suivi des résultats électoraux en temps réel — Kafka → Spark → PostgreSQL")

with header_right:
    st.markdown(
        '<div style="text-align:right; padding-top: 18px;">'
        '<span class="live-badge"><span class="live-dot"></span> LIVE</span>'
        "</div>",
        unsafe_allow_html=True,
    )

if HAS_AUTOREFRESH:
    st_autorefresh(interval=REFRESH_MS, key="dashboard_refresh")
else:
    st.warning(
        "Le paquet `streamlit-autorefresh` n'est pas installé — "
        "l'actualisation automatique est désactivée. "
        "Installez-le pour un rafraîchissement toutes les 3 secondes."
    )


# =====================================
# Chargement des données réelles
# =====================================

try:
    data = {table: load_table(table) for table in TABLES}
except (OperationalError, ProgrammingError):
    st.info(
        "⏳ En attente des premières données du pipeline...\n\n"
        "PostgreSQL n'est pas encore joignable, ou les tables Gold "
        "n'ont pas encore été créées par Spark. Vérifie que "
        "`docker compose up --build` a bien démarré `kafka`, `producer`, "
        "`spark-master` et `postgres`, puis patiente quelques secondes "
        "(le premier micro-batch Spark arrive sous ~5 secondes)."
    )
    st.stop()
except Exception as exc:  # connexion impossible, etc.
    st.error(f"Impossible de se connecter à PostgreSQL : {exc}")
    st.stop()

candidats_df = data["votes_par_candidat"]
regions_df = data["votes_par_region"]
partis_df = data["votes_par_parti"]
diaspora_df = data["participation_diaspora"]

if candidats_df.empty:
    st.info(
        "⏳ Le pipeline tourne mais aucun vote n'a encore été agrégé. "
        "Le producer envoie un vote toutes les quelques secondes — "
        "cette page se met à jour automatiquement."
    )
    st.stop()

candidats_df = candidats_df.sort_values("nombre_votes", ascending=False).reset_index(drop=True)


# =====================================
# Indicateurs principaux
# =====================================

total_votes = int(candidats_df["nombre_votes"].sum())
nb_candidats = candidats_df["candidat"].nunique()
nb_regions = regions_df["region"].nunique() if not regions_df.empty else 0
leader = candidats_df.iloc[0]

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total votes", f"{total_votes:,}".replace(",", " "))
kpi2.metric("Candidats", nb_candidats)
kpi3.metric("Régions", nb_regions)
kpi4.metric("Candidat en tête", leader["candidat"])
kpi5.metric("Votes du leader", f"{int(leader['nombre_votes']):,}".replace(",", " "))

st.caption(f"Dernière actualisation : {datetime.now().strftime('%H:%M:%S')}")

st.divider()


# =====================================
# Votes par candidat + classement
# =====================================

col_chart, col_ranking = st.columns([3, 2])

with col_chart:
    st.subheader("Votes par candidat")
    fig_candidats = px.bar(
        candidats_df,
        x="nombre_votes",
        y="candidat",
        orientation="h",
        text="nombre_votes",
        color="candidat",
    )
    fig_candidats.update_layout(
        showlegend=False,
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="Votes",
        yaxis_title="",
        height=420,
    )
    st.plotly_chart(fig_candidats, use_container_width=True)

with col_ranking:
    st.subheader("Classement")
    ranking_df = candidats_df.copy()
    ranking_df.insert(0, "Rang", range(1, len(ranking_df) + 1))
    ranking_df["% des votes"] = (ranking_df["nombre_votes"] / total_votes * 100).round(1)
    ranking_df = ranking_df.rename(columns={"candidat": "Candidat", "nombre_votes": "Votes"})
    st.dataframe(
        ranking_df[["Rang", "Candidat", "Votes", "% des votes"]],
        hide_index=True,
        use_container_width=True,
        height=420,
    )

st.divider()


# =====================================
# Votes par région + votes par parti
# =====================================

col_region, col_parti = st.columns(2)

with col_region:
    st.subheader("Votes par région")
    if regions_df.empty:
        st.caption("Pas encore de données régionales.")
    else:
        regions_df = regions_df.sort_values("nombre_votes", ascending=False)
        fig_region = px.bar(
            regions_df,
            x="region",
            y="nombre_votes",
            color="nombre_votes",
            color_continuous_scale="Blues",
        )
        fig_region.update_layout(
            xaxis_title="",
            yaxis_title="Votes",
            coloraxis_showscale=False,
            height=380,
        )
        st.plotly_chart(fig_region, use_container_width=True)

with col_parti:
    st.subheader("Votes par parti")
    if partis_df.empty:
        st.caption("Pas encore de données par parti.")
    else:
        fig_parti = px.pie(
            partis_df,
            names="parti",
            values="nombre_votes",
            hole=0.45,
        )
        fig_parti.update_layout(height=380)
        st.plotly_chart(fig_parti, use_container_width=True)

st.divider()


# =====================================
# Participation nationale / diaspora
# =====================================

st.subheader("Participation nationale / diaspora")
if diaspora_df.empty:
    st.caption("Pas encore de données de participation.")
else:
    col_pie, col_table = st.columns([2, 1])
    with col_pie:
        fig_diaspora = px.pie(
            diaspora_df,
            names="type_vote",
            values="nombre_votes",
            color="type_vote",
            color_discrete_map={"National": "#2563eb", "Diaspora": "#f59e0b"},
        )
        fig_diaspora.update_layout(height=320)
        st.plotly_chart(fig_diaspora, use_container_width=True)
    with col_table:
        st.dataframe(
            diaspora_df.rename(columns={"type_vote": "Type", "nombre_votes": "Votes"}),
            hide_index=True,
            use_container_width=True,
        )
