import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import pandas as pd
import plotly.express as px
from google.cloud import bigquery
import numpy as np

MAIN_COLOR = "#FF4B4B"

# Style CSS personnalisé
st.markdown("""
    <style>
    .main-title {
        color: #003366;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-align: center;
    }
    .section-title {
        color: #003366;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 1.5rem 0;
    }
    .card {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown("<h1 class='main-title' style='margin-top: -70px; margin-bottom: -8000px;'>🌍 Carte de France des hospitalisations</h1>", unsafe_allow_html=True)

# Fonction de chargement des données
@st.cache_resource
def load_data():
    try:
        # Chargement des secrets
        gcp_service_account = st.secrets["gcp_service_account"]
        client = bigquery.Client.from_service_account_info(gcp_service_account)
        
        # Chargement des données
        query = """
            SELECT *
            FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_sexe_population`
        """
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None

# Préparation des données pour la carte
@st.cache_data
def prepare_map_data(df_filtered, selected_service, niveau_administratif):

    # Filtrer par service si nécessaire
    if selected_service != 'Tous':
        df_filtered = df_filtered[df_filtered['classification'] == selected_service]
    
    # Filtrer par niveau administratif
    df_filtered = df_filtered[df_filtered['niveau'] == niveau_administratif]
    
    # Sélectionner la colonne appropriée selon le niveau administratif
    territory_col = 'region' if niveau_administratif == "Départements" else 'nom_region'
    
    # Correction du nom de l'Île-de-France
    if niveau_administratif == "Régions":
        df_filtered[territory_col] = df_filtered[territory_col].replace("Ile de France", "Île-de-France")
    
    # Agrégation des données par territoire
    hospi_by_territory = df_filtered.groupby(territory_col)['nbr_hospi'].sum().reset_index()
    
    # Formater les codes de département pour correspondre au GeoJSON
    if niveau_administratif == "Départements":
        hospi_by_territory[territory_col] = hospi_by_territory[territory_col].astype(str).str.extract('(\d+)')[0].str.zfill(2)
    
    # Création du dictionnaire pour la carte
    map_data = dict(zip(hospi_by_territory[territory_col], hospi_by_territory['nbr_hospi']))
    
    return map_data, df_filtered

def get_style_function(x):
    return {
        'fillColor': '#ffffff',
        'color': '#000000',
        'fillOpacity': 0.1,
        'weight': 0.1
    }

def get_highlight_function(x):
    return {
        'fillColor': '#000000',
        'color': '#000000',
        'fillOpacity': 0.50,
        'weight': 0.1
    }

def generate_map(map_data, geojson_data, niveau_administratif, df_filtered, sexe, annee, service):
    # Créer la carte de base
    m = folium.Map(location=[46.603354, 1.888334], zoom_start=6, tiles='Stadia.AlidadeSatellite')

    # Convertir les données en DataFrame pour Folium
    df_map = pd.DataFrame(list(map_data.items()), columns=['territoire', 'nbr_hospi'])
    
    # Pré-calcul des statistiques par territoire
    territory_col = 'region' if niveau_administratif == "Départements" else 'nom_region'
    
    # Créer une colonne de code formaté pour le filtrage
    if niveau_administratif == "Départements":
        df_filtered['code_territoire'] = df_filtered[territory_col].astype(str).str.extract('(\d+)')[0].str.zfill(2)
    else:
        df_filtered['code_territoire'] = df_filtered[territory_col]
    
    # Pré-calcul des durées moyennes (utilisant les données déjà filtrées)
    durees_moy = df_filtered.groupby('code_territoire')['AVG_duree_hospi'].mean()
    
    # Pré-calcul des top pathologies (utilisant les données déjà filtrées)
    top_patho_dict = {}
    for code, group in df_filtered.groupby('code_territoire'):
        top_patho = group.groupby('nom_pathologie')['nbr_hospi'].sum().nlargest(2)
        top_patho_text = "\n".join([f" {nom}: {val:,.0f} hospitalisations /" for nom, val in top_patho.items()])
        top_patho_dict[code] = top_patho_text
    
    # Ajouter la couche choropleth
    choropleth = folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=df_map,
        columns=['territoire', 'nbr_hospi'],
        key_on='feature.properties.nom' if niveau_administratif == "Régions" else 'feature.properties.code',
        fill_color='YlOrBr',
        fill_opacity=0.8,
        line_opacity=0.2,
        legend_name="Nombre d'hospitalisations",
        bins=14,
        nan_fill_color="white"
    ).add_to(m)
    
    # Ajouter les tooltips
    for feature in choropleth.geojson.data['features']:
        if niveau_administratif == "Régions":
            code = feature['properties']['nom']
        else:
            code = feature['properties']['code']
        nom = feature['properties']['nom']
        
        # Récupérer les statistiques pré-calculées
        nbr_hospi = map_data.get(code, 0)
        duree_moy = durees_moy.get(code, 0)
        top_patho_text = top_patho_dict.get(code, "Aucune donnée")
        
        # Créer un tooltip enrichi avec les informations de filtrage
        tooltip_html = f"""
        <div style='font-family: Arial; font-size: 12px;'>
            <b>{nom} {annee}</b><br>
            <b>Hospitalisations:</b> {nbr_hospi:,.0f}<br>
            <b>Durée moyenne de séjour:</b> {duree_moy:.1f} jours<br>
            <b>Pathologies les plus fréquentes:</b><br>
            {top_patho_text}
        </div>
        """
        
        # Créer un tooltip avec le HTML formaté
        tooltip = folium.Tooltip(tooltip_html)
        
        folium.GeoJson(
            feature,
            tooltip=tooltip,
            style_function=get_style_function,
            highlight_function=get_highlight_function
        ).add_to(m)
    
    return m

def show_map(df_filtered, niveau_administratif, selected_service, sexe, annee):
    st.markdown("""
        <div class="insight-card">
        <center><p>Explorez la carte interactive pour visualiser les données hospitalières par région.
        Naviguez à travers les différents niveaux administratifs pour une analyse détaillée.</p>
        </center></div>
    """, unsafe_allow_html=True)
    
    # Charger les GeoJSON appropriés selon le niveau administratif
    if niveau_administratif == "Régions":
        with open('data/regions-version-simplifiee.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)

    else:  # Département
        with open('data/departements-version-simplifiee.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
    
    # Préparer les données pour la carte
    map_data, filtered_df = prepare_map_data(df_filtered, selected_service, niveau_administratif)
    
    # Générer la carte
    m = generate_map(map_data, geojson_data, niveau_administratif, filtered_df, sexe, annee, selected_service)
    
    return m

# Chargement des données
df = load_data()

if df is not None:
    # Création de colonnes pour les filtres
    col1, col2, col3, = st.columns(3)
    
    with col1:
        # Sélection du niveau administratif
        niveau_administratif = st.selectbox(
            "Niveau administratif",
            ["Régions", "Départements"]
        )

    with col2:
        # Sélection du sexe
        sexe = st.selectbox(
            "Sexe",
            ["Ensemble", "Homme", "Femme"]
        )
    
    with col3:
        # Sélection de l'année
        years = sorted(df['year'].unique())
        years.insert(0, "Toutes les années")
        selected_year = st.selectbox("Année", years)
    
    # Filtrer les données
    if selected_year != "Toutes les années":
        df_filtered = df[df['year'] == selected_year]
    else:
        df_filtered = df.copy()
    
    if sexe != "Ensemble":
        df_filtered = df_filtered[df_filtered['sexe'] == sexe]
        
    col1, col2 = st.columns(2)
    
    with col1:
        # Sélection du service médical
        services_medicaux = {
            'Tous': 'Tous les services',
            'M': 'Médecine',
            'C': 'Chirurgie',
            'O': 'Obstétrique',
            'PSY': 'Psychiatrie',
            'SSR': 'Soins de suite et réadaptation',
            'ESND': 'Établissement de soin longue durée'
        }
        
        selected_service = st.selectbox(
            "Service médical",
            list(services_medicaux.keys()),
            format_func=lambda x: services_medicaux[x]
        )

    with col2:
        # Filtrer les pathologies en fonction du service sélectionné
        if selected_service != 'Tous':
            pathologies_df = df_filtered[df_filtered['classification'] == selected_service]
        else:
            pathologies_df = df_filtered

        # Liste déroulante des pathologies filtrées par service
        all_pathologies = sorted(pathologies_df['nom_pathologie'].unique())
        all_pathologies.insert(0, "Toutes les pathologies")
        selected_pathology = st.selectbox(
            "Pathologie",
            all_pathologies
        )

    # Appliquer le filtre de pathologie si nécessaire
    if selected_pathology != "Toutes les pathologies":
        df_filtered = df_filtered[df_filtered['nom_pathologie'] == selected_pathology]

    # Création des onglets après les filtres
    tab1= st.tabs([
        "🗺️ Zoom sur la France",
    ])

    with tab1:
        # Générer et afficher la carte
        m = show_map(df_filtered, niveau_administratif, selected_service, sexe, selected_year)
        
        # Afficher la carte
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st_folium(m, width=1200, height=800)
        with col_help:
            st.metric(
                label="help",
                value="",
                help="""Cette carte interactive vous permet de visualiser la distribution des hospitalisations en France.
                
                🔍 Navigation :
                - Zoomez avec la molette de la souris
                - Cliquez et faites glisser pour vous déplacer
                - Survolez une région pour voir les détails
                
                📊 Informations affichées :
                - Nombre total d'hospitalisations
                - Taux standardisé de recours
                
                🎨 Les couleurs plus foncées indiquent un nombre plus élevé d'hospitalisations."""
            )

    st.markdown("---")
    st.markdown("Développé avec 💫 par l'équipe JBN | Le Wagon - Promotion 2024")