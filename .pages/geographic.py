import streamlit as st
import plotly.express as px
import pandas as pd
import folium
import json

def show_geographic_analysis(df_nbr_hospi, df_duree_hospi, selected_years):
    st.subheader("🗺️ Distribution géographique")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique des hospitalisations par département
        hospi_by_departement = df_nbr_hospi.groupby('nom_departement')['nbr_hospi'].sum().reset_index()
        hospi_by_departement = hospi_by_departement.sort_values(by='nbr_hospi', ascending=True)
        
        fig = px.bar(hospi_by_departement, 
                    x='nbr_hospi', 
                    y='nom_departement',
                    orientation='h',
                    title="Nombre d'hospitalisations par département",
                    labels={'nbr_hospi': "Nombre d'hospitalisations", 
                           'nom_departement': 'Département'},
                    custom_data=['nom_departement', 'nbr_hospi'])
        
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
        # Graphique de la durée moyenne par département
        duree_by_departement = df_duree_hospi.groupby('nom_departement_region')['AVG_duree_hospi'].mean().reset_index()
        duree_by_departement = duree_by_departement.sort_values(by='AVG_duree_hospi', ascending=True)
        
        fig = px.bar(duree_by_departement, 
                    x='AVG_duree_hospi', 
                    y='nom_departement_region',
                    orientation='h',
                    title='Durée moyenne des hospitalisations par département',
                    labels={'AVG_duree_hospi': 'Durée moyenne (jours)', 
                           'nom_departement_region': 'Département'},
                    custom_data=['nom_departement_region', 'AVG_duree_hospi'])
        
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
