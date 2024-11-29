import streamlit as st
import pandas as pd
import plotly.express as px

def style_metric_cards(background_color="#abc4f7"):
    st.markdown(
        f"""
        <style>
        div[data-testid="metric-container"] {{
            background-color: {background_color};
            border-radius: 5px;
            padding: 5px;
            border: 1px solid #CCCCCC;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def show_overview(df_nbr_hospi, df_duree_hospi, main_metrics):
    st.subheader("📊 Vue d'ensemble des données")

    # Affichage des métriques dans des cartes stylisées
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Hospitalisations en 2018",
            value=f"{main_metrics['hospi_2018'] / 1_000_000:.2f}M",
            delta=None,
            help="Nombre total d'hospitalisations en 2018"
        )
    with col2:
        value_2018 = main_metrics["hospi_2018"]
        value_2019 = main_metrics["hospi_2019"]
        delta_2019 = ((value_2019 - value_2018) / value_2018) * 100
        st.metric(
            label="Hospitalisations en 2019",
            value=f"{value_2019 / 1_000_000:.2f}M",
            delta=f"{delta_2019:.2f}%",
            help="Nombre total d'hospitalisations en 2019 et variation par rapport à 2018"
        )
    with col3:
        value_2019 = main_metrics["hospi_2019"]
        value_2020 = main_metrics["hospi_2020"]
        delta_2020 = ((value_2020 - value_2019) / value_2019) * 100
        st.metric(
            label="Hospitalisations en 2020",
            value=f"{value_2020 / 1_000_000:.2f}M",
            delta=f"{delta_2020:.2f}%",
            help="Nombre total d'hospitalisations en 2020 et variation par rapport à 2019"
        )
    with col4:
        value_2020 = main_metrics["hospi_2020"]
        value_2021 = main_metrics["hospi_2021"]
        delta_2021 = ((value_2021 - value_2020) / value_2020) * 100
        st.metric(
            label="Hospitalisations en 2021",
            value=f"{value_2021 / 1_000_000:.2f}M",
            delta=f"{delta_2021:.2f}%",
            help="Nombre total d'hospitalisations en 2021 et variation par rapport à 2020"
        )
    with col5:
        value_2021 = main_metrics["hospi_2021"]
        value_2022 = main_metrics["hospi_2022"]
        delta_2022 = ((value_2022 - value_2021) / value_2021) * 100
        st.metric(
            label="Hospitalisations en 2022",
            value=f"{value_2022 / 1_000_000:.2f}M",
            delta=f"{delta_2022:.2f}%",
            help="Nombre total d'hospitalisations en 2022 et variation par rapport à 2021"
        )
    st.markdown("</div>", unsafe_allow_html=True)
    style_metric_cards(background_color="#abc4f7")

    # Affichage des lits disponibles
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            label="Lits disponibles en 2018",
            value=main_metrics["lits_2018"],
            delta=None,
            help="Nombre total de lits disponibles en 2018"
        )
    with col2:
        value_2018_lits = main_metrics["lits_2018"]
        value_2019_lits = main_metrics["lits_2019"]
        delta_2019_lits = ((value_2019_lits - value_2018_lits) / value_2018_lits) * 100
        st.metric(
            label="Lits disponibles en 2019",
            value=value_2019_lits,
            delta=f"{delta_2019_lits:.2f}%",
            help="Nombre total de lits disponibles en 2019 et variation par rapport à 2018"
        )
    with col3:
        value_2020_lits = main_metrics["lits_2020"]
        delta_2020_lits = ((value_2020_lits - value_2019_lits) / value_2019_lits) * 100
        st.metric(
            label="Lits disponibles en 2020",
            value=value_2020_lits,
            delta=f"{delta_2020_lits:.2f}%",
            help="Nombre total de lits disponibles en 2020 et variation par rapport à 2019"
        )
    with col4:
        value_2021_lits = main_metrics["lits_2021"]
        delta_2021_lits = ((value_2021_lits - value_2020_lits) / value_2020_lits) * 100
        st.metric(
            label="Lits disponibles en 2021",
            value=value_2021_lits,
            delta=f"{delta_2021_lits:.2f}%",
            help="Nombre total de lits disponibles en 2021 et variation par rapport à 2020"
        )
    with col5:
        value_2022_lits = main_metrics["lits_2022"]
        delta_2022_lits = ((value_2022_lits - value_2021_lits) / value_2021_lits) * 100
        st.metric(
            label="Lits disponibles en 2022",
            value=value_2022_lits,
            delta=f"{delta_2022_lits:.2f}%",
            help="Nombre total de lits disponibles en 2022 et variation par rapport à 2021"
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Tendances temporelles avec tooltips améliorés
    st.subheader("📈 Évolution temporelle")
    col1, col2 = st.columns(2)

    with col1:
        hospi_by_year = df_nbr_hospi.groupby('year')['nbr_hospi'].sum().reset_index()
        fig = px.line(hospi_by_year, x='year', y='nbr_hospi',
                     title='Nombre d\'hospitalisations par année',
                     labels={'year': 'Année', 'nbr_hospi': 'Nombre d\'hospitalisations'},
                     custom_data=['year', 'nbr_hospi'])
        fig.update_traces(
            hovertemplate="<b>Année:</b> %{customdata[0]}<br>" +
                         "<b>Hospitalisations:</b> %{customdata[1]:,.0f}<br><extra></extra>"
        )
        fig.update_layout(
            hoverlabel=dict(bgcolor="white"),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        duree_by_year = df_duree_hospi.groupby('year')['AVG_duree_hospi'].mean().reset_index()
        fig = px.line(duree_by_year, x='year', y='AVG_duree_hospi',
                     title='Durée moyenne des hospitalisations par année',
                     labels={'year': 'Année', 'AVG_duree_hospi': 'Durée moyenne (jours)'},
                     custom_data=['year', 'AVG_duree_hospi'])
        fig.update_traces(
            hovertemplate="<b>Année:</b> %{customdata[0]}<br>" +
                         "<b>Durée moyenne:</b> %{customdata[1]:.1f} jours<br><extra></extra>"
        )
        fig.update_layout(
            hoverlabel=dict(bgcolor="white"),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)