import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
from pygwalker.api.streamlit import StreamlitRenderer



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
        '''
        return client.query(query).to_dataframe()
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return None

# Chargement initial des données
df_main = load_data()

if df_main is not None:
    # Préparation des différents dataframes
    df_nbr_hospi = df_main.copy()
    df_duree_hospi = df_main.copy()
    df_tranche_age_hospi = df_main.copy()

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

    # Add Title
    st.markdown("<h1 class='main-title' style='margin-top: -70px;'>📊 Générateur de Graphiques</h1>", unsafe_allow_html=True)

    # Chargement progressif des données avec indicateur de progression
    with st.spinner("Chargement des données d'hospitalisation..."):
        df_hospi = prepare_hospi_data()
        
    with st.spinner("Chargement des données de durée de séjour..."):
        df_duree = prepare_duree_data()
        
    with st.spinner("Chargement des données par âge..."):
        df_age = prepare_age_data()

    if all(df is not None for df in [df_hospi, df_duree, df_age]):
        # Initialize PyGWalker with the loaded data
        walker = StreamlitRenderer(df_hospi, spec="./config.json", debug=False)
        walker.explorer()
        
        st.markdown("### 🎨 Personnalisation", unsafe_allow_html=True)
        
        st.markdown("### 📈 Visualisation", unsafe_allow_html=True)
        
        st.markdown("### 💾 Exportation", unsafe_allow_html=True)
        
        st.markdown("Développé avec 💫 par l'équipe JBN | Le Wagon - Promotion 2024")
    else:
        st.error("Erreur lors du chargement des données. Veuillez réessayer.")
else:
    st.error("Erreur lors du chargement des données initiales. Veuillez réessayer.")