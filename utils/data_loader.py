import streamlit as st
from google.cloud import bigquery
import pandas as pd
import time

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