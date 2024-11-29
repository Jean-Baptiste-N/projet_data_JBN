import streamlit as st
import folium
from streamlit_folium import st_folium
import json

def prepare_map_data(hospi_by_departement, hospi_by_region):
    dept_map_data = []
    for _, row in hospi_by_departement.iterrows():
        dept_map_data.append({
            'departement': row['nom_departement'],
            'nbr_hospi': row['nbr_hospi']
        })
    
    region_map_data = []
    for _, row in hospi_by_region.iterrows():
        region_map_data.append({
            'region': row['nom_region'],
            'nbr_hospi': row['nbr_hospi']
        })
    
    return dept_map_data, region_map_data

def generate_multi_level_map(dept_map_data, region_map_data, dept_geojson, region_geojson, selected_view):
    if selected_view == "Départements":
        m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
        
        choropleth = folium.Choropleth(
            geo_data=dept_geojson,
            name="choropleth",
            data=dept_map_data,
            columns=["departement", "nbr_hospi"],
            key_on="feature.properties.code",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Nombre d'hospitalisations"
        ).add_to(m)
        
        # Ajout des tooltips
        choropleth.geojson.add_child(
            folium.features.GeoJsonTooltip(["nom"], labels=False)
        )
        
    else:  # Vue par région
        m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
        
        choropleth = folium.Choropleth(
            geo_data=region_geojson,
            name="choropleth",
            data=region_map_data,
            columns=["region", "nbr_hospi"],
            key_on="feature.properties.nom",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Nombre d'hospitalisations"
        ).add_to(m)
        
        # Ajout des tooltips
        choropleth.geojson.add_child(
            folium.features.GeoJsonTooltip(["nom"], labels=False)
        )
    
    return m

def show_interactive_map(df_nbr_hospi):
    st.subheader("🗺️ Carte interactive des Hospitalisations")
    
    # Chargement des données géographiques
    with open("departements-version-simplifiee.geojson") as f:
        dept_geojson = json.load(f)
    
    with open("regions-version-simplifiee.geojson") as f:
        region_geojson = json.load(f)
    
    # Agrégation des données par département et région
    hospi_by_departement = df_nbr_hospi.groupby('nom_departement')['nbr_hospi'].sum().reset_index()
    hospi_by_region = df_nbr_hospi.groupby('nom_region')['nbr_hospi'].sum().reset_index()
    
    # Préparation des données pour la carte
    dept_map_data, region_map_data = prepare_map_data(hospi_by_departement, hospi_by_region)
    
    # Sélecteur de vue
    selected_view = st.radio(
        "Choisir le niveau de visualisation",
        ["Départements", "Régions"],
        horizontal=True
    )
    
    # Génération de la carte
    m = generate_multi_level_map(
        dept_map_data,
        region_map_data,
        dept_geojson,
        region_geojson,
        selected_view
    )
    
    # Affichage de la carte
    st_folium(m, width=1200, height=600)
