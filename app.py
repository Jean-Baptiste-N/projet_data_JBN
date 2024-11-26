import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery


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
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
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
            SELECT * FROM `projet-jbn-data-le-wagon.morbidite_h.duree_hospi_dpt_intermediate`
        ''').to_dataframe()

        df_tranche_age_hospi = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.morbidite_h.tranche_age_hospi_dpt_intermediate`
        ''').to_dataframe()

        return df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, None

    except Exception as e:
        st.error(f"Erreur détaillée: {str(e)}")
        return None, None, None, str(e)

# Chargement des données avec spinner et gestion d'erreurs
with st.spinner('Chargement des données...'):
    df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, error = load_data()
    
    if error:
        st.error(f"Erreur lors du chargement des données: {error}")
        st.stop()

# Suite du code uniquement si les données sont chargées correctement
if df_nbr_hospi is not None:
    # Sidebar pour les filtres globaux
    st.sidebar.header("📊 Filtres")
    
    # Filtre années
    years = sorted(df_nbr_hospi['year'].unique())
    selected_years = st.sidebar.multiselect(
        "Sélectionner les années",
        years,
        default=years
    )
    
    # Filtre départements
    departments = sorted(df_nbr_hospi['nom_departement'].unique())
    selected_departments = st.sidebar.multiselect(
        "Sélectionner les départements",
        departments,
        default=departments[:5]
    )
    
    # Onglets principaux
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Vue Générale",
        "🗺️ Analyse Géographique",
        "🏥 Pathologies",
        "👥 Démographie"
    ])
    
        # Vue Générale
    with tab1:
        st.subheader("📊 Vue d'ensemble des données")
        
        # Affichage des valeurs manquantes
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("Valeurs manquantes - Hospitalisations:")
            st.write(df_nbr_hospi.isnull().sum())
        with col2:
            st.write("Valeurs manquantes - Durées:")
            st.write(df_duree_hospi.isnull().sum())
        with col3:
            st.write("Valeurs manquantes - Tranches d'âge:")
            st.write(df_tranche_age_hospi.isnull().sum())
        
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
            hospi_by_departement = df_nbr_hospi.groupby('nom_departement')['nbr_hospi'].sum().reset_index()
            hospi_by_departement = hospi_by_departement.sort_values(by='nbr_hospi', ascending=True)
            fig = px.bar(hospi_by_departement, x='nbr_hospi', y='nom_departement', 
                        title='Nombre d\'hospitalisations par département',
                        orientation='h')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            duree_by_departement = df_duree_hospi.groupby('nom_departement')['AVG_duree_hospi'].mean().reset_index()
            duree_by_departement = duree_by_departement.sort_values(by='AVG_duree_hospi', ascending=True)
            fig = px.bar(duree_by_departement, x='AVG_duree_hospi', y='nom_departement', 
                        title='Durée moyenne des hospitalisations par département',
                        orientation='h')
            st.plotly_chart(fig, use_container_width=True)

    # Pathologies
    with tab3:
        st.subheader("🏥 Analyse des pathologies")
        
        # Top pathologies par nombre d'hospitalisations
        hospi_by_pathology = df_nbr_hospi.groupby('nom_pathologie')['nbr_hospi'].sum().reset_index()
        hospi_by_pathology = hospi_by_pathology.sort_values(by='nbr_hospi', ascending=True)
        fig = px.bar(hospi_by_pathology.tail(20), x='nbr_hospi', y='nom_pathologie', 
                    title='Top 20 Pathologies par nombre d\'hospitalisations',
                    orientation='h')
        st.plotly_chart(fig, use_container_width=True)
        
        # Top pathologies par durée moyenne
        duree_by_pathology = df_duree_hospi.groupby('nom_pathologie')['AVG_duree_hospi'].mean().reset_index()
        duree_by_pathology = duree_by_pathology.sort_values(by='AVG_duree_hospi', ascending=True)
        fig = px.bar(duree_by_pathology.tail(20), x='AVG_duree_hospi', y='nom_pathologie', 
                    title='Top 20 Pathologies par durée moyenne de séjour',
                    orientation='h')
        st.plotly_chart(fig, use_container_width=True)
        
        # Indices comparatifs
        comparative_indices = df_tranche_age_hospi.groupby('nom_pathologie')['indice_comparatif_tt_age_percent'].mean().reset_index()
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
        
        recourse_by_age = df_tranche_age_hospi[age_groups].mean().reset_index()
        recourse_by_age.columns = ['Tranche d\'âge', 'Taux de recours']
        fig = px.bar(recourse_by_age, x='Taux de recours', y='Tranche d\'âge', 
                    title='Taux de recours par tranche d\'âge',
                    orientation='h')
        st.plotly_chart(fig, use_container_width=True)