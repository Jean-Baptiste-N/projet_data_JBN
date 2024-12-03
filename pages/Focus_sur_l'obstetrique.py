import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
from plotly.subplots import make_subplots


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
st.markdown("<h1 class='main-title' style='margin-top: -70px; margin-bottom: -8000px;'>👶 Service Obstétrique</h1>", unsafe_allow_html=True)

# Fonction de chargement des données
@st.cache_resource
def load_data():
    try:
        # Chargement des secrets
        gcp_service_account = st.secrets["gcp_service_account"]
        client = bigquery.Client.from_service_account_info(gcp_service_account)
        
        # Requête SQL pour les données de chirurgie
        query = """
            SELECT *
            FROM `projet-jbn-data-le-wagon.dbt_medical_analysis_join_total_morbidite.class_join_total_morbidite_sexe_population`
            WHERE classification = 'O' AND niveau = 'Régions'
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
            ["Ensemble", "Homme", "Femme"],
            key="selecteur_sexe_obs"
        )

    with col2:
        # Filtre années avec une liste déroulante simple
        years = sorted(df['annee'].unique(), reverse=True)
        years_options = ["Toutes les années"] + [str(year) for year in years]
        selected_year = st.selectbox(
            "Année", 
            years_options, 
            key="year_filter_obs"
        )
    
    # Filtrage des données selon les sélections
    df_filtered = df.copy()
    
    # Filtre par sexe
    if selected_sex != "Ensemble":
        df_filtered = df_filtered[df_filtered['sexe'] == selected_sex]
    
    # Filtre par année si nécessaire
    if selected_year != "Toutes les années":
        df_filtered = df_filtered[df_filtered['annee'] == int(selected_year)]
    
    tab1, tab2, tab3= st.tabs([
        "📈 Analyse par pathologies",
        "🗺️ Analyse par capacité",
        "🏥 Analyse démographique",

    ])

    with tab1:

        # Liste déroulante de toutes les pathologies
        all_pathologies = sorted(df_filtered['nom_pathologie'].unique())
        all_pathologies.insert(0, "Toutes les pathologies")  # Ajout de l'option pour toutes les pathologies
        selected_pathology = st.selectbox(
            "🔍 Sélectionner une pathologie en médecine pour obtenir des détails",
            all_pathologies,
            key="pathology_selector_psy"
        )
        
        # Afficher les données pour la pathologie sélectionnée
        if selected_pathology == "Toutes les pathologies":
            path_data = df_filtered[
                (df_filtered['sexe'] == selected_sex)
            ]
        else:
            path_data = df_filtered[
                (df_filtered['nom_pathologie'] == selected_pathology) &
                (df_filtered['sexe'] == selected_sex)
            ]
        
        # Calcul des métriques avec les filtres appliqués
        total_hospi = path_data['nbr_hospi'].sum()
        
        # Calcul de la durée moyenne en fonction de la sélection
        if selected_pathology == "Toutes les pathologies":
            avg_duration = df_filtered[
                (df_filtered['sexe'] == selected_sex)
            ]['AVG_duree_hospi'].mean()
        else:
            avg_duration = df_filtered[
                (df_filtered['nom_pathologie'] == selected_pathology) &
                (df_filtered['sexe'] == selected_sex)
            ]['AVG_duree_hospi'].mean()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total d'hospitalisations", f"{total_hospi/1_000:,.2f}K")
        with col2:
            st.metric("Durée moyenne", f"{avg_duration:.1f} jours")
        with col3:
            st.metric("Indice comparatif", f"{path_data['indice_comparatif_tt_age_percent'].mean():.1f}%")
        with col4:
            hospi_24h = path_data['hospi_total_24h'].sum()
            percentage_24h = (hospi_24h / total_hospi * 100) if total_hospi > 0 else 0
            st.metric("Hospitalisations < 24h", f"{percentage_24h:.1f}%")
        with col5:
            # Sélectionner toutes les colonnes tranche_age_*
            age_columns = [col for col in path_data.columns if col.startswith('tranche_age_')]
            # Calculer la somme pour chaque tranche d'âge
            age_sums = path_data[age_columns].sum()
            # Trouver la tranche d'âge avec la plus grande valeur
            most_common_age = age_sums.idxmax().replace('tranche_age_', '')
            st.metric("Tranche d'âge majoritaire", most_common_age)

        
        st.divider()

        # Ajout d'un sélecteur pour filtrer le nombre de pathologies à afficher
        n_pathologies = st.slider("Nombre de pathologies à afficher", 5, 57, 20)
        
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
                name="Nombre d'hospitalisations",
                marker_color=MAIN_COLOR,
                customdata=hospi_by_pathology[['nom_pathologie', 'nbr_hospi']],
                hovertemplate="<b>Pathologie:</b> %{customdata[0]}<br>" +
                            "<b>Hospitalisations:</b> %{customdata[1]:,.0f}<br><extra></extra>"
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
                text='Pathologies médicales : Hospitalisations et durée moyenne de séjour',
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
        fig.update_yaxes(title_text="Nombre d'hospitalisations", secondary_y=False)
        fig.update_yaxes(title_text="Durée moyenne de séjour (jours)", secondary_y=True)

        # Affichage du graphique avec une colonne d'aide
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique montre la relation entre le nombre d'hospitalisations (barres) et la durée moyenne de séjour (ligne) pour les pathologies médicales les plus fréquentes.")

        # Préparation des DataFrames pour les graphiques
        df_nbr_hospi = df_filtered.copy()
        df_duree_hospi = df_filtered.copy()
        df_tranche_age_hospi = df_filtered.copy()

        st.markdown("---")
        # Graphique combiné (scatter plot)
        # Fusion des données d'hospitalisation et de durée par année
        combined_data = pd.merge(
            df_nbr_hospi.groupby(['nom_pathologie', 'annee'])['nbr_hospi'].sum().reset_index(),
            df_duree_hospi.groupby(['nom_pathologie', 'annee'])['AVG_duree_hospi'].mean().reset_index(),
            on=['nom_pathologie', 'annee']
        )
        
        # Filtrer pour garder seulement les n_pathologies plus fréquentes par année
        top_pathologies = df_nbr_hospi.groupby('nom_pathologie')['nbr_hospi'].sum().nlargest(n_pathologies).index
        combined_data = combined_data[combined_data['nom_pathologie'].isin(top_pathologies)]

        # Création du scatter plot avec animation
        if selected_year != "Toutes les années":
            # Si une année spécifique est sélectionnée, créer un scatter plot statique
            fig = px.scatter(
                combined_data,
                x='nbr_hospi',
                y='AVG_duree_hospi',
                text='nom_pathologie',
                title=f'Relation entre nombre d\'hospitalisations et durée moyenne de séjour ({selected_year})',
                labels={'nbr_hospi': 'Nombre d\'hospitalisations',
                    'AVG_duree_hospi': 'Durée moyenne de séjour (jours)',
                    'nom_pathologie': 'Pathologie'},
                size='nbr_hospi',
                size_max=40,
                color='AVG_duree_hospi',
                color_continuous_scale='Viridis'
            )
        else:
            # Si toutes les années sont sélectionnées, créer le scatter plot animé
            fig = px.scatter(
                combined_data,
                x='nbr_hospi',
                y='AVG_duree_hospi',
                text='nom_pathologie',
                animation_frame='annee',
                animation_group='nom_pathologie',
                title=f'Relation entre nombre d\'hospitalisations et durée moyenne de séjour',
                labels={'nbr_hospi': 'Nombre d\'hospitalisations',
                    'AVG_duree_hospi': 'Durée moyenne de séjour (jours)',
                    'nom_pathologie': 'Pathologie'},
                size='nbr_hospi',
                size_max=40,
                color='AVG_duree_hospi',
                color_continuous_scale='Viridis'
            )
            # Configuration de l'animation
            if hasattr(fig, 'layout') and hasattr(fig.layout, 'updatemenus'):
                try:
                    fig.layout.sliders[0].x = 0.1
                    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1500
                    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500
                except (IndexError, KeyError, AttributeError):
                    pass  # Ignorer les erreurs si la configuration de l'animation échoue
                    
        # Personnalisation du graphique
        fig.update_traces(
            textposition='top center',
            hovertemplate="<b>%{text}</b><br>" +
                        "Hospitalisations: %{x:,.0f}<br>" +
                        "Durée moyenne: %{y:.1f} jours<br>" +
                        "<extra></extra>"
        )

        # Mise à jour de la mise en page
        fig.update_layout(
            height=800,
            template='plotly_white',
            showlegend=False,
            margin=dict(t=100, b=100, l=100, r=150),
            annotations=[
                dict(
                    text="<b>Légende</b> : <br>La taille des points représente le nombre d'hospitalisations<br>La couleur indique la durée moyenne de séjour",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.8, y=1.1,
                    align="left",
                    xanchor="left"
                )
            ]
        )

        # Affichage du graphique avec une colonne d'aide
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique animé montre l'évolution de la relation entre le nombre d'hospitalisations et la durée moyenne de séjour pour chaque pathologie au fil des années. La taille des bulles représente le nombre d'hospitalisations.")
        st.markdown("---")
        # Graphique 3D
        # Fusion des données avec les trois métriques
        combined_data_3d = pd.merge(
            df_nbr_hospi.groupby(['nom_pathologie', 'annee'])['nbr_hospi'].sum().reset_index(),
            df_duree_hospi.groupby(['nom_pathologie', 'annee'])['AVG_duree_hospi'].mean().reset_index(),
            on=['nom_pathologie', 'annee']
        )
        combined_data_3d = pd.merge(
            combined_data_3d,
            df_tranche_age_hospi.groupby(['nom_pathologie', 'annee'])['indice_comparatif_tt_age_percent'].mean().reset_index(),
            on=['nom_pathologie', 'annee']
        )

        # Filtrer pour garder seulement les n_pathologies plus fréquentes
        top_pathologies = df_nbr_hospi.groupby('nom_pathologie')['nbr_hospi'].sum().nlargest(n_pathologies).index
        combined_data_3d = combined_data_3d[combined_data_3d['nom_pathologie'].isin(top_pathologies)]

        # Création du graphique 3D avec animation
        fig = go.Figure()

        # Créer les frames pour l'animation avec interpolation
        frames = []
        years = sorted(combined_data_3d['annee'].unique())
        
        for i in range(len(years)):
            current_year = years[i]
            current_data = combined_data_3d[combined_data_3d['annee'] == current_year].copy()
            
            # Nettoyer les valeurs NA
            current_data = current_data.dropna(subset=['nbr_hospi', 'AVG_duree_hospi', 'indice_comparatif_tt_age_percent'])
            
            # Ajouter la frame pour l'année actuelle
            frame = go.Frame(
                data=[go.Scatter3d(
                    x=current_data['nbr_hospi'].tolist(),
                    y=current_data['AVG_duree_hospi'].tolist(),
                    z=current_data['indice_comparatif_tt_age_percent'].tolist(),
                    mode='markers+text',
                    text=current_data['nom_pathologie'].tolist(),
                    textposition='top center',
                    marker=dict(
                        size=[x/current_data['nbr_hospi'].max()*30 for x in current_data['nbr_hospi']],
                        color=current_data['AVG_duree_hospi'].tolist(),
                        colorscale='Viridis',
                        opacity=0.8,
                        colorbar=dict(title="Durée moyenne de séjour (jours)")
                    ),
                    hovertemplate="<b>%{text}</b><br>" +
                                f"Année: {current_year}<br>" +
                                "Hospitalisations: %{x:,.0f}<br>" +
                                "Durée moyenne: %{y:.1f} jours<br>" +
                                "Indice comparatif: %{z:.1f}%<br>" +
                                "<extra></extra>"
                )],
                name=str(current_year)
            )
            frames.append(frame)
            
            # Créer des frames intermédiaires si ce n'est pas la dernière année
            if i < len(years) - 1:
                next_year = years[i + 1]
                next_data = combined_data_3d[combined_data_3d['annee'] == next_year].copy()
                next_data = next_data.dropna(subset=['nbr_hospi', 'AVG_duree_hospi', 'indice_comparatif_tt_age_percent'])
                
                # S'assurer que les données sont alignées
                common_pathologies = sorted(list(set(current_data['nom_pathologie']) & set(next_data['nom_pathologie'])))
                current_data = current_data[current_data['nom_pathologie'].isin(common_pathologies)].sort_values('nom_pathologie')
                next_data = next_data[next_data['nom_pathologie'].isin(common_pathologies)].sort_values('nom_pathologie')
                
                # Créer 5 frames intermédiaires entre chaque année
                for step in range(1, 6):
                    # Interpolation linéaire entre les années
                    alpha = step / 6.0
                    
                    # Calculer les valeurs interpolées
                    nbr_hospi = (current_data['nbr_hospi'].values * (1-alpha) + next_data['nbr_hospi'].values * alpha).tolist()
                    avg_duree = (current_data['AVG_duree_hospi'].values * (1-alpha) + next_data['AVG_duree_hospi'].values * alpha).tolist()
                    indice = (current_data['indice_comparatif_tt_age_percent'].values * (1-alpha) + next_data['indice_comparatif_tt_age_percent'].values * alpha).tolist()
                    
                    # Calculer la taille des points
                    max_hospi = max(nbr_hospi) if nbr_hospi else 1  # Éviter la division par zéro
                    point_sizes = [x/max_hospi*30 for x in nbr_hospi]
                    
                    frame = go.Frame(
                        data=[go.Scatter3d(
                            x=nbr_hospi,
                            y=avg_duree,
                            z=indice,
                            mode='markers+text',
                            text=current_data['nom_pathologie'].tolist(),
                            textposition='top center',
                            marker=dict(
                                size=point_sizes,
                                color=avg_duree,
                                colorscale='Viridis',
                                opacity=0.8,
                                colorbar=dict(title="Durée moyenne de séjour (jours)")
                            ),
                            hovertemplate="<b>%{text}</b><br>" +
                                        f"Transition {current_year}-{next_year}<br>" +
                                        "Hospitalisations: %{x:,.0f}<br>" +
                                        "Durée moyenne: %{y:.1f} jours<br>" +
                                        "Indice comparatif: %{z:.1f}%<br>" +
                                        "<extra></extra>"
                        )],
                        name=f"{current_year}_{step}"
                    )
                    frames.append(frame)
            
            # Ajouter la première année comme trace initiale
            if current_year == years[0]:
                fig.add_trace(frame.data[0])

        fig.frames = frames

        # Mise à jour des steps pour inclure uniquement les années principales
        steps = []
        for year in years:
            step = dict(
                method="animate",
                args=[[str(year)], {
                    "frame": {"duration": 300, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 300}
                }],
                label=str(year)
            )
            steps.append(step)

        sliders = [dict(
            active=0,
            currentvalue={"prefix": "Année: "},
            pad={"t": 50},
            steps=steps
        )]

        # Mise en page du graphique 3D
        fig.update_layout(
            title=dict(
                text='Évolution des pathologies selon trois dimensions clés',
                y=0.95,
                x=0.4,
                xanchor='right',
                yanchor='top'
            ),
            scene=dict(
                xaxis_title='Nombre d\'hospitalisations',
                yaxis_title='Durée moyenne de séjour (jours)',
                zaxis_title='Indice comparatif (%)',
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            height=800,
            template='plotly_white',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            ),
            width=800,
            sliders=sliders,
            annotations=[
                dict(
                    text="<b>Légende</b> : <br>La taille des points représente le nombre d'hospitalisations<br>La couleur indique la durée moyenne de séjour",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.8, y=1.1,
                    align="left",
                    xanchor="left"
                )
            ],
            margin=dict(t=100, b=50, l=50, r=50),  # Augmenter la marge du haut pour plus d'espace
            updatemenus=[{
                "buttons": [
                    {
                        "args": [None, {
                            "frame": {"duration": 300, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": 300},
                            "mode": "immediate"
                        }],
                        "label": "Lecture",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {
                            "frame": {"duration": 0, "redraw": True},
                            "mode": "immediate",
                            "transition": {"duration": 0}
                        }],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.0,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }]
        )

        # Ajout de configuration pour une animation plus fluide
        fig.update_traces(
            hoverinfo="none",  # Désactiver temporairement le hover pendant l'animation
            customdata=combined_data_3d[['nom_pathologie', 'nbr_hospi', 'AVG_duree_hospi', 'indice_comparatif_tt_age_percent']].values,
        )

        # Affichage du graphique 3D
        col_chart, col_help = st.columns([1, 0.01])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_help:
            st.metric(label="help", value="", help="Ce graphique 3D montre la distribution des hospitalisations par pathologie, durée moyenne de séjour et indice comparatif. Utilisez les contrôles pour faire pivoter et zoomer sur le graphique.")
        st.markdown("---")
        # Tableau récapitulatif détaillé
        st.subheader("Évolution des pathologies - Augmentation les plus importantes (2018-2022)")
        
        # Calculer les évolutions année par année
        evolutions_by_year = {}
        years = sorted(df_filtered['annee'].unique())
        
        for i in range(len(years)-1):
            current_year = years[i]
            next_year = years[i+1]
            
            # Données pour l'année courante et suivante
            current_data = df_filtered[df_filtered['annee'] == current_year].groupby('nom_pathologie')['nbr_hospi'].sum()
            next_data = df_filtered[df_filtered['annee'] == next_year].groupby('nom_pathologie')['nbr_hospi'].sum()
            
            # Calculer l'évolution en pourcentage
            evolution = ((next_data - current_data) / current_data * 100).fillna(0)
            evolutions_by_year[f'{current_year}-{next_year}'] = evolution
            
        # Créer le DataFrame de base avec le nombre total d'hospitalisations
        df_summary = df_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().reset_index()
        
        # Ajouter les évolutions année par année
        for period, evolution in evolutions_by_year.items():
            df_summary = df_summary.merge(
                evolution.reset_index().rename(columns={'nbr_hospi': f'Evolution_{period}'}),
                on='nom_pathologie',
                how='left'
            )
        
        # Calculer l'évolution globale (2018-2022)
        hospi_2018 = df_filtered[df_filtered['annee'] == min(years)].groupby('nom_pathologie')['nbr_hospi'].sum()
        hospi_2022 = df_filtered[df_filtered['annee'] == max(years)].groupby('nom_pathologie')['nbr_hospi'].sum()
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
        df_summary.columns = ['Pathologie', 'Hospitalisations'] + [f'Évol. {period} (%)' for period in evolutions_by_year.keys()] + ['Évol. globale (%)']
        
        # Colonnes d'évolution pour le gradient
        evolution_columns = [col for col in df_summary.columns if 'Évol.' in col]
        
        # Formater et afficher le tableau
        st.dataframe(
            df_summary.style.format({
                'Hospitalisations': '{:,.0f}',
                **{col: '{:+.1f}%' for col in evolution_columns}
            }).background_gradient(
                subset=evolution_columns,
                cmap='RdYlBu_r'
            ),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Deuxième tableau avec les baisses en premier
        st.subheader("Évolution des pathologies - Baisses les plus importantes (2018-2022)")
        
        # Utiliser le même DataFrame mais trié dans l'ordre inverse
        df_summary_desc = df_summary.sort_values('Évol. globale (%)', ascending=True)
        
        # Afficher le deuxième tableau
        st.dataframe(
            df_summary_desc.style.format({
                'Hospitalisations': '{:,.0f}',
                **{col: '{:+.1f}%' for col in evolution_columns}
            }).background_gradient(
                subset=evolution_columns,
                cmap='RdYlBu_r'
            ),
            use_container_width=True
        )
        
    st.markdown("---")
    st.markdown("Développé avec 💫 par l'équipe JBN | Le Wagon - Promotion 2024")

else:
    st.error("Impossible de charger les données. Veuillez réessayer plus tard.")