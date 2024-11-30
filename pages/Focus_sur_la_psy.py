import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery

# Configuration de la page
st.set_page_config(
    page_title="Focus sur la Psychiatrie",
    page_icon="🏥",
    layout="wide"
)

# Titre de la page
st.title("Focus sur la Psychiatrie")

# Fonction de chargement des données
@st.cache_resource
def load_data():
    try:
        # Chargement des secrets
        gcp_service_account = st.secrets["gcp_service_account"]
        client = bigquery.Client.from_service_account_info(gcp_service_account)
        
        # Chargement des données
        query = '''
            SELECT *
            FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_population`
            WHERE classification = 'PSY'
        '''
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None

# Chargement des données
df = load_data()

if df is not None:
    # Filtres principaux en colonnes
    col1, col2, col3 = st.columns(3)

    with col1:
        # Sélection du niveau administratif
        niveau_administratif = st.selectbox(
            "Niveau administratif",
            ["Régions", "Départements"],
            key="niveau_administratif_psy"
        )

    with col2:
        # Sélection du sexe
        selected_sex = st.selectbox(
            "Sexe",
            ["Ensemble", "Homme", "Femme"],
            key="selecteur_sexe_psy"
        )

    with col3:
        # Filtre années avec une liste déroulante simple
        years = sorted(df['annee'].unique(), reverse=True)
        years_options = ["Toutes les années"] + [str(year) for year in years]
        selected_year = st.selectbox(
            "Année", 
            years_options, 
            key="year_filter_psy"
        )
    
    # Filtrage des données selon les sélections
    df_filtered = df.copy()
    
    # Filtre par sexe
    if selected_sex != "Ensemble":
        df_filtered = df_filtered[df_filtered['sexe'] == selected_sex]
    
    # Filtre par année si nécessaire
    if selected_year != "Toutes les années":
        df_filtered = df_filtered[df_filtered['annee'] == int(selected_year)]

    # Affichage des métriques clés
    st.subheader("Statistiques clés")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_hospi = df_filtered['nbr_hospi'].sum()
        st.metric("Total des hospitalisations", f"{total_hospi:,.0f}")
    
    with col2:
        avg_duration = df_filtered['AVG_duree_hospi'].mean()
        st.metric("Durée moyenne d'hospitalisation", f"{avg_duration:.1f} jours")
    
    with col3:
        evolution = df_filtered['evolution_percent_nbr_hospi'].mean()
        st.metric("Évolution moyenne", f"{evolution:+.1f}%")

else:
    st.error("Impossible de charger les données. Veuillez réessayer plus tard.")