import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.cloud import bigquery
from streamlit_extras.metric_cards import style_metric_cards 
import time
import folium
from streamlit_folium import st_folium
import json
from pygwalker.api.streamlit import StreamlitRenderer
import pygwalker as pyg
from langchain_openai import AzureChatOpenAI
import numpy as np


# Styles CSS personnalisés
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
    }
    .main-title {
        color: #2c3e50;
        text-align: center;
        padding: 1rem 0;
        font-size: 2.5rem;
    }
    .section-title {
        color: #34495e;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
    }
    .insight-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 0.5rem 0;
    }
    .tab-content {
        padding: 1rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Définition des couleurs du thème
MAIN_COLOR = '#003366'  # Bleu marine principal
SECONDARY_COLOR = '#AFDC8F'  # Vert clair complémentaire
ACCENT_COLOR = '#3D7317'  # Vert foncé pour les accents

# Fonction de chargement des données avec gestion d'erreurs
@st.cache_resource
def fetch_data():
    try:
        # Chargement des secrets
        gcp_service_account = st.secrets["gcp_service_account"]
        client = bigquery.Client.from_service_account_info(gcp_service_account)
        
        # Chargement du dataset principal qui contient toutes les données
        df_complet = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_population`
        ''').to_dataframe()
        
        # Convertir les colonnes year en datetime
        df_complet['year'] = pd.to_datetime(df_complet['year'])
        
        # Créer des vues spécifiques pour maintenir la compatibilité avec le code existant
        df_nbr_hospi = df_complet[[
            'year', 'region', 'nom_region', 'pathologie', 'nom_pathologie', 'sexe',
            'nbr_hospi', 'evolution_nbr_hospi', 'evolution_percent_nbr_hospi',
            'hospi_prog_24h', 'hospi_autres_24h', 'hospi_total_24h'
        ]].copy()

        df_duree_hospi = df_complet[[
            'year', 'region', 'nom_region', 'pathologie', 'nom_pathologie',
            'AVG_duree_hospi', 'evolution_AVG_duree_hospi', 'evolution_percent_AVG_duree_hospi',
            'hospi_1J', 'hospi_2J', 'hospi_3J', 'hospi_4J', 'hospi_5J',
            'hospi_6J', 'hospi_7J', 'hospi_8J', 'hospi_9J', 'hospi_10J_19J',
            'hospi_20J_29J', 'hospi_30J', 'hospi_total_jj'
        ]].copy()

        df_tranche_age_hospi = df_complet[[
            'year', 'region', 'nom_region', 'pathologie', 'nom_pathologie',
            'tranche_age_0_1', 'tranche_age_1_4', 'tranche_age_5_14',
            'tranche_age_15_24', 'tranche_age_25_34', 'tranche_age_35_44',
            'tranche_age_45_54', 'tranche_age_55_64', 'tranche_age_65_74',
            'tranche_age_75_84', 'tranche_age_85_et_plus',
            'tx_brut_tt_age_pour_mille', 'tx_standard_tt_age_pour_mille',
            'indice_comparatif_tt_age_percent'
        ]].copy()
        
        # Charger uniquement les données de capacité
        df_capacite_hospi = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite_capacite.class_join_total_morbidite_capacite`
        ''').to_dataframe()
        
        # Convertir la colonne year en datetime pour df_capacite_hospi
        df_capacite_hospi['year'] = pd.to_datetime(df_capacite_hospi['year'])
        
        return df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, df_complet
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None, None, None, None, None

# Fonction pour calculer les métriques de la page principale
@st.cache_data
def calculate_main_metrics(df_nbr_hospi, df_capacite_hospi, selected_sex='Ensemble'):
    metrics = {}
    
    # Calcul des hospitalisations par année
    df_hospi_filtered = df_nbr_hospi[df_nbr_hospi['sexe'] == selected_sex]
    for year in range(2018, 2023):
        total_hospi = df_hospi_filtered["nbr_hospi"][df_hospi_filtered["year"].dt.year == year].sum()
        metrics[f"hospi_{year}"] = total_hospi

    # Calcul des lits disponibles par année
    lits_disponibles = df_capacite_hospi.groupby('year')['lit_hospi_complete'].sum().reset_index()
    for year in range(2018, 2023):
        metrics[f"lits_{year}"] = lits_disponibles[lits_disponibles['year'].dt.year == year]['lit_hospi_complete'].sum()
    
    return metrics

# Interface de chargement
def load_with_progress():
    # Centrer le GIF avec du CSS personnalisé
    st.markdown("""
        <style>
        .loading-gif {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Créer un conteneur pour le GIF centré
    gif_container = st.container()
    with gif_container:
        st.markdown('<div class="loading-gif">', unsafe_allow_html=True)
        gif_placeholder = st.empty()
        gif_placeholder.image("ezgif.com-crop.gif", width=300)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Créer la barre de progression séparément
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0, text="Initialisation du chargement...")
    
    try:
        # Chargement des données
        progress_bar.progress(10, text="Chargement des données...")
        df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, df_complet = fetch_data()
        
        if df_complet is None:
            gif_placeholder.empty()
            progress_bar.empty()
            st.stop()
        
        # Calcul des métriques
        progress_bar.progress(80, text="Calcul des métriques...")
        metrics = calculate_main_metrics(df_nbr_hospi, df_capacite_hospi, 'Ensemble')
        
        progress_bar.progress(100, text="Chargement terminé!")
        time.sleep(0.5)
        
        # Clear loading interface
        gif_placeholder.empty()
        progress_bar.empty()
        
        return df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, df_complet, metrics
        
    except Exception as e:
        gif_placeholder.empty()
        progress_bar.empty()
        st.error(f"Erreur inattendue: {str(e)}")
        st.stop()

# Chargement des données avec interface de progression
df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, df_complet, main_metrics = load_with_progress()

# Titre principal avec style amélioré
st.markdown("<h1 class='main-title' style='margin-top: -70px; margin-bottom: -8000px;'>🏥 Analyse hospitalière en France (2018-2022)</h1>", unsafe_allow_html=True)

# Suite du code uniquement si les données sont chargées correctement
if df_nbr_hospi is not None:
    # Filtres dans une card dédiée
    
    col1, col2, col3 = st.columns(3)

    with col1:
        # Sélection du niveau administratif
        niveau_administratif = st.selectbox(
            "Niveau administratif",
            ["Régions", "Départements"],
            key="niveau_administratif"
        )

    with col2:
        # Sélection du sexe
        selected_sex = st.selectbox(
            "Sexe",
            ["Ensemble", "Homme", "Femme"],
            key="selecteur_sexe"
        )

    with col3:
        # Filtre années avec une liste déroulante simple
        years = sorted(df_nbr_hospi['year'].dt.year.unique(), reverse=True)
        years_options = ["Toutes les années"] + [str(year) for year in years]
        selected_year = st.selectbox("Année", years_options, key="year_filter")
        
        # Convertir la sélection en liste d'années pour le filtrage
        if selected_year == "Toutes les années":
            selected_years = years
        else:
            selected_years = [int(selected_year)]

    # Sidebar pour la navigation
    st.sidebar.header("Navigation")
    
    # Filtrer le DataFrame en fonction du niveau sélectionné
    df_filtered = df_complet[df_complet['niveau'] == niveau_administratif]

    # Filtre régions/départements selon le niveau choisi
    territories = sorted(df_filtered['nom_region'].unique())
    territory_label = "régions" if niveau_administratif == "Régions" else "départements"
    
    select_all_territories = st.sidebar.checkbox(f"Sélectionner tous les {territory_label}", value=True)
    if select_all_territories:
        selected_territories = st.sidebar.multiselect(
            f"Sélectionner les {territory_label}",
            territories,
            default=territories
        )
    else:
        selected_territories = st.sidebar.multiselect(f"Sélectionner les {territory_label}", territories)
    
    # Appliquer les filtres aux DataFrames
    df_nbr_hospi_filtered = df_nbr_hospi[
        df_nbr_hospi['year'].dt.year.isin(selected_years) &
        df_nbr_hospi['nom_region'].isin(selected_territories)
    ]
    df_duree_hospi_filtered = df_duree_hospi[
        df_duree_hospi['year'].dt.year.isin(selected_years) &
        df_duree_hospi['nom_region'].isin(selected_territories)
    ]
    df_tranche_age_hospi_filtered = df_tranche_age_hospi[
        df_tranche_age_hospi['year'].dt.year.isin(selected_years) &
        df_tranche_age_hospi['nom_region'].isin(selected_territories)
    ]
    df_capacite_hospi_filtered = df_capacite_hospi[
        df_capacite_hospi['year'].dt.year.isin(selected_years) &
        df_capacite_hospi['nom_region'].isin(selected_territories)
    ]
    
    # Calcul des métriques principales avec le filtre de sexe sélectionné
    main_metrics = calculate_main_metrics(df_nbr_hospi, df_capacite_hospi, selected_sex)
    
    # Onglets principaux
    tab1, tab2, tab3, tab4, tab5= st.tabs([
        "📈 Vue générale",
        "🗺️ Analyse géographique",
        "🏥 Pathologies",
        "👥 Démographie",
        "Services Médicaux"

    ])
    
    # Vue Générale
    with tab1:
        st.markdown("""
            <div class="insight-card">
            <h3>📈 Évolution des hospitalisations et capacités</h3>
            <p>Suivez l'évolution du nombre d'hospitalisations et des capacités d'accueil au fil des années.
            Les indicateurs clés vous permettent de comprendre les tendances et les changements majeurs.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Nombre d'hospitalisations par année")
        
        # Affichage des métriques dans des cartes stylisées
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            value_2019 = main_metrics["hospi_2019"]
            value_2018 = main_metrics["hospi_2018"]
            delta_2019 = ((value_2019 - value_2018) / value_2018) * 100
            st.metric(
                label="2019",
                value=f"{value_2019 / 1_000_000:.2f}M",
                delta=f"{delta_2019:.2f}% vs 2018",
                help="Nombre total d'hospitalisations en 2019 et variation par rapport à 2018"
            )
        with col2:
            value_2020 = main_metrics["hospi_2020"]
            delta_2020 = ((value_2020 - value_2019) / value_2019) * 100
            st.metric(
                label="2020",
                value=f"{value_2020 / 1_000_000:.2f}M",
                delta=f"{delta_2020:.2f}% vs 2019",
                help="Nombre total d'hospitalisations en 2020 et variation par rapport à 2019"
            )
        with col3:
            value_2021 = main_metrics["hospi_2021"]
            delta_2021 = ((value_2021 - value_2020) / value_2020) * 100
            st.metric(
                label="2021",
                value=f"{value_2021 / 1_000_000:.2f}M",
                delta=f"{delta_2021:.2f}% vs 2020",
                help="Nombre total d'hospitalisations en 2021 et variation par rapport à 2020"
            )
        with col4:
            value_2022 = main_metrics["hospi_2022"]
            delta_2022 = ((value_2022 - value_2021) / value_2021) * 100
            st.metric(
                label="2022",
                value=f"{value_2022 / 1_000_000:.2f}M",
                delta=f"{delta_2022:.2f}% vs 2021",
                help="Nombre total d'hospitalisations en 2022 et variation par rapport à 2021"
            )
        with col5:
            value_2022_2018 = value_2022 - value_2018  # Calcul du nombre de lits perdus
            delta_total = ((value_2022 - value_2018) / value_2018) * 100
            st.metric(
                label="Évolution 2018-2022",
                value=f"+{value_2022_2018 / 1_000:.2f}K",
                delta=f"{delta_total:.2f}% vs 2018",
                help="Évolution du nombre total d'hospitalisations entre 2018 et 2022"
            )
        st.markdown("</div>", unsafe_allow_html=True)
        style_metric_cards(background_color="#F0F2F6",border_left_color= MAIN_COLOR)
        # Affichage des lits disponibles
        st.subheader("Nombre de lits disponibles par années")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            value_2019_lits = main_metrics["lits_2019"]
            value_2018_lits = main_metrics["lits_2018"]
            delta_2019_lits = ((value_2019_lits - value_2018_lits) / value_2018_lits) * 100
            st.metric(
                label="2019",
                value=f"{value_2019_lits / 1_000:.2f}K",
                delta=f"{delta_2019_lits:.2f}% vs 2018",
                help="Nombre total de lits disponibles en 2019 et variation par rapport à 2018"
            )
        with col2:
            value_2020_lits = main_metrics["lits_2020"]
            delta_2020_lits = ((value_2020_lits - value_2019_lits) / value_2019_lits) * 100
            st.metric(
                label="2020",
                value=f"{value_2020_lits / 1_000:.2f}K",
                delta=f"{delta_2020_lits:.2f}% vs 2019",
                help="Nombre total de lits disponibles en 2020 et variation par rapport à 2019"
            )
        with col3:
            value_2021_lits = main_metrics["lits_2021"]
            delta_2021_lits = ((value_2021_lits - value_2020_lits) / value_2020_lits) * 100
            st.metric(
                label="2021",
                value=f"{value_2021_lits / 1_000:.2f}K",
                delta=f"{delta_2021_lits:.2f}% vs 2020",
                help="NoKbre total de lits disponibles en 2021 et variation par rapport à 2020"
            )
        with col4:
            value_2022_lits = main_metrics["lits_2022"]
            delta_2022_lits = ((value_2022_lits - value_2021_lits) / value_2021_lits) * 100
            st.metric(
                label="2022",
                value=f"{value_2022_lits / 1_000:.2f}K",
                delta=f"{delta_2022_lits:.2f}% vs 2021",
                help="Nombre total de lits disponibles en 2022 et variation par rapport à 2021"
            )
        with col5:
            lits_perdus = value_2018_lits - value_2022_lits  # Calcul du nombre de lits perdus
            delta_total_lits = ((value_2022_lits - value_2018_lits) / value_2018_lits) * 100
            st.metric(
                label="Évolution 2018-2022",
                value=f"-{lits_perdus / 1_000:.2f}K",  # Affichage en milliers
                delta=f"{delta_total_lits:.2f}% vs 2018",
                help="Nombre de lits perdus entre 2018 et 2022 et pourcentage de diminution"
            )


        # Préparation des données
        hospi_by_year = df_nbr_hospi.groupby('year')['nbr_hospi'].sum().reset_index()
        duree_by_year = df_duree_hospi.groupby('year')['AVG_duree_hospi'].mean().reset_index()
        
        # Création du graphique combiné
        fig = go.Figure()

        # Ajout des barres pour le nombre d'hospitalisations
        fig.add_trace(
            go.Bar(
                x=hospi_by_year['year'],
                y=hospi_by_year['nbr_hospi'],
                name="Nombre d'hospitalisations",
                yaxis='y',
                marker_color=MAIN_COLOR,
                hovertemplate="<b>Année:</b> %{x|%Y}<br>" +
                             "<b>Hospitalisations:</b> %{y:,.0f}<br><extra></extra>"
            )
        )

        # Ajout de la ligne pour la durée moyenne
        fig.add_trace(
            go.Scatter(
                x=duree_by_year['year'],
                y=duree_by_year['AVG_duree_hospi'],
                name="Durée moyenne",
                yaxis='y2',
                line=dict(color=SECONDARY_COLOR, width=3),
                hovertemplate="<b>Année:</b> %{x|%Y}<br>" +
                             "<b>Durée moyenne:</b> %{y:.1f} jours<br><extra></extra>"
            )
        )

        # Mise à jour de la mise en page
        fig.update_layout(
            title="Évolution des hospitalisations et de leur durée moyenne",
            yaxis=dict(
                title="Nombre d'hospitalisations",
                titlefont=dict(color=MAIN_COLOR),
                tickfont=dict(color=MAIN_COLOR),
                showgrid=True
            ),
            yaxis2=dict(
                title="Durée moyenne (jours)",
                titlefont=dict(color=ACCENT_COLOR),
                tickfont=dict(color=ACCENT_COLOR),
                anchor="x",
                overlaying="y",
                side="right"
            ),
            xaxis=dict(
                title="Année",
                tickformat="%Y"
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified',
            hoverlabel=dict(bgcolor="white"),
            barmode='relative',
            template='plotly_white'
        )

        # Affichage du graphique
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="", value="", help="Ce graphique combine le nombre total d'hospitalisations (barres bleues) et la durée moyenne de séjour (ligne verte) par année. Passez votre souris sur les éléments du graphique pour voir les détails.")
        
    # Analyse Géographique
    with tab2:
        st.markdown("""
            <div class="insight-card">
            <h3>🗺️ Répartition géographique</h3>
            <p>Explorez la distribution des établissements et des hospitalisations à travers les régions françaises.
            Identifiez les zones de forte concentration et les disparités territoriales.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            # Adapter le groupby selon le niveau administratif
            territory_col = 'nom_region'
            territory_label = "région" if niveau_administratif == "Régions" else "département"
            
            hospi_by_territory = df_nbr_hospi_filtered.groupby(territory_col)['nbr_hospi'].sum().reset_index()
            hospi_by_territory = hospi_by_territory.sort_values(by='nbr_hospi', ascending=True)
            
            fig = px.bar(hospi_by_territory, x='nbr_hospi', y=territory_col,
                        title=f'Nombre d\'hospitalisations par {territory_label}',
                        labels={'nbr_hospi': 'Nombre d\'hospitalisations',
                               territory_col: territory_label.capitalize()},
                        custom_data=[territory_col, 'nbr_hospi'],
                        orientation='h')
            fig.update_traces(
                hovertemplate=f"<b>{territory_label.capitalize()}:</b> %{{customdata[0]}}<br>" +
                             "<b>Hospitalisations:</b> %{customdata[1]:,.0f}<br><extra></extra>",
                marker_color=MAIN_COLOR
            )
            fig.update_layout(height=600, template='plotly_white')
            col_chart, col_help = st.columns([1, 0.01])
            with col_chart:
                st.plotly_chart(fig, use_container_width=True)
            with col_help:
                st.metric(label="", value="", help=f"Ce graphique montre le nombre total d'hospitalisations par {territory_label}. Les barres sont triées par ordre croissant.")
        
        with col2:
            duree_by_territory = df_duree_hospi_filtered.groupby(territory_col)['AVG_duree_hospi'].mean().reset_index()
            duree_by_territory = duree_by_territory.sort_values(by='AVG_duree_hospi', ascending=True)
            
            fig = px.bar(duree_by_territory, x='AVG_duree_hospi', y=territory_col,
                        title=f'Durée moyenne des hospitalisations par {territory_label}',
                        labels={'AVG_duree_hospi': 'Durée moyenne (jours)',
                               territory_col: territory_label.capitalize()},
                        custom_data=[territory_col, 'AVG_duree_hospi'],
                        orientation='h')
            fig.update_traces(
                hovertemplate=f"<b>{territory_label.capitalize()}:</b> %{{customdata[0]}}<br>" +
                             "<b>Durée moyenne:</b> %{customdata[1]:.1f} jours<br><extra></extra>",
                marker_color=MAIN_COLOR
            )
            fig.update_layout(height=600, template='plotly_white')
            col_chart, col_help = st.columns([1, 0.01])
            with col_chart:
                st.plotly_chart(fig, use_container_width=True)
            with col_help:
                st.metric(label="", value="", help=f"Ce graphique présente la durée moyenne des séjours hospitaliers par {territory_label}. Les barres sont triées par ordre croissant.")

    # Pathologies
    with tab3:
        
        # Système de recherche avec autocomplétion
        all_pathologies = sorted(df_nbr_hospi_filtered['nom_pathologie'].unique())
        search_term = st.text_input("🔍 Rechercher une pathologie spécifique pour obtenir des détails sur celle-ci", "")
        
        # Filtrer et suggérer les pathologies pendant la saisie
        if search_term:
            filtered_pathologies = [path for path in all_pathologies if search_term.lower() in path.lower()]
            if filtered_pathologies:
                selected_pathology = st.selectbox(
                    "Sélectionner une pathologie dans les suggestions",
                    filtered_pathologies,
                    key="pathology_selector"
                )
                
                # Afficher les données pour la pathologie sélectionnée
                path_data = df_nbr_hospi_filtered[df_nbr_hospi_filtered['nom_pathologie'] == selected_pathology]
                total_hospi = path_data['nbr_hospi'].sum()
                avg_duration = df_duree_hospi_filtered[df_duree_hospi_filtered['nom_pathologie'] == selected_pathology]['AVG_duree_hospi'].mean()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Nombre total d'hospitalisations", f"{total_hospi:,.0f}")
                with col2:
                    st.metric("Durée moyenne de séjour", f"{avg_duration:.1f} jours")
            else:
                st.warning("Aucune pathologie trouvée avec ce terme de recherche.")
        
        st.divider()
        
        # Ajout d'un sélecteur pour filtrer le nombre de pathologies à afficher
        n_pathologies = st.slider("Nombre de pathologies à afficher", 5, 159, 20)
        
        # Top pathologies par nombre d'hospitalisations
        hospi_by_pathology = df_nbr_hospi_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().reset_index()
        hospi_by_pathology = hospi_by_pathology.sort_values(by='nbr_hospi', ascending=False).head(n_pathologies)
        
        # Ajout des données de durée moyenne
        duree_data = df_duree_hospi_filtered.groupby('nom_pathologie')['AVG_duree_hospi'].mean().reset_index()
        hospi_by_pathology = pd.merge(hospi_by_pathology, duree_data, on='nom_pathologie', how='left')

        # Création d'une figure avec deux axes Y
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Ajout des barres pour le nombre d'hospitalisations
        fig.add_trace(
            go.Bar(
                x=hospi_by_pathology['nom_pathologie'],
                y=hospi_by_pathology['nbr_hospi'],
                name="Nombre d'hospitalisations",
                marker_color=MAIN_COLOR,
                customdata=hospi_by_pathology[['nom_pathologie', 'nbr_hospi']],
                hovertemplate="<b>Pathologie:</b> %{customdata[0]}<br>" +
                            "<b>Hospitalisations:</b> %{customdata[1]:,.0f}<br><extra></extra>"
            ),
            secondary_y=False
        )

        # Ajout de la ligne pour la durée moyenne
        fig.add_trace(
            go.Scatter(
                x=hospi_by_pathology['nom_pathologie'],
                y=hospi_by_pathology['AVG_duree_hospi'],
                name="Durée moyenne de séjour",
                line=dict(color=SECONDARY_COLOR, width=2),
                mode='lines+markers',
                marker=dict(size=6),
                customdata=hospi_by_pathology[['nom_pathologie', 'AVG_duree_hospi']],
                hovertemplate="<b>Pathologie:</b> %{customdata[0]}<br>" +
                            "<b>Durée moyenne:</b> %{customdata[1]:.1f} jours<br><extra></extra>"
            ),
            secondary_y=True
        )

        # Mise à jour de la mise en page
        fig.update_layout(
            title=dict(
                text='Relation entre nombre d\'hospitalisations et durée moyenne de séjour',
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top'
            ),
            height=500,
            template='plotly_white',
            showlegend=False,
            margin=dict(t=100, b=50, l=50, r=50),  # Augmenter la marge du haut pour plus d'espace
        )

        # Mise à jour des titres des axes Y
        fig.update_yaxes(title_text="Nombre d'hospitalisations", secondary_y=False)
        fig.update_yaxes(title_text="Durée moyenne de séjour (jours)", secondary_y=True)

        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="", value="", help="Ce graphique montre la relation entre le nombre d'hospitalisations (barres) et la durée moyenne de séjour (ligne) pour les pathologies les plus fréquentes.")

        # Graphique combiné (scatter plot)
        # Fusion des données d'hospitalisation et de durée par année
        combined_data = pd.merge(
            df_nbr_hospi_filtered.groupby(['nom_pathologie', 'year'])['nbr_hospi'].sum().reset_index(),
            df_duree_hospi_filtered.groupby(['nom_pathologie', 'year'])['AVG_duree_hospi'].mean().reset_index(),
            on=['nom_pathologie', 'year']
        )
        
        # Filtrer pour garder seulement les n_pathologies plus fréquentes par année
        top_pathologies = df_nbr_hospi_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().nlargest(n_pathologies).index
        combined_data = combined_data[combined_data['nom_pathologie'].isin(top_pathologies)]

        # Création du scatter plot avec animation
        fig = px.scatter(
            combined_data,
            x='nbr_hospi',
            y='AVG_duree_hospi',
            text='nom_pathologie',
            animation_frame=combined_data['year'].dt.year,
            title=f'Relation entre nombre d\'hospitalisations et durée moyenne de séjour',
            labels={'nbr_hospi': 'Nombre d\'hospitalisations',
                   'AVG_duree_hospi': 'Durée moyenne de séjour (jours)',
                   'nom_pathologie': 'Pathologie'},
            size='nbr_hospi',
            size_max=40,
            color='AVG_duree_hospi',
            color_continuous_scale='Viridis',
            range_x=[0.1, combined_data['nbr_hospi'].max() * 1.1],  # Commencer à 0 pour l'axe des hospitalisations
            range_y=[0.5, combined_data['AVG_duree_hospi'].max() * 1.1]  # Commencer à 0 pour la durée moyenne
        )

        # Personnalisation du graphique
        fig.update_traces(
            textposition='top center',
            hovertemplate="<b>%{text}</b><br>" +
                         "Hospitalisations: %{x:,.0f}<br>" +
                         "Durée moyenne: %{y:.1f} jours<br>" +
                         "<extra></extra>"
        )

        # Mise à jour de la mise en page
        fig.update_layout(
            height=800,
            template='plotly_white',
            showlegend=False,
            margin=dict(t=100, b=100, l=100, r=150),
            annotations=[
                dict(
                    text="<b>Légende</b> : <br>La taille des points représente le nombre d'hospitalisations<br>La couleur indique la durée moyenne de séjour",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.8, y=1.1,
                    align="left",
                    xanchor="left"
                )
            ]
        )

        # Configuration de l'animation
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1500
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 500
        
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="", value="", help="Ce graphique animé montre l'évolution de la relation entre le nombre d'hospitalisations et la durée moyenne de séjour pour chaque pathologie au fil des années. La taille des bulles représente le nombre d'hospitalisations.")

        # Graphique 3D
        # Fusion des données avec les trois métriques
        combined_data_3d = pd.merge(
            df_nbr_hospi_filtered.groupby(['nom_pathologie', 'year'])['nbr_hospi'].sum().reset_index(),
            df_duree_hospi_filtered.groupby(['nom_pathologie', 'year'])['AVG_duree_hospi'].mean().reset_index(),
            on=['nom_pathologie', 'year']
        )
        combined_data_3d = pd.merge(
            combined_data_3d,
            df_tranche_age_hospi_filtered.groupby(['nom_pathologie', 'year'])['indice_comparatif_tt_age_percent'].mean().reset_index(),
            on=['nom_pathologie', 'year']
        )

        # Filtrer pour garder seulement les n_pathologies plus fréquentes
        top_pathologies = df_nbr_hospi_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().nlargest(n_pathologies).index
        combined_data_3d = combined_data_3d[combined_data_3d['nom_pathologie'].isin(top_pathologies)]

        # Création du graphique 3D avec animation
        fig = go.Figure()

        # Créer les frames pour l'animation avec interpolation
        frames = []
        years = sorted(combined_data_3d['year'].dt.year.unique())
        
        for i in range(len(years)):
            current_year = years[i]
            current_data = combined_data_3d[combined_data_3d['year'].dt.year == current_year].copy()
            
            # Nettoyer les valeurs NA
            current_data = current_data.dropna(subset=['nbr_hospi', 'AVG_duree_hospi', 'indice_comparatif_tt_age_percent'])
            
            # Ajouter la frame pour l'année actuelle
            frame = go.Frame(
                data=[go.Scatter3d(
                    x=current_data['nbr_hospi'].tolist(),
                    y=current_data['AVG_duree_hospi'].tolist(),
                    z=current_data['indice_comparatif_tt_age_percent'].tolist(),
                    mode='markers+text',
                    text=current_data['nom_pathologie'].tolist(),
                    textposition='top center',
                    marker=dict(
                        size=[x/current_data['nbr_hospi'].max()*30 for x in current_data['nbr_hospi']],
                        color=current_data['AVG_duree_hospi'].tolist(),
                        colorscale='Viridis',
                        opacity=0.8,
                        colorbar=dict(title="Durée moyenne de séjour (jours)")
                    ),
                    hovertemplate="<b>%{text}</b><br>" +
                                 f"Année: {current_year}<br>" +
                                 "Hospitalisations: %{x:,.0f}<br>" +
                                 "Durée moyenne: %{y:.1f} jours<br>" +
                                 "Indice comparatif: %{z:.1f}%<br>" +
                                 "<extra></extra>"
                )],
                name=str(current_year)
            )
            frames.append(frame)
            
            # Créer des frames intermédiaires si ce n'est pas la dernière année
            if i < len(years) - 1:
                next_year = years[i + 1]
                next_data = combined_data_3d[combined_data_3d['year'].dt.year == next_year].copy()
                next_data = next_data.dropna(subset=['nbr_hospi', 'AVG_duree_hospi', 'indice_comparatif_tt_age_percent'])
                
                # S'assurer que les données sont alignées
                common_pathologies = sorted(list(set(current_data['nom_pathologie']) & set(next_data['nom_pathologie'])))
                current_data = current_data[current_data['nom_pathologie'].isin(common_pathologies)].sort_values('nom_pathologie')
                next_data = next_data[next_data['nom_pathologie'].isin(common_pathologies)].sort_values('nom_pathologie')
                
                # Créer 5 frames intermédiaires entre chaque année
                for step in range(1, 6):
                    # Interpolation linéaire entre les années
                    alpha = step / 6.0
                    
                    # Calculer les valeurs interpolées
                    nbr_hospi = (current_data['nbr_hospi'].values * (1-alpha) + next_data['nbr_hospi'].values * alpha).tolist()
                    avg_duree = (current_data['AVG_duree_hospi'].values * (1-alpha) + next_data['AVG_duree_hospi'].values * alpha).tolist()
                    indice = (current_data['indice_comparatif_tt_age_percent'].values * (1-alpha) + next_data['indice_comparatif_tt_age_percent'].values * alpha).tolist()
                    
                    # Calculer la taille des points
                    max_hospi = max(nbr_hospi) if nbr_hospi else 1  # Éviter la division par zéro
                    point_sizes = [x/max_hospi*30 for x in nbr_hospi]
                    
                    frame = go.Frame(
                        data=[go.Scatter3d(
                            x=nbr_hospi,
                            y=avg_duree,
                            z=indice,
                            mode='markers+text',
                            text=current_data['nom_pathologie'].tolist(),
                            textposition='top center',
                            marker=dict(
                                size=point_sizes,
                                color=avg_duree,
                                colorscale='Viridis',
                                opacity=0.8,
                                colorbar=dict(title="Durée moyenne de séjour (jours)")
                            ),
                            hovertemplate="<b>%{text}</b><br>" +
                                         f"Transition {current_year}-{next_year}<br>" +
                                         "Hospitalisations: %{x:,.0f}<br>" +
                                         "Durée moyenne: %{y:.1f} jours<br>" +
                                         "Indice comparatif: %{z:.1f}%<br>" +
                                         "<extra></extra>"
                        )],
                        name=f"{current_year}_{step}"
                    )
                    frames.append(frame)
            
            # Ajouter la première année comme trace initiale
            if current_year == years[0]:
                fig.add_trace(frame.data[0])

        fig.frames = frames

        # Mise à jour des steps pour inclure uniquement les années principales
        steps = []
        for year in years:
            step = dict(
                method="animate",
                args=[[str(year)], {
                    "frame": {"duration": 300, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 300}
                }],
                label=str(year)
            )
            steps.append(step)

        sliders = [dict(
            active=0,
            currentvalue={"prefix": "Année: "},
            pad={"t": 50},
            steps=steps
        )]
        
        # Mise en page du graphique 3D
        fig.update_layout(
            title=dict(
                text='Évolution des pathologies selon trois dimensions clés',
                y=0.95,
                x=0.4,
                xanchor='right',
                yanchor='top'
            ),
            scene=dict(
                xaxis_title='Nombre d\'hospitalisations',
                yaxis_title='Durée moyenne de séjour (jours)',
                zaxis_title='Indice comparatif (%)',
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            height=800,
            template='plotly_white',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            width=800,
            sliders=sliders,
            annotations=[
                dict(
                    text="<b>Légende</b> : <br>La taille des points représente le nombre d'hospitalisations<br>La couleur indique la durée moyenne de séjour",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.8, y=1.1,
                    align="left",
                    xanchor="left"
                )
            ],
            margin=dict(t=100, b=50, l=50, r=50)  # Augmenter la marge du haut pour l'annotation
        )

        # Ajout de configuration pour une animation plus fluide
        fig.update_traces(
            hoverinfo="none",  # Désactiver temporairement le hover pendant l'animation
            customdata=combined_data_3d[['nom_pathologie', 'nbr_hospi', 'AVG_duree_hospi', 'indice_comparatif_tt_age_percent']].values,
        )
        
        # Ajout des boutons de contrôle pour l'animation
        fig.update_layout(
            updatemenus=[{
                "buttons": [
                    {
                        "args": [None, {
                            "frame": {"duration": 300, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": 300},
                            "mode": "immediate"
                        }],
                        "label": "Lecture",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {
                            "frame": {"duration": 0, "redraw": True},
                            "mode": "immediate",
                            "transition": {"duration": 0}
                        }],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.0,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }]
        )

        # Affichage du graphique
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="", value="", help="Ce graphique 3D montre la distribution des hospitalisations par pathologie, durée moyenne de séjour et indice comparatif. Utilisez les contrôles pour faire pivoter et zoomer sur le graphique.")

        # Tableau récapitulatif détaillé
        st.subheader("Évolution des pathologies (2018-2022)")
        
        # Calculer les évolutions année par année
        evolutions_by_year = {}
        years = sorted(df_nbr_hospi_filtered['year'].dt.year.unique())
        
        for i in range(len(years)-1):
            current_year = years[i]
            next_year = years[i+1]
            
            # Données pour l'année courante et suivante
            current_data = df_nbr_hospi_filtered[df_nbr_hospi_filtered['year'].dt.year == current_year].groupby('nom_pathologie')['nbr_hospi'].sum()
            next_data = df_nbr_hospi_filtered[df_nbr_hospi_filtered['year'].dt.year == next_year].groupby('nom_pathologie')['nbr_hospi'].sum()
            
            # Calculer l'évolution en pourcentage
            evolution = ((next_data - current_data) / current_data * 100).fillna(0)
            evolutions_by_year[f'{current_year}-{next_year}'] = evolution
        
        # Créer le DataFrame de base avec le nombre total d'hospitalisations
        df_summary = df_nbr_hospi_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().reset_index()
        
        # Ajouter les évolutions année par année
        for period, evolution in evolutions_by_year.items():
            df_summary = df_summary.merge(
                evolution.reset_index().rename(columns={'nbr_hospi': f'Evolution_{period}'}),
                on='nom_pathologie',
                how='left'
            )
        
        # Calculer l'évolution globale (2018-2022)
        hospi_2018 = df_nbr_hospi_filtered[df_nbr_hospi_filtered['year'].dt.year == 2018].groupby('nom_pathologie')['nbr_hospi'].sum()
        hospi_2022 = df_nbr_hospi_filtered[df_nbr_hospi_filtered['year'].dt.year == 2022].groupby('nom_pathologie')['nbr_hospi'].sum()
        evolution_globale = ((hospi_2022 - hospi_2018) / hospi_2018 * 100).fillna(0)
        
        # Ajouter l'évolution globale au DataFrame
        df_summary = df_summary.merge(
            evolution_globale.reset_index().rename(columns={'nbr_hospi': 'Evolution_globale'}),
            on='nom_pathologie',
            how='left'
        )
        
        # Trier par évolution globale décroissante
        df_summary = df_summary.sort_values('Evolution_globale', ascending=False)
        
        # Renommer les colonnes pour l'affichage
        df_summary.columns = ['Pathologie', 'Hospitalisations'] + [f'Évol. {period} (%)' for period in evolutions_by_year.keys()] + ['Évol. 2018-2022 (%)']
        
        # Colonnes d'évolution pour le gradient
        evolution_columns = ['Évol. 2018-2019 (%)', 'Évol. 2019-2020 (%)', 
                           'Évol. 2020-2021 (%)', 'Évol. 2021-2022 (%)', 
                           'Évol. 2018-2022 (%)']
        
        # Formater et afficher le tableau
        st.dataframe(
            df_summary.style.format({
                'Hospitalisations': '{:,.0f}',
                'Évol. 2018-2019 (%)': '{:+.1f}%',
                'Évol. 2019-2020 (%)': '{:+.1f}%',
                'Évol. 2020-2021 (%)': '{:+.1f}%',
                'Évol. 2021-2022 (%)': '{:+.1f}%',
                'Évol. 2018-2022 (%)': '{:+.1f}%'
            }).background_gradient(
                subset=evolution_columns,
                cmap='RdYlBu_r'
            ),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Deuxième tableau avec les baisses en premier
        st.subheader("Évolution des pathologies (2018-2022) - Baisses les plus importantes")
        
        # Utiliser le même DataFrame mais trié dans l'ordre inverse
        df_summary_desc = df_summary.sort_values('Évol. 2018-2022 (%)', ascending=True)
        
        # Afficher le deuxième tableau
        st.dataframe(
            df_summary_desc.style.format({
                'Hospitalisations': '{:,.0f}',
                'Évol. 2018-2019 (%)': '{:+.1f}%',
                'Évol. 2019-2020 (%)': '{:+.1f}%',
                'Évol. 2020-2021 (%)': '{:+.1f}%',
                'Évol. 2021-2022 (%)': '{:+.1f}%',
                'Évol. 2018-2022 (%)': '{:+.1f}%'
            }).background_gradient(
                subset=evolution_columns,
                cmap='RdYlBu_r'
            ),
            use_container_width=True
        )
        
    # Démographie
    with tab4:
        st.markdown("""
            <div class="insight-card">
            <h3>👥 Profil démographique</h3>
            <p>Analysez la répartition des hospitalisations par tranche d'âge et par territoire.
            Identifiez les besoins spécifiques de chaque groupe démographique.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Taux de recours par tranche d'âge
        age_groups = [
            'tranche_age_0_1', 'tranche_age_1_4', 'tranche_age_5_14',
            'tranche_age_15_24', 'tranche_age_25_34', 'tranche_age_35_44',
            'tranche_age_45_54', 'tranche_age_55_64', 'tranche_age_65_74',
            'tranche_age_75_84', 'tranche_age_85_et_plus'
        ]
        
        age_labels = {
            'tranche_age_0_1': '0-1 an',
            'tranche_age_1_4': '1-4 ans',
            'tranche_age_5_14': '5-14 ans',
            'tranche_age_15_24': '15-24 ans',
            'tranche_age_25_34': '25-34 ans',
            'tranche_age_35_44': '35-44 ans',
            'tranche_age_45_54': '45-54 ans',
            'tranche_age_55_64': '55-64 ans',
            'tranche_age_65_74': '65-74 ans',
            'tranche_age_75_84': '75-84 ans',
            'tranche_age_85_et_plus': '85 ans et plus'
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(" Distribution par tranche d'âge")
            
            # Optimisation du calcul de la moyenne pour les tranches d'âge
            age_means = []
            for col in age_groups:
                mean_value = df_tranche_age_hospi_filtered[col].mean()
                age_means.append({
                    'Tranche d\'âge': age_labels[col],
                    'Taux': mean_value
                })
            
            age_distribution = pd.DataFrame(age_means)
            
            fig = px.bar(age_distribution,
                        x='Tranche d\'âge',
                        y='Taux',
                        title='Distribution des hospitalisations par tranche d\'âge',
                        labels={'Taux': 'Taux d\'hospitalisation'},
                        custom_data=['Tranche d\'âge', 'Taux'])
            
            fig.update_traces(
                hovertemplate="<b>Tranche d'âge:</b> %{customdata[0]}<br>" +
                             "<b>Taux:</b> %{customdata[1]:.2f}%<br><extra></extra>",
                marker_color=MAIN_COLOR
            )
            fig.update_layout(height=500, template='plotly_white')
            col_chart, col_help = st.columns([1, 0.01])
            with col_chart:
                st.plotly_chart(fig, use_container_width=True)
            with col_help:
                st.metric(label="", value="", help="Ce graphique montre la distribution des hospitalisations par tranche d'âge. Les barres représentent le taux d'hospitalisation pour chaque groupe d'âge.")
        
        with col2:
            st.subheader(" Évolution des taux")
            
            # Calcul de l'évolution des taux standardisés
            evolution_taux = df_tranche_age_hospi_filtered.groupby('year').agg({
                'tx_standard_tt_age_pour_mille': 'mean',
                'tx_brut_tt_age_pour_mille': 'mean'
            }).reset_index()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=evolution_taux['year'],
                y=evolution_taux['tx_standard_tt_age_pour_mille'],
                name='Taux standardisé',
                line=dict(color=SECONDARY_COLOR, width=2),
                hovertemplate="<b>Date:</b> %{x|%Y}<br>" +
                             "<b>Taux standardisé:</b> %{y:.2f}‰<br><extra></extra>"
            ))
            
            fig.add_trace(go.Scatter(
                x=evolution_taux['year'],
                y=evolution_taux['tx_brut_tt_age_pour_mille'],
                name='Taux brut',
                line=dict(color=ACCENT_COLOR, width=2, dash='dash'),
                hovertemplate="<b>Date:</b> %{x|%Y}<br>" +
                             "<b>Taux brut:</b> %{y:.2f}‰<br><extra></extra>"
            ))
            
            fig.update_layout(
                title='Évolution des taux d\'hospitalisation',
                xaxis_title='Année',
                yaxis_title='Taux pour 1000 habitants',
                height=500,
                hovermode='x unified',
                template='plotly_white'
            )
            col_chart, col_help = st.columns([1, 0.01])
            with col_chart:
                st.plotly_chart(fig, use_container_width=True)
            with col_help:
                st.metric(label="", value="", help="Ce graphique montre l'évolution des taux d'hospitalisation au fil du temps. Il permet de comparer les tendances entre différentes régions ou services.")

        # Analyse régionale par tranche d'âge
        st.subheader(" Analyse territoriale par tranche d'âge")
        
        # Sélection du territoire
        territory_col = 'nom_region'
        territories = sorted(df_tranche_age_hospi_filtered[territory_col].unique())
        selected_territory = st.selectbox(
            f"Sélectionner un territoire", 
            territories
        )
        
        # Filtrage des données pour le territoire sélectionné
        territory_data = df_tranche_age_hospi_filtered[df_tranche_age_hospi_filtered[territory_col] == selected_territory]
        territory_age_data = territory_data[age_groups].mean().reset_index()
        territory_age_data.columns = ['Tranche d\'âge', 'Taux']
        territory_age_data['Tranche d\'âge'] = territory_age_data['Tranche d\'âge'].map(age_labels)
        
        fig = px.bar(territory_age_data,
                    x='Tranche d\'âge',
                    y='Taux',
                    title=f'Distribution par tranche d\'âge - {selected_territory}',
                    labels={'Taux': 'Taux d\'hospitalisation'},
                    custom_data=['Tranche d\'âge', 'Taux'])
        
        fig.update_traces(
            hovertemplate="<b>Tranche d'âge:</b> %{customdata[0]}<br>" +
                         "<b>Taux:</b> %{customdata[1]:.2f}%<br><extra></extra>",
            marker_color=MAIN_COLOR
        )
        fig.update_layout(height=500, template='plotly_white')
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="", value="", help="Ce graphique montre la distribution des hospitalisations par tranche d'âge pour le territoire sélectionné.")

        # Affichage des indicateurs clés
        col1, col2, col3 = st.columns(3)
        with col1:
            tx_brut = territory_data['tx_brut_tt_age_pour_mille'].mean()
            st.metric(
                "Taux brut",
                f"{tx_brut:.2f}‰"
            )
        
        with col2:
            tx_standard = territory_data['tx_standard_tt_age_pour_mille'].mean()
            st.metric(
                "Taux standardisé",
                f"{tx_standard:.2f}‰"
            )
        
        with col3:
            indice_comp = territory_data['indice_comparatif_tt_age_percent'].mean()
            st.metric(
                "Indice comparatif",
                f"{indice_comp:.1f}%"
            )

    @st.cache_data
    def prepare_hospi_data():
        hospi_columns = ['year', 'region', 'nom_region', 'pathologie', 'nom_pathologie', 'nbr_hospi']
        df_hospi = df_nbr_hospi[hospi_columns].copy()
        df_hospi['year'] = pd.to_datetime(df_hospi['year']).dt.date
        df_hospi['nbr_hospi'] = df_hospi['nbr_hospi'].astype('float32')
        return df_hospi

    @st.cache_data
    def prepare_duree_data():
        duree_columns = ['year', 'region', 'nom_region', 'pathologie', 'nom_pathologie', 'AVG_duree_hospi']
        df_duree = df_duree_hospi[duree_columns].copy()
        df_duree['year'] = pd.to_datetime(df_duree['year']).dt.date
        df_duree['AVG_duree_hospi'] = df_duree['AVG_duree_hospi'].astype('float32')
        return df_duree

    @st.cache_data
    def prepare_age_data():
        age_columns = ['year', 'region', 'nom_region', 'pathologie', 'nom_pathologie', 
                      'tx_brut_tt_age_pour_mille', 'tx_standard_tt_age_pour_mille']
        df_age = df_tranche_age_hospi[age_columns].copy()
        df_age['year'] = pd.to_datetime(df_age['year']).dt.date
        df_age['tx_brut_tt_age_pour_mille'] = df_age['tx_brut_tt_age_pour_mille'].astype('float32')
        df_age['tx_standard_tt_age_pour_mille'] = df_age['tx_standard_tt_age_pour_mille'].astype('float32')
        return df_age
        
    # Création d'un nouvel onglet pour l'analyse par service médical
    with tab5:
        st.markdown("""
            <div class="insight-card">
            <h3>🏥 Performance des services</h3>
            <p>Évaluez la performance des différents services médicaux à travers le temps.
            Analysez les tendances et les variations par spécialité.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Filtrer les données pour n'avoir que les totaux par service
        df_service = df_complet[df_complet['sexe'] == 'Ensemble'].copy()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sélection de l'année
            selected_year = st.selectbox(
                "Sélectionner l'année",
                sorted(df_service['annee'].unique()),
                key='service_year'
            )
        
        with col2:
            # Sélection de la région
            selected_region = st.selectbox(
                "Sélectionner la région",
                ['France entière'] + sorted(df_service['nom_region'].unique()),
                key='service_region'
            )
        
        # Filtrer les données selon les sélections
        mask = (df_service['annee'] == selected_year)
        if selected_region != 'France entière':
            mask &= (df_service['nom_region'] == selected_region)
        
        df_service_filtered = df_service[mask]
        
        # Création des groupes d'âge
        df_service_filtered['age_enfants'] = df_service_filtered[['tranche_age_0_1', 'tranche_age_1_4', 
            'tranche_age_5_14']].sum(axis=1)
        df_service_filtered['age_jeunes'] = df_service_filtered['tranche_age_15_24']
        df_service_filtered['age_adultes'] = df_service_filtered[['tranche_age_25_34', 
            'tranche_age_35_44']].sum(axis=1)
        df_service_filtered['age_seniors'] = df_service_filtered[['tranche_age_45_54', 
            'tranche_age_55_64']].sum(axis=1)
        df_service_filtered['age_ages'] = df_service_filtered[['tranche_age_65_74', 'tranche_age_75_84', 
            'tranche_age_85_et_plus']].sum(axis=1)

        # Création du dataframe pour les tranches d'âge regroupées
        age_groups = ['Enfants (0-14)', 'Jeunes (15-24)', 'Adultes (25-44)', 'Seniors (45-64)', 'Personnes âgées (65+)']
        df_age_grouped = df_service_filtered.groupby('classification').agg({
            'age_enfants': 'mean',
            'age_jeunes': 'mean',
            'age_adultes': 'mean',
            'age_seniors': 'mean',
            'age_ages': 'mean',
            'nbr_hospi': 'sum'
        }).reset_index()
        
        # Pie chart interactif
        fig_pie = px.pie(
            df_service_filtered.groupby('classification')['nbr_hospi'].sum().reset_index(),
            values='nbr_hospi',
            names='classification',
            title=f'Répartition des hospitalisations par service médical ({selected_year})',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(template='plotly_white')
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_help:
            st.metric(label="", value="", help=f"Ce graphique circulaire montre la répartition des hospitalisations entre les différents services médicaux pour l'année {selected_year}.")

        # Évolution temporelle par service
        df_evolution = df_service.groupby(['annee', 'classification'])['nbr_hospi'].sum().reset_index()
        
        fig_evolution = px.line(
            df_evolution,
            x='annee',
            y='nbr_hospi',
            color='classification',
            title='Évolution des hospitalisations par service médical',
            labels={'annee': 'Année', 'nbr_hospi': 'Nombre d\'hospitalisations', 'classification': 'Service'}
        )
        fig_evolution.update_layout(template='plotly_white')
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig_evolution, use_container_width=True)
        with col_help:
            st.metric(label="", value="", help="Ce graphique montre l'évolution du nombre d'hospitalisations pour chaque service médical au fil du temps.")

        # Heatmap des services par tranche d'âge
        age_columns = [col for col in df_service.columns if col.startswith('tranche_age_')]
        
        df_age_service = df_service_filtered.groupby('classification')[age_columns].mean().reset_index()
        df_age_service_melted = pd.melt(
            df_age_service,
            id_vars=['classification'],
            value_vars=age_columns,
            var_name='tranche_age',
            value_name='pourcentage'
        )
        
        # Nettoyer les noms des tranches d'âge
        df_age_service_melted['tranche_age'] = df_age_service_melted['tranche_age'].str.replace('tranche_age_', '')
        
        fig_heatmap = px.density_heatmap(
            df_age_service_melted,
            x='tranche_age',
            y='classification',
            z='pourcentage',
            title='Distribution des tranches d\'âge par service médical',
            labels={'tranche_age': 'Tranche d\'âge', 'classification': 'Service', 'pourcentage': 'Pourcentage'},
            color_continuous_scale='redor'
        )
        fig_heatmap.update_layout(xaxis_tickangle=-45, template='plotly_white')
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig_heatmap, use_container_width=True)
        with col_help:
            st.metric(label="", value="", help="Cette heatmap montre la distribution des tranches d'âge pour chaque service médical. Les couleurs plus foncées indiquent une plus forte concentration.")

        # Création d'une visualisation 3D plus pertinente
        st.subheader("Évolution des services médicaux dans le temps")

        # Préparation des données pour le graphique 3D
        df_evolution = df_service.groupby(['annee', 'classification', 'nom_region'])['nbr_hospi'].sum().reset_index()
        
        # Création du graphique 3D
        fig_3d = go.Figure()

        # Ajout d'une trace pour chaque service
        for service in df_evolution['classification'].unique():
            df_service_data = df_evolution[df_evolution['classification'] == service]
            
            fig_3d.add_trace(go.Scatter3d(
                x=df_service_data['annee'],
                y=df_service_data['nom_region'],
                z=df_service_data['nbr_hospi'],
                name=service,
                mode='markers',
                marker=dict(
                    size=6,
                    opacity=0.7
                ),
                hovertemplate=
                '<b>Service:</b> ' + service + '<br>' +
                '<b>Année:</b> %{x}<br>' +
                '<b>Région:</b> %{y}<br>' +
                '<b>Hospitalisations:</b> %{z:,.0f}<br>'
            ))

        # Mise en page du graphique 3D
        fig_3d.update_layout(
            title='Distribution des hospitalisations par service, année et région',
            scene=dict(
                xaxis_title='Année',
                yaxis_title='Région',
                zaxis_title='Nombre d\'hospitalisations',
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=2, y=2, z=1.5)
                )
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            width=800,
            height=600,
            template='plotly_white'
        )

        # Affichage du graphique
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig_3d, use_container_width=True)
        with col_help:
            st.metric(label="", value="", help="Ce graphique 3D montre la distribution des hospitalisations par service, année et région. Utilisez les contrôles pour faire pivoter et zoomer sur le graphique.")
        
        # Tableau récapitulatif simplifié
        st.subheader("Résumé par service médical")
        df_summary = df_service_filtered.groupby('classification').agg({
            'nbr_hospi': 'sum',
            'evolution_nbr_hospi': 'mean'
        }).reset_index()
        
        df_summary.columns = ['Service', 'Hospitalisations', 'Évolution (%)']
        st.dataframe(df_summary.style.format({
            'Hospitalisations': '{:,.0f}',
            'Évolution (%)': '{:+.1f}%'
        }))