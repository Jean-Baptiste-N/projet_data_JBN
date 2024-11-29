import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
from streamlit_extras.metric_cards import style_metric_cards 
import time
import folium
from streamlit_folium import st_folium
import json
from pygwalker.api.streamlit import StreamlitRenderer
import pygwalker as pyg



# Configuration de la page
st.set_page_config(
    page_title="Analyse Hospitalière",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #abc4f7;
        border-radius: 4px 4px 0px 0px;
        color: black;
    }
    .error-message {
        color: red;
        padding: 1rem;
        border: 1px solid red;
        border-radius: 4px;
    }
    .nav-button {
        background-color: #abc4f7;
        color: black;
        padding: 10px 20px;
        border-radius: 4px;
        text-decoration: none;
        margin: 5px;
        cursor: pointer;
        border: none;
    }
    .nav-button:hover {
        background-color: #8ba8e0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .back-to-top {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999;
        background-color: #abc4f7;
        color: black;
        padding: 10px;
        border-radius: 50%;
        text-decoration: none;
        display: none;
    }
    </style>
    <script>
    window.onscroll = function() {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            document.querySelector('.back-to-top').style.display = 'block';
        } else {
            document.querySelector('.back-to-top').style.display = 'none';
        }
    };
    </script>
""", unsafe_allow_html=True)

# Titre principal
st.title("🏥 Dashboard d'Analyse Hospitalière")

# Fonction de chargement des données avec gestion d'erreurs
@st.cache_resource
def fetch_data():
    try:
        # Chargement des secrets
        gcp_service_account = st.secrets["gcp_service_account"]
        client = bigquery.Client.from_service_account_info(gcp_service_account)
        
        # Chargement des datasets
        df_nbr_hospi = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.morbidite_h.nbr_hospi_intermediate`
        ''').to_dataframe()
        
        df_duree_hospi = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.duree_hospitalisation_par_patho.duree_hospi_region_et_dpt_clean_classifie`
        ''').to_dataframe()
        
        df_tranche_age_hospi = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.morbidite_h.tranche_age_intermediate`
        ''').to_dataframe()
        
        df_capacite_hospi = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.capacite_services_h.jointure_capa_hospi_dureehospi_KPIs`
        ''').to_dataframe()
        
        return df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, None

    except Exception as e:
        return None, None, None, None, str(e)

# Fonction pour calculer les métriques de la page principale
@st.cache_data
def calculate_main_metrics(df_nbr_hospi, df_capacite_hospi):
    metrics = {}
    
    # Calcul des hospitalisations par année
    for year in range(2018, 2023):
        total_hospi = df_nbr_hospi["nbr_hospi"][pd.to_datetime(df_nbr_hospi["year"]).dt.year == year].sum()
        metrics[f"hospi_{year}"] = total_hospi

    # Calcul des lits disponibles par année
    lits_disponibles = df_capacite_hospi.groupby('year')['total_lit_hospi_complete'].sum().reset_index()
    for year in range(2018, 2023):
        metrics[f"lits_{year}"] = lits_disponibles[lits_disponibles['year'] == year]['total_lit_hospi_complete'].sum()
    
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
        df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, error = fetch_data()
        
        if error:
            gif_placeholder.empty()
            progress_bar.empty()
            st.error(f"Erreur lors du chargement des données: {error}")
            st.stop()
        
        # Calcul des métriques
        progress_bar.progress(80, text="Calcul des métriques...")
        metrics = calculate_main_metrics(df_nbr_hospi, df_capacite_hospi)
        
        progress_bar.progress(100, text="Chargement terminé!")
        time.sleep(0.5)
        
        # Clear loading interface
        gif_placeholder.empty()
        progress_bar.empty()
        
        return df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, metrics
        
    except Exception as e:
        gif_placeholder.empty()
        progress_bar.empty()
        st.error(f"Erreur inattendue: {str(e)}")
        st.stop()

# Chargement des données avec interface de progression
df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, main_metrics = load_with_progress()

# Suite du code uniquement si les données sont chargées correctement
if df_nbr_hospi is not None:
    # Sidebar pour les filtres globaux
    st.sidebar.header("📊 Filtres")

    # Filtre années
    years = sorted(df_nbr_hospi['year'].unique())
    select_all_years = st.sidebar.checkbox("Sélectionner toutes les années", value=True)
    if select_all_years:
        selected_years = st.sidebar.multiselect("Sélectionner les années", years, default=years)
    else:
        selected_years = st.sidebar.multiselect("Sélectionner les années", years)

    # Filtre départements
    departments = sorted(df_nbr_hospi['nom_departement'].unique())
    select_all_departments = st.sidebar.checkbox("Sélectionner tous les départements", value=True)
    if select_all_departments:
        selected_departments = st.sidebar.multiselect("Sélectionner les départements", departments, default=departments)
    else:
        selected_departments = st.sidebar.multiselect("Sélectionner les départements", departments)

    # Appliquer les filtres aux DataFrames pour les onglets autres que "Vue Générale"
    df_nbr_hospi_filtered = df_nbr_hospi[df_nbr_hospi['year'].isin(selected_years) & df_nbr_hospi['nom_departement'].isin(selected_departments)]
    df_duree_hospi_filtered = df_duree_hospi[df_duree_hospi['year'].isin(selected_years) & df_duree_hospi['nom_departement_region'].isin(selected_departments)]
    df_tranche_age_hospi_filtered = df_tranche_age_hospi[df_tranche_age_hospi['year'].isin(selected_years) & df_tranche_age_hospi['nom_region'].isin(selected_departments)]
    df_capacite_hospi_filtered = df_capacite_hospi[df_capacite_hospi['year'].isin(selected_years) & df_capacite_hospi['nom_departement'].isin(selected_departments)]
    
    # Onglets principaux
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Vue Générale",
        "🗺️ Analyse Géographique",
        "🏥 Pathologies",
        "👥 Démographie",
        "Carte Géographique",
        "PYGWalker"
    ])
    
    # Vue Générale
    with tab1:
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

    # Analyse Géographique
    with tab2:
        st.subheader("🗺️ Distribution géographique")
        
        col1, col2 = st.columns(2)
        with col1:
            hospi_by_departement = df_nbr_hospi_filtered.groupby('nom_departement')['nbr_hospi'].sum().reset_index()
            hospi_by_departement = hospi_by_departement.sort_values(by='nbr_hospi', ascending=True)
            fig = px.bar(hospi_by_departement, x='nbr_hospi', y='nom_departement',
                        title='Nombre d\'hospitalisations par département',
                        labels={'nbr_hospi': 'Nombre d\'hospitalisations',
                               'nom_departement': 'Département'},
                        custom_data=['nom_departement', 'nbr_hospi'],
                        orientation='h')
            fig.update_traces(
                hovertemplate="<b>Département:</b> %{customdata[0]}<br>" +
                             "<b>Hospitalisations:</b> %{customdata[1]:,.0f}<br><extra></extra>",
                marker_color='#abc4f7'
            )
            fig.update_layout(
                hoverlabel=dict(bgcolor="white"),
                showlegend=False,
                height=800
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            duree_by_departement = df_duree_hospi_filtered.groupby('nom_departement_region')['AVG_duree_hospi'].mean().reset_index()
            duree_by_departement = duree_by_departement.sort_values(by='AVG_duree_hospi', ascending=True)
            fig = px.bar(duree_by_departement, x='AVG_duree_hospi', y='nom_departement_region',
                        title='Durée moyenne des hospitalisations par département',
                        labels={'AVG_duree_hospi': 'Durée moyenne (jours)',
                               'nom_departement_region': 'Département'},
                        custom_data=['nom_departement_region', 'AVG_duree_hospi'],
                        orientation='h')
            fig.update_traces(
                hovertemplate="<b>Département:</b> %{customdata[0]}<br>" +
                             "<b>Durée moyenne:</b> %{customdata[1]:.1f} jours<br><extra></extra>",
                marker_color='#abc4f7'
            )
            fig.update_layout(
                hoverlabel=dict(bgcolor="white"),
                showlegend=False,
                height=800
            )
            st.plotly_chart(fig, use_container_width=True)

    # Pathologies
    with tab3:
        st.subheader("🏥 Analyse des pathologies")
        
        # Ajout d'un sélecteur pour filtrer le nombre de pathologies à afficher
        n_pathologies = st.slider("Nombre de pathologies à afficher", 5, 50, 20)
        
        # Top pathologies par nombre d'hospitalisations
        hospi_by_pathology = df_nbr_hospi_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().reset_index()
        hospi_by_pathology = hospi_by_pathology.sort_values(by='nbr_hospi', ascending=True).tail(n_pathologies)
        fig = px.bar(hospi_by_pathology, x='nbr_hospi', y='nom_pathologie',
                    title=f'Top {n_pathologies} Pathologies par nombre d\'hospitalisations',
                    labels={'nbr_hospi': 'Nombre d\'hospitalisations',
                           'nom_pathologie': 'Pathologie'},
                    custom_data=['nom_pathologie', 'nbr_hospi'],
                    orientation='h')
        fig.update_traces(
            hovertemplate="<b>Pathologie:</b> %{customdata[0]}<br>" +
                         "<b>Hospitalisations:</b> %{customdata[1]:,.0f}<br><extra></extra>",
            marker_color='#abc4f7'
        )
        fig.update_layout(
            hoverlabel=dict(bgcolor="white"),
            showlegend=False,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top pathologies par durée moyenne
        duree_by_pathology = df_duree_hospi_filtered.groupby('nom_pathologie')['AVG_duree_hospi'].mean().reset_index()
        duree_by_pathology = duree_by_pathology.sort_values(by='AVG_duree_hospi', ascending=True).tail(n_pathologies)
        fig = px.bar(duree_by_pathology, x='AVG_duree_hospi', y='nom_pathologie',
                    title=f'Top {n_pathologies} Pathologies par durée moyenne de séjour',
                    labels={'AVG_duree_hospi': 'Durée moyenne (jours)',
                           'nom_pathologie': 'Pathologie'},
                    custom_data=['nom_pathologie', 'AVG_duree_hospi'],
                    orientation='h')
        fig.update_traces(
            hovertemplate="<b>Pathologie:</b> %{customdata[0]}<br>" +
                         "<b>Durée moyenne:</b> %{customdata[1]:.1f} jours<br><extra></extra>",
            marker_color='#abc4f7'
        )
        fig.update_layout(
            hoverlabel=dict(bgcolor="white"),
            showlegend=False,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Indices comparatifs avec recherche
        st.subheader("🔍 Recherche de pathologies spécifiques")
        search_term = st.text_input("Rechercher une pathologie", "")
        
        comparative_indices = df_tranche_age_hospi_filtered.groupby('nom_pathologie')['indice_comparatif_tt_age_percent'].mean().reset_index()
        if search_term:
            comparative_indices = comparative_indices[comparative_indices['nom_pathologie'].str.contains(search_term, case=False)]
        
        comparative_indices = comparative_indices.sort_values(by='indice_comparatif_tt_age_percent', ascending=True).tail(n_pathologies)
        fig = px.bar(comparative_indices, x='indice_comparatif_tt_age_percent', y='nom_pathologie',
                    title=f'Indices comparatifs des pathologies',
                    labels={'indice_comparatif_tt_age_percent': 'Indice comparatif (%)',
                           'nom_pathologie': 'Pathologie'},
                    custom_data=['nom_pathologie', 'indice_comparatif_tt_age_percent'],
                    orientation='h')
        fig.update_traces(
            hovertemplate="<b>Pathologie:</b> %{customdata[0]}<br>" +
                         "<b>Indice comparatif:</b> %{customdata[1]:.1f}%<br><extra></extra>",
            marker_color='#abc4f7'
        )
        fig.update_layout(
            hoverlabel=dict(bgcolor="white"),
            showlegend=False,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    # Démographie
    with tab4:
        st.subheader("👥 Analyse démographique")
        
        # Taux de recours par tranche d'âge
        age_groups = ['tranche_age_1_4', 'tranche_age_5_14', 'tranche_age_15_24', 
                     'tranche_age_25_34', 'tranche_age_35_44', 'tranche_age_45_54', 
                     'tranche_age_55_64', 'tranche_age_65_74', 'tranche_age_75_84', 
                     'tranche_age_85_et_plus']
        
        # Création d'un DataFrame plus lisible pour l'affichage
        age_labels = {
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
        
        recourse_by_age = df_tranche_age_hospi_filtered[age_groups].mean().reset_index()
        recourse_by_age.columns = ['Tranche d\'âge', 'Taux de recours']
        recourse_by_age['Tranche d\'âge'] = recourse_by_age['Tranche d\'âge'].map(age_labels)
        
        # Création du graphique avec des tooltips améliorés
        fig = px.bar(recourse_by_age, x='Taux de recours', y='Tranche d\'âge',
                    title='Taux de recours par tranche d\'âge',
                    labels={'Taux de recours': 'Taux de recours (pour 10 000 habitants)'},
                    custom_data=['Tranche d\'âge', 'Taux de recours'],
                    orientation='h')
        fig.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>" +
                         "Taux de recours: %{customdata[1]:.1f}<br><extra></extra>",
            marker_color='#abc4f7'
        )
        fig.update_layout(
            hoverlabel=dict(bgcolor="white"),
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse par région et tranche d'âge
        st.subheader("📊 Analyse régionale par tranche d'âge")
        
        # Sélection de la région
        regions = sorted(df_tranche_age_hospi_filtered['nom_region'].unique())
        selected_region = st.selectbox("Sélectionner une région", regions)
        
        # Filtrage des données pour la région sélectionnée
        region_data = df_tranche_age_hospi_filtered[df_tranche_age_hospi_filtered['nom_region'] == selected_region]
        region_age_data = region_data[age_groups].mean().reset_index()
        region_age_data.columns = ['Tranche d\'âge', 'Taux de recours']
        region_age_data['Tranche d\'âge'] = region_age_data['Tranche d\'âge'].map(age_labels)
        
        # Comparaison avec la moyenne nationale
        national_avg = df_tranche_age_hospi_filtered[age_groups].mean()
        region_age_data['Moyenne nationale'] = national_avg.values
        
        # Création du graphique de comparaison
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Région',
            x=region_age_data['Tranche d\'âge'],
            y=region_age_data['Taux de recours'],
            marker_color='#abc4f7'
        ))
        
        fig.add_trace(go.Bar(
            name='Moyenne nationale',
            x=region_age_data['Tranche d\'âge'],
            y=region_age_data['Moyenne nationale'],
            marker_color='rgba(171, 196, 247, 0.5)'
        ))
        
        fig.update_layout(
            title=f'Comparaison des taux de recours : {selected_region} vs Moyenne nationale',
            barmode='group',
            xaxis_tickangle=-45,
            height=600,
            hoverlabel=dict(bgcolor="white"),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    # Ajout du bouton "Retour en haut"
    st.markdown("""
        <a href="#" class="back-to-top">↑</a>
    """, unsafe_allow_html=True)

# Préparation des données pour la carte

@st.cache_data
def prepare_map_data(hospi_by_departement, hospi_by_region):
    # Prepare dictionaries for both department and region data
    dept_map_data = dict(zip(hospi_by_departement['nom_departement'], hospi_by_departement['nbr_hospi']))
    region_map_data = dict(zip(hospi_by_region['nom_region'], hospi_by_region['nbr_hospi']))
    return dept_map_data, region_map_data


def generate_multi_level_map(dept_map_data, region_map_data, dept_geojson, region_geojson, selected_view):
    # Création de la carte centrée sur la France
    france_map = folium.Map(location=[46.603354, 1.888334], zoom_start=5)

    if selected_view == "Régions":
        # Choropleth pour les régions
        region_choropleth = folium.Choropleth(
            geo_data=region_geojson,
            data=region_map_data,
            columns=['nom_region', 'nbr_hospi'],
            key_on="feature.properties.nom",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            line_weight=0.1,
            legend_name="Hospitalisations par région"
        ).add_to(france_map)

        # Ajout des tooltips pour les régions
        for feature in region_choropleth.geojson.data['features']:
            region_name = feature['properties']['nom']
            nbr_hospi = region_map_data.get(region_name, 0)
    
            tooltip = folium.Tooltip(f"{region_name}: {nbr_hospi} hospitalisations")
            folium.GeoJson(
                feature,
                tooltip=tooltip,
                style_function=lambda x: {
                'color': 'red',
                'weight': 0.5,
                'opacity': 0.2,
                'fillOpacity': 0
            }
            ).add_to(france_map)

    else:  # "Départements"
        # Choropleth pour les départements
        dept_choropleth = folium.Choropleth(
            geo_data=dept_geojson,
            data=dept_map_data,
            columns=['nom_departement', 'nbr_hospi'],
            key_on="feature.properties.nom",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            line_weight=0.1,
            legend_name="Hospitalisations par Département"
        ).add_to(france_map)

        # Ajout des tooltips pour les départements
        for feature in dept_choropleth.geojson.data['features']:
            dept_name = feature['properties']['nom']
            nbr_hospi = dept_map_data.get(dept_name, 0)
            tooltip = folium.Tooltip(f"{dept_name}: {nbr_hospi} hospitalisations")
            folium.GeoJson(
                feature,
                tooltip=tooltip,
                style_function=lambda x: {
                'color': 'blue',
                'weight': 0.5,
                'opacity': 0.2,
                'fillOpacity': 0
            }
            ).add_to(france_map)

    return france_map

# In the Carte Géographique tab
with tab5:
    st.subheader("🗺️ Carte interactive des Hospitalisations")
    
    # Ajout des boutons radio pour sélectionner le type d'affichage
    selected_view = st.radio(
        "Sélectionner le niveau géographique :",
        ["Régions", "Départements"],
        horizontal=True
    )
    
    # Préparation des données pour la carte
    hospi_by_departement = df_capacite_hospi_filtered.groupby('nom_departement')['nbr_hospi'].sum().reset_index()
    hospi_by_region = df_capacite_hospi_filtered.groupby('nom_region')['nbr_hospi'].sum().reset_index()
    
    # Chargement des GeoJSON
    with open("departements-version-simplifiee.geojson", "r", encoding="utf-8") as f:
        dept_geojson = json.load(f)
    
    with open("regions-version-simplifiee.geojson", "r", encoding="utf-8") as f:
        region_geojson = json.load(f)
    
    # Préparer les données de la carte
    dept_map_data, region_map_data = prepare_map_data(hospi_by_departement, hospi_by_region)
    
    # Génération de la carte avec le niveau sélectionné
    france_map = generate_multi_level_map(dept_map_data, region_map_data, dept_geojson, region_geojson, selected_view)
    st_data = st_folium(france_map, width=800, height=600)
    
    # Ajout du bouton "Retour en haut"
    st.markdown("""
        <a href="#" class="back-to-top">↑</a>
    """, unsafe_allow_html=True)

# In the PYGWalker tab
@st.cache_data
def prepare_pygwalker_data():
    # Premier DataFrame
    df_hospi = df_nbr_hospi_filtered.copy()
    if 'year' in df_hospi.columns:
        df_hospi['year'] = pd.to_datetime(df_hospi['year'])
    
    # Deuxième DataFrame
    df_duree = df_duree_hospi.copy()
    if 'year' in df_duree.columns:
        df_duree['year'] = pd.to_datetime(df_duree['year'])
        
    # Troisième DataFrame
    df_age = df_tranche_age_hospi.copy()
    if 'year' in df_age.columns:
        df_age['year'] = pd.to_datetime(df_age['year'])
    
    return df_hospi, df_duree, df_age

with tab6:
    # Add Title
    st.title("Analyse Interactive des Données")
    
    # Get cached data
    df_hospi, df_duree, df_age = prepare_pygwalker_data()
    
    # Create tabs for different datasets
    hospi_tab, duree_tab, age_tab = st.tabs(["Hospitalisations", "Durée de séjour", "Tranches d'âge"])
    
    with hospi_tab:
        st.subheader("Analyse des hospitalisations")
        pyg_hospi = StreamlitRenderer(df_hospi, spec="./gw_hospi.json")
        pyg_hospi.explorer()
    
    with duree_tab:
        st.subheader("Analyse des durées de séjour")
        pyg_duree = StreamlitRenderer(df_duree, spec="./gw_duree.json")
        pyg_duree.explorer()
    
    with age_tab:
        st.subheader("Analyse par tranches d'âge")
        pyg_age = StreamlitRenderer(df_age, spec="./gw_age.json")
        pyg_age.explorer()
