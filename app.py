import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
from streamlit_extras.metric_cards import style_metric_cards 
import time
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
    </style>
""", unsafe_allow_html=True)

# Titre principal
st.title("🏥 Dashboard d'Analyse Hospitalière")

# Fonction de chargement des données avec gestion d'erreurs
@st.cache_data
def load_data():
    try:
        # Chargement des secrets
        gcp_service_account = st.secrets["gcp_service_account"]

        # Initialisation du client BigQuery
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
            SELECT * FROM `projet-jbn-data-le-wagon.capacite_services_h.capacite_etablissement_intermediate_class`
        ''').to_dataframe()

        return df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, None

    except Exception as e:
        st.error(f"Erreur détaillée: {str(e)}")
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
    # Calcul des lits disponibles par année
    lits_disponibles = df_capacite_hospi.groupby('year')['total_lit_hospi_complete'].sum().reset_index()
    for year in range(2018, 2023):
        metrics[f"lits_{year}"] = lits_disponibles[lits_disponibles['year'] == year]['total_lit_hospi_complete'].sum()
    
    return metrics
    
placeholder = st.empty()
with st.spinner('Chargement des données...'):
    placeholder.image("ezgif.com-crop.gif", width=300)
    df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi, error = load_data()
    main_metrics = calculate_main_metrics(df_nbr_hospi, df_capacite_hospi)

    if error:
        st.error(f"Erreur lors du chargement des données: {error}")
        st.stop()

# Attendre 5 secondes avant de supprimer le GIF
time.sleep(5)
placeholder.empty()

# Calcul des métriques de la page principale

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Vue Générale",
        "🗺️ Analyse Géographique",
        "🏥 Pathologies",
        "👥 Démographie",
        "Carte Géographique"
    ])
    
    # Vue Générale
    with tab1:
        st.subheader("📊 Vue d'ensemble des données")
        
        # Affichage des valeurs manquantes
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric(
                label="Hospitalisations en 2018",
                value=f"{main_metrics['hospi_2018'] / 1_000_000:.2f}M",
                delta=None
            )
        with col2:
            value_2018 = main_metrics["hospi_2018"]
            value_2019 = main_metrics["hospi_2019"]
            delta_2019 = ((value_2019 - value_2018) / value_2018) * 100
            st.metric(
                label="Hospitalisations en 2019",
                value=f"{value_2019 / 1_000_000:.2f}M",
                delta=f"{delta_2019:.2f}%"
            )
        with col3:
            value_2019 = main_metrics["hospi_2019"]
            value_2020 = main_metrics["hospi_2020"]
            delta_2020 = ((value_2020 - value_2019) / value_2019) * 100
            st.metric(
                label="Hospitalisations en 2020",
                value=f"{value_2020 / 1_000_000:.2f}M",
                delta=f"{delta_2020:.2f}%"
            )
        with col4:
            value_2020 = main_metrics["hospi_2020"]
            value_2021 = main_metrics["hospi_2021"]
            delta_2021 = ((value_2021 - value_2020) / value_2020) * 100
            st.metric(
                label="Hospitalisations en 2021",
                value=f"{value_2021 / 1_000_000:.2f}M",
                delta=f"{delta_2021:.2f}%"
            )
        with col5:
            value_2021 = main_metrics["hospi_2021"]
            value_2022 = main_metrics["hospi_2022"]
            delta_2022 = ((value_2022 - value_2021) / value_2021) * 100
            st.metric(
                label="Hospitalisations en 2022",
                value=f"{value_2022 / 1_000_000:.2f}M",
                delta=f"{delta_2022:.2f}%"
            )
        style_metric_cards(background_color="#abc4f7")
        
        # Affichage des cartes de score pour les lits disponibles
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric(
                label="Lits disponibles en 2018",
                value=main_metrics["lits_2018"],
                delta=None
            )
        with col2:
            value_2018_lits = main_metrics["lits_2018"]
            value_2019_lits = main_metrics["lits_2019"]
            delta_2019_lits = ((value_2019_lits - value_2018_lits) / value_2018_lits) * 100
            st.metric(
                label="Lits disponibles en 2019",
                value=value_2019_lits,
                delta=f"{delta_2019_lits:.2f}%"
            )
        with col3:
            value_2020_lits = main_metrics["lits_2020"]
            delta_2020_lits = ((value_2020_lits - value_2019_lits) / value_2019_lits) * 100
            st.metric(
                label="Lits disponibles en 2020",
                value=value_2020_lits,
                delta=f"{delta_2020_lits:.2f}%"
            )
        with col4:
            value_2021_lits = main_metrics["lits_2021"]
            delta_2021_lits = ((value_2021_lits - value_2020_lits) / value_2020_lits) * 100
            st.metric(
                label="Lits disponibles en 2021",
                value=value_2021_lits,
                delta=f"{delta_2021_lits:.2f}%"
            )
        with col5:
            value_2022_lits = main_metrics["lits_2022"]
            delta_2022_lits = ((value_2022_lits - value_2021_lits) / value_2021_lits) * 100
            st.metric(
                label="Lits disponibles en 2022",
                value=value_2022_lits,
                delta=f"{delta_2022_lits:.2f}%"
            )
        # Tendances temporelles
        st.subheader("📈 Évolution temporelle")
        col1, col2 = st.columns(2)
        
        with col1:
            hospi_by_year = df_nbr_hospi.groupby('year')['nbr_hospi'].sum().reset_index()
            fig = px.line(hospi_by_year, x='year', y='nbr_hospi', 
                         title='Nombre d\'hospitalisations par année')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            duree_by_year = df_duree_hospi.groupby('year')['AVG_duree_hospi'].mean().reset_index()
            fig = px.line(duree_by_year, x='year', y='AVG_duree_hospi', 
                         title='Durée moyenne des hospitalisations par année')
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
                        orientation='h')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            duree_by_departement = df_duree_hospi_filtered.groupby('nom_departement_region')['AVG_duree_hospi'].mean().reset_index()
            duree_by_departement = duree_by_departement.sort_values(by='AVG_duree_hospi', ascending=True)
            fig = px.bar(duree_by_departement, x='AVG_duree_hospi', y='nom_departement_region', 
                        title='Durée moyenne des hospitalisations par département',
                        orientation='h')
            st.plotly_chart(fig, use_container_width=True)

    # Pathologies
    with tab3:
        st.subheader("🏥 Analyse des pathologies")
        
        # Top pathologies par nombre d'hospitalisations
        hospi_by_pathology = df_nbr_hospi_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().reset_index()
        hospi_by_pathology = hospi_by_pathology.sort_values(by='nbr_hospi', ascending=True)
        fig = px.bar(hospi_by_pathology.tail(20), x='nbr_hospi', y='nom_pathologie', 
                    title='Top 20 Pathologies par nombre d\'hospitalisations',
                    orientation='h')
        st.plotly_chart(fig, use_container_width=True)
        
        # Top pathologies par durée moyenne
        duree_by_pathology = df_duree_hospi_filtered.groupby('nom_pathologie')['AVG_duree_hospi'].mean().reset_index()
        duree_by_pathology = duree_by_pathology.sort_values(by='AVG_duree_hospi', ascending=True)
        fig = px.bar(duree_by_pathology.tail(20), x='AVG_duree_hospi', y='nom_pathologie', 
                    title='Top 20 Pathologies par durée moyenne de séjour',
                    orientation='h')
        st.plotly_chart(fig, use_container_width=True)
        
        # Indices comparatifs
        comparative_indices = df_tranche_age_hospi_filtered.groupby('nom_pathologie')['indice_comparatif_tt_age_percent'].mean().reset_index()
        comparative_indices = comparative_indices.sort_values(by='indice_comparatif_tt_age_percent', ascending=True)
        fig = px.bar(comparative_indices.tail(20), x='indice_comparatif_tt_age_percent', y='nom_pathologie', 
                    title='Top 20 Pathologies par indices comparatifs',
                    orientation='h')
        st.plotly_chart(fig, use_container_width=True)

    # Démographie
    with tab4:
        st.subheader("👥 Analyse démographique")
        
        # Taux de recours par tranche d'âge
        age_groups = ['tranche_age_1_4', 'tranche_age_5_14', 'tranche_age_15_24', 
                     'tranche_age_25_34', 'tranche_age_35_44', 'tranche_age_45_54', 
                     'tranche_age_55_64', 'tranche_age_65_74', 'tranche_age_75_84', 
                     'tranche_age_85_et_plus']
        
        recourse_by_age = df_tranche_age_hospi_filtered[age_groups].mean().reset_index()
        recourse_by_age.columns = ['Tranche d\'âge', 'Taux de recours']
        fig = px.bar(recourse_by_age, x='Taux de recours', y='Tranche d\'âge', 
                    title='Taux de recours par tranche d\'âge',
                    orientation='h')
        st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.subheader("🗺️ Carte des Hospitalisations par Département")

    # Préparation des données pour la carte
    # Exemple de données par département (ajustez selon vos données)
        hospi_by_departement = df_nbr_hospi_filtered.groupby('nom_departement')['nbr_hospi'].sum().reset_index()

    # Vous devez avoir les géolocalisations des départements sous forme de coordonnées ou de codes
    # Si vous avez des codes de département, vous pouvez les utiliser pour une carte choroplèthe

    # Exemple d'utilisation de `plotly.express.choropleth` pour afficher la carte
        fig = px.choropleth(
            hospi_by_departement,
            locations='nom_departement',  # Nom du département
            color='nbr_hospi',  # Nombre d'hospitalisations
            hover_name='nom_departement',  # Affichage du nom du département au survol
            color_continuous_scale="Viridis",  # Choix de la palette de couleurs
            labels={'nbr_hospi': 'Nombre d\'hospitalisations'},
            title="Répartition des hospitalisations par département"
        )

    # Afficher la carte
        st.plotly_chart(fig, use_container_width=True)