import streamlit as st
from utils.data_loader import fetch_data, calculate_main_metrics, load_with_progress
from pages.geographic import show_geographic_analysis
from pages.pathologies import show_pathologies_analysis
from pages.demographics import show_demographics_analysis
from pages.interactive_map import show_interactive_map
from pages.interactive_analysis import show_interactive_analysis
from pages.ai_assistant import show_ai_assistant
from styles.main import load_css

# Configuration de la page
st.set_page_config(
    page_title="Analyse Hospitalière",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chargement du CSS
st.markdown(load_css(), unsafe_allow_html=True)

# Titre principal
st.title("🏥 Dashboard d'Analyse Hospitalière")

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
        selected_years = years
    else:
        selected_years = st.sidebar.multiselect("Sélectionner les années", years, default=[years[-1]])
        if not selected_years:  # Si aucune année n'est sélectionnée
            selected_years = [years[-1]]  # Sélectionner la dernière année par défaut

    # Filtre région
    regions = sorted(df_capacite_hospi['nom_region'].unique())
    select_all_regions = st.sidebar.checkbox("Sélectionner toutes les régions", value=True)
    if select_all_regions:
        selected_regions = regions
    else:
        selected_regions = st.sidebar.multiselect("Sélectionner les régions", regions)
        if not selected_regions:  # Si aucune région n'est sélectionnée
            selected_regions = [regions[0]]  # Sélectionner la première région par défaut

    # Filtre départements
    departments = sorted(df_nbr_hospi['nom_departement'].unique())
    select_all_departments = st.sidebar.checkbox("Sélectionner tous les départements", value=True)
    if select_all_departments:
        selected_departments = departments
    else:
        selected_departments = st.sidebar.multiselect("Sélectionner les départements", departments)
        if not selected_departments:  # Si aucun département n'est sélectionné
            selected_departments = [departments[0]]  # Sélectionner le premier département par défaut

    # Appliquer les filtres aux DataFrames
    df_nbr_hospi_filtered = df_nbr_hospi[
        df_nbr_hospi['year'].isin(selected_years) & 
        df_nbr_hospi['nom_departement'].isin(selected_departments)
    ]
    
    df_duree_hospi_filtered = df_duree_hospi[
        df_duree_hospi['year'].isin(selected_years) & 
        df_duree_hospi['nom_departement_region'].isin(selected_departments)
    ]
    
    df_tranche_age_hospi_filtered = df_tranche_age_hospi[
        df_tranche_age_hospi['year'].isin(selected_years) & 
        df_tranche_age_hospi['nom_region'].isin(selected_regions)
    ]
    
    df_capacite_hospi_filtered = df_capacite_hospi[
        df_capacite_hospi['year'].isin(selected_years) & 
        df_capacite_hospi['nom_departement'].isin(selected_departments)
    ]

    # Création des onglets
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Vue Générale",
        "🗺️ Analyse Géographique",
        "🏥 Pathologies",
        "👥 Démographie",
        "Carte Géographique",
        "PYGWalker",
        "Docteur"
    ])

    # Contenu des onglets
    with tab1:
        from pages.overview import show_overview
        show_overview(df_nbr_hospi_filtered, df_duree_hospi_filtered, main_metrics)

    with tab2:
        show_geographic_analysis(df_nbr_hospi_filtered, df_duree_hospi_filtered, selected_years)

    with tab3:
        show_pathologies_analysis(df_nbr_hospi_filtered, df_duree_hospi_filtered)

    with tab4:
        show_demographics_analysis(df_tranche_age_hospi_filtered)

    with tab5:
        show_interactive_map(df_nbr_hospi_filtered)

    with tab6:
        show_interactive_analysis(df_nbr_hospi_filtered, df_duree_hospi_filtered, df_tranche_age_hospi_filtered, df_capacite_hospi_filtered)

    with tab7:
        show_ai_assistant(df_nbr_hospi_filtered, df_duree_hospi_filtered, df_tranche_age_hospi_filtered, df_capacite_hospi_filtered)
