import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery


# Définition des couleurs du thème
MAIN_COLOR = '#003366'  # Bleu marine principal
SECONDARY_COLOR = '#AFDC8F'  # Vert clair complémentaire
ACCENT_COLOR = '#3D7317'  # Vert foncé pour les accents

# Style CSS personnalisé
st.markdown ("""
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
st.markdown("<h1 class='main-title' style='margin-top: -70px; margin-bottom: -8000px;'>🏥 Focus sur la Médecine</h1>", unsafe_allow_html=True)


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
            FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_population`
            WHERE classification = 'M'
        """
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error (f"Erreur lors du chargement des données : {str(e)}")
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
            key="niveau_administratif_med"
        )

    with col2:
        # Sélection du sexe
        selected_sex = st.selectbox(
            "Sexe",
            ["Ensemble", "Homme", "Femme"],
            key="selecteur_sexe_med"
        )

    with col3:
        # Filtre années avec une liste déroulante simple
        years = sorted(df['annee'].unique(), reverse=True)
        years_options = ["Toutes les années"] + [str(year) for year in years]
        selected_year = st.selectbox(
            "Année", 
            years_options, 
            key="year_filter_med"
        )
    
    # Filtrage des données selon les sélections
    df_filtered = df.copy()
    
    # Filtre par sexe
    df_filtered = df_filtered[df_filtered['sexe'] == selected_sex]
    
    # Filtre par année si nécessaire
    if selected_year != "Toutes les années":
        df_filtered = df_filtered[df_filtered['annee'] == int(selected_year)]

    # Affichage des métriques clés
    st.subheader("Statistiques clés")
    col1, col2, col3, col_help = st.columns([1, 1, 1, 0.01])
    
    with col1:
        total_hospi = df_filtered['nbr_hospi'].sum()
        st.metric("Total des hospitalisations", f"{total_hospi:,.0f}")
    
    with col2:
        avg_duration = df_filtered['AVG_duree_hospi'].mean()
        st.metric("Durée moyenne d'hospitalisation", f"{avg_duration:.1f} jours")
    
    with col3:
        evolution = df_filtered['evolution_percent_nbr_hospi'].mean()
        st.metric("Évolution moyenne", f"{evolution:+.1f}%")
    
    with col_help:
        st.metric(
            label="",
            value="",
            help="""📊 Ces métriques clés résument les données de médecine :
            
            - Total des hospitalisations : nombre total de patients hospitalisés
            - Durée moyenne : temps moyen passé à l'hôpital
            - Évolution : changement en pourcentage par rapport à la période précédente"""
        )
        
    # Préparation des données pour le graphique 3D
    group_cols = ['annee']
    location_label = 'Région' if niveau_administratif == "Régions" else 'Département'
    
    if niveau_administratif == "Régions":
        df_filtered['location_name'] = df_filtered['nom_region']
    else:
        df_filtered['location_name'] = df_filtered['nom_region']
        
    group_cols.append('location_name')
    df_evolution = df_filtered.groupby(group_cols)['nbr_hospi'].sum().reset_index()
    
    # Création du graphique 3D
    fig_3d = go.Figure(data=[go.Scatter3d(
        x=df_evolution['annee'],
        y=df_evolution['location_name'],
        z=df_evolution['nbr_hospi'],
        mode='markers',
        marker=dict(
            size=10,
            color=pd.Categorical(df_evolution['location_name']).codes,
            colorscale='Turbo',
            opacity=0.8,
            showscale=False
        ),
        hovertemplate=
        f'<b>{location_label}:</b> %{{y}}<br>' +
        '<b>Année:</b> %{x}<br>' +
        '<b>Hospitalisations:</b> %{z:,.0f}<br>'
    )])

    # Mise en page du graphique 3D
    fig_3d.update_layout(
        title=f'Évolution des hospitalisations en Médecine par {location_label.lower()}',
        scene=dict(
            xaxis_title='Année',
            yaxis_title=location_label,
            zaxis=dict(
                title='Nombre d\'hospitalisations',
                type='log',
                exponentformat='none'
            ),
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=2.5, y=2.5, z=2)
            )
        ),
        width=1000,
        height=1000
    )

    # Affichage du graphique
    col_chart, col_help = st.columns([1, 0.01])
    with col_chart:
        st.plotly_chart(fig_3d, use_container_width=True)
    with col_help:
        st.metric(
            label="",
            value="",
            help="""🔍 Ce graphique 3D montre l'évolution des hospitalisations en médecine :
            
            Navigation :
            - Utilisez la souris pour faire pivoter le graphique
            - Double-cliquez pour réinitialiser la vue
            - Survolez les points pour voir les détails
            
            Axes :
            - X : Année
            - Y : Région/Département
            - Z : Nombre d'hospitalisations (échelle logarithmique)
            
            Les couleurs différentes représentent les différentes régions/départements."""
        )

else:
    st.error("Impossible de charger les données. Veuillez réessayer plus tard.")