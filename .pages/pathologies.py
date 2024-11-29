import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def show_pathologies_analysis(df_nbr_hospi, df_duree_hospi):
    st.subheader("🏥 Analyse des pathologies")
        
    # Affichage des colonnes pour déboguer
    st.write("Colonnes disponibles dans df_duree_hospi:", df_duree_hospi.columns.tolist())
        
    # Ajout d'un sélecteur pour filtrer le nombre de pathologies à afficher
    n_pathologies = st.slider("Nombre de pathologies à afficher", 5, 50, 20)
    
    # Top pathologies par nombre d'hospitalisations
    hospi_by_pathology = df_nbr_hospi.groupby('nom_pathologie')['nbr_hospi'].sum().reset_index()
    hospi_by_pathology = hospi_by_pathology.sort_values(by='nbr_hospi', ascending=False).head(n_pathologies)
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
    duree_by_pathology = df_duree_hospi.groupby('nom_pathologie')['AVG_duree_hospi'].mean().reset_index()
    duree_by_pathology = duree_by_pathology.sort_values(by='AVG_duree_hospi', ascending=False).head(n_pathologies)
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