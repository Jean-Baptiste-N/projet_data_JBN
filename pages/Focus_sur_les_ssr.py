import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from google.cloud import bigquery

# Définition des couleurs du thème
MAIN_COLOR = '#003366'  # Bleu marine principal
SECONDARY_COLOR = '#AFDC8F'  # Vert clair complémentaire
ACCENT_COLOR = '#3D7317'  # Vert foncé pour les accents

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
st.markdown("<h1 class='main-title' style='margin-top: -70px;'>♿ Service SSR (Soins de santé et de réhabilitation)</h1>", unsafe_allow_html=True)

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
            WHERE classification = 'SSR'
        """
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None

# Chargement des données
df = load_data()

if df is not None:
    # Filtres principaux en colonnes
    col1, col2 = st.columns(2)

    with col1:
        # Sélection du sexe
        selected_sex = st.selectbox(
            "Sexe",
            ["Ensemble", "Femme"],
            key="selecteur_sexe_ssr"
        )

    with col2:
        # Filtre années avec une liste déroulante simple
        years = sorted(df['annee'].unique(), reverse=True)
        years_options = ["Toutes les années"] + [str(year) for year in years]
        selected_year = st.selectbox(
            "Année", 
            years_options, 
            key="year_filter_ssr"
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
            label="help",
            value="",
            help="""📊 Ces métriques clés résument les données psychiatriques :
            
            - Total des hospitalisations : nombre total d'hospitalisations en psychiatrie
            - Durée moyenne : temps moyen de séjour en service psychiatrique
            - Évolution : tendance des hospitalisations psychiatriques par rapport à la période précédente
            
            Note : Les durées de séjour en psychiatrie sont généralement plus longues que dans les autres services."""
        )
    st.divider()

    # Système de recherche avec autocomplétion
    all_pathologies = sorted(df_filtered['nom_pathologie'].unique())
    search_term = st.text_input("🔍 Rechercher une pathologie en SSR pour obtenir des détails", "")
    
    # Filtrer et suggérer les pathologies pendant la saisie
    if search_term:
        filtered_pathologies = [path for path in all_pathologies if search_term.lower() in path.lower()]
        if filtered_pathologies:
            selected_pathology = st.selectbox(
                "Sélectionner une pathologie dans les suggestions",
                filtered_pathologies,
                key="pathology_selector_ssr"
            )
            
            # Afficher les données pour la pathologie sélectionnée
            path_data = df_filtered[df_filtered['nom_pathologie'] == selected_pathology]
            total_hospi = path_data['nbr_hospi'].sum()
            avg_duration = path_data['AVG_duree_hospi'].mean()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Nombre total de séjours en SSR", f"{total_hospi:,.0f}")
            with col2:
                st.metric("Durée moyenne de séjour", f"{avg_duration:.1f} jours")
        else:
            st.warning("Aucune pathologie trouvée avec ce terme de recherche.")

    # Affichage des métriques clés
    st.subheader("📊 Indicateurs clés")
    col1, col2, col3, col_help = st.columns([1, 1, 1, 0.01])
    
    with col1:
        total_hospi = df_filtered['nbr_hospi'].sum()
        st.metric("Total des séjours", f"{total_hospi:,.0f}")
    
    with col2:
        avg_duration = df_filtered['AVG_duree_hospi'].mean()
        st.metric("Durée moyenne de séjour", f"{avg_duration:.1f} jours")
    
    with col3:
        evolution = df_filtered['evolution_percent_nbr_hospi'].mean()
        st.metric("Évolution moyenne", f"{evolution:+.1f}%")

    with col_help:
        st.metric(
            label="help",
            value="",
            help="""📊 Ces métriques clés résument les données SSR :
            
            - Total des séjours : nombre total de séjours en Soins de Suite et de Réadaptation
            - Durée moyenne : temps moyen de séjour en SSR
            - Évolution : tendance des séjours SSR par rapport à la période précédente
            
            Note : Les SSR sont caractérisés par des durées de séjour plus longues, adaptées à la rééducation et à la réadaptation."""
        )

    st.divider()
    
    # Ajout d'un sélecteur pour filtrer le nombre de pathologies à afficher
    n_pathologies = st.slider("Nombre de pathologies à afficher", 3, 6, 6)
    
    # Top pathologies par nombre d'hospitalisations
    hospi_by_pathology = df_filtered.groupby('nom_pathologie').agg({
        'nbr_hospi': 'sum',
        'AVG_duree_hospi': 'mean'
    }).reset_index()
    
    hospi_by_pathology = hospi_by_pathology.sort_values(by='nbr_hospi', ascending=False).head(n_pathologies)

    # Création d'une figure avec deux axes Y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Ajout des barres pour le nombre d'hospitalisations
    fig.add_trace(
        go.Bar(
            x=hospi_by_pathology['nom_pathologie'],
            y=hospi_by_pathology['nbr_hospi'],
            name="Nombre de séjours",
            marker_color=MAIN_COLOR,
            customdata=hospi_by_pathology[['nom_pathologie', 'nbr_hospi']],
            hovertemplate="<b>Pathologie:</b> %{customdata[0]}<br>" +
                        "<b>Séjours:</b> %{customdata[1]:,.0f}<br><extra></extra>"
        ),
        secondary_y=False
    )

    # Ajout de la ligne pour la durée moyenne
    fig.add_trace(
        go.Scatter(
            x=hospi_by_pathology['nom_pathologie'],
            y=hospi_by_pathology['AVG_duree_hospi'],
            name="Durée moyenne de séjour",
            line=dict(color=SECONDARY_COLOR, width=2),
            mode='lines+markers',
            marker=dict(size=6),
            customdata=hospi_by_pathology[['nom_pathologie', 'AVG_duree_hospi']],
            hovertemplate="<b>Pathologie:</b> %{customdata[0]}<br>" +
                        "<b>Durée moyenne:</b> %{customdata[1]:.1f} jours<br><extra></extra>"
        ),
        secondary_y=True
    )

    # Mise à jour de la mise en page
    fig.update_layout(
        title=dict(
            text='Pathologies en SSR : Séjours et durée moyenne',
            y=0.95,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        height=500,
        template='plotly_white',
        showlegend=False,
        margin=dict(t=100, b=50, l=50, r=50)
    )

    # Mise à jour des titres des axes Y
    fig.update_yaxes(title_text="Nombre de séjours", secondary_y=False)
    fig.update_yaxes(title_text="Durée moyenne de séjour (jours)", secondary_y=True)

    # Affichage du graphique avec une colonne d'aide
    col_chart, col_help = st.columns([1, 0.01])
    with col_chart:
        st.plotly_chart(fig, use_container_width=True)
    with col_help:
        st.metric(label="help", value="", help="Ce graphique montre la relation entre le nombre de séjours (barres) et la durée moyenne de séjour (ligne) pour les pathologies les plus fréquentes en SSR.")

    # Tableau récapitulatif détaillé
    st.subheader("Évolution des pathologies en SSR (2018-2022)")
    
    # Calculer les évolutions année par année
    evolutions_by_year = {}
    years = sorted(df['annee'].unique())
    
    for i in range(len(years)-1):
        current_year = years[i]
        next_year = years[i+1]
        
        # Données pour l'année courante et suivante
        current_data = df[df['annee'] == current_year].groupby('nom_pathologie')['nbr_hospi'].sum()
        next_data = df[df['annee'] == next_year].groupby('nom_pathologie')['nbr_hospi'].sum()
        
        # Calculer l'évolution en pourcentage
        evolution = ((next_data - current_data) / current_data * 100).fillna(0)
        evolutions_by_year[f'{current_year}-{next_year}'] = evolution
    
    # Créer le DataFrame de base avec le nombre total de séjours
    df_summary = df.groupby('nom_pathologie')['nbr_hospi'].sum().reset_index()
    
    # Ajouter les évolutions année par année
    for period, evolution in evolutions_by_year.items():
        df_summary = df_summary.merge(
            evolution.reset_index().rename(columns={'nbr_hospi': f'Evolution_{period}'}),
            on='nom_pathologie',
            how='left'
        )
    
    # Calculer l'évolution globale (2018-2022)
    hospi_2018 = df[df['annee'] == 2018].groupby('nom_pathologie')['nbr_hospi'].sum()
    hospi_2022 = df[df['annee'] == 2022].groupby('nom_pathologie')['nbr_hospi'].sum()
    evolution_globale = ((hospi_2022 - hospi_2018) / hospi_2018 * 100).fillna(0)
    
    # Ajouter l'évolution globale au DataFrame
    df_summary = df_summary.merge(
        evolution_globale.reset_index().rename(columns={'nbr_hospi': 'Evolution_globale'}),
        on='nom_pathologie',
        how='left'
    )
    
    # Trier par évolution globale décroissante
    df_summary = df_summary.sort_values('Evolution_globale', ascending=False)
    
    # Renommer les colonnes pour l'affichage
    df_summary.columns = ['Pathologie', 'Séjours'] + [f'Évol. {period} (%)' for period in evolutions_by_year.keys()] + ['Évol. 2018-2022 (%)']
    
    # Colonnes d'évolution pour le gradient
    evolution_columns = ['Évol. 2018-2019 (%)', 'Évol. 2019-2020 (%)', 
                       'Évol. 2020-2021 (%)', 'Évol. 2021-2022 (%)', 
                       'Évol. 2018-2022 (%)']
    
    # Formater et afficher le tableau
    st.dataframe(
        df_summary.style.format({
            'Séjours': '{:,.0f}',
            'Évol. 2018-2019 (%)': '{:+.1f}%',
            'Évol. 2019-2020 (%)': '{:+.1f}%',
            'Évol. 2020-2021 (%)': '{:+.1f}%',
            'Évol. 2021-2022 (%)': '{:+.1f}%',
            'Évol. 2018-2022 (%)': '{:+.1f}%'
        }).background_gradient(
            subset=evolution_columns,
            cmap='RdYlBu_r'
        ),
        use_container_width=True
    )

else:
    st.error("Impossible de charger les données. Veuillez réessayer plus tard.")
st.markdown("Développé avec 💫 par l'équipe JBN | Le Wagon - Promotion 2024")