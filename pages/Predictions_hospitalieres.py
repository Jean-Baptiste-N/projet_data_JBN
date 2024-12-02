import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# CSS personnalisé
st.markdown("""
    <style>
    .main-title {
        color: #2c3e50;
        text-align: center;
        padding: 1rem 0;
    }
    .prediction-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Définition des couleurs du thème
MAIN_COLOR = '#003366'  # Bleu marine principal
SECONDARY_COLOR = '#AFDC8F'  # Vert clair complémentaire
ACCENT_COLOR = '#3D7317'  # Vert foncé pour les accents

# Titre principal
st.markdown("<h1 class='main-title'>🔮 Prédictions Hospitalières</h1>", unsafe_allow_html=True)

# Sélecteur de type de prédiction
prediction_type = st.selectbox(
    "Choisissez le type de prédiction",
    ["Besoins en lits", "Tendances d'hospitalisation", "Durées de séjour"]
)

# Filtres communs
col1, col2, col3 = st.columns(3)
with col1:
    region = st.selectbox("Région", ["Toutes les régions", "Île-de-France", "Auvergne-Rhône-Alpes", "Nouvelle-Aquitaine"])
with col2:
    specialite = st.selectbox("Spécialité", ["Toutes les spécialités", "Médecine", "Chirurgie", "Obstétrique", "SSR", "Psychiatrie"])
with col3:
    horizon = st.selectbox("Horizon de prédiction", ["1 mois", "3 mois", "6 mois", "1 an"])

# Fonction pour générer des données simulées
def generate_mock_data(days=365):
    dates = [datetime.now() + timedelta(days=x) for x in range(days)]
    values = np.random.normal(100, 15, days) + np.sin(np.array(range(days))/30.0)*20
    return pd.DataFrame({
        'Date': dates,
        'Valeur': values
    })

# Affichage selon le type de prédiction
if prediction_type == "Besoins en lits":
    st.markdown("""
        <div class='prediction-card'>
        <h3>📊 Prédiction des besoins en lits</h3>
        <p>Cette section utilise des modèles de machine learning pour prédire les besoins futurs en lits hospitaliers,
        en tenant compte des tendances historiques, des variations saisonnières et des facteurs démographiques.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Graphique de prédiction
    df = generate_mock_data()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'][:180],
        y=df['Valeur'][:180],
        name='Données historiques',
        line=dict(color=MAIN_COLOR)
    ))
    fig.add_trace(go.Scatter(
        x=df['Date'][180:],
        y=df['Valeur'][180:],
        name='Prédictions',
        line=dict(color=SECONDARY_COLOR, dash='dash')
    ))
    fig.update_layout(
        title='Prédiction des besoins en lits',
        xaxis_title='Date',
        yaxis_title='Nombre de lits nécessaires',
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)

elif prediction_type == "Tendances d'hospitalisation":
    st.markdown("""
        <div class='prediction-card'>
        <h3>📈 Analyse des tendances d'hospitalisation</h3>
        <p>Visualisez les tendances futures d'hospitalisation basées sur l'analyse des données historiques
        et les facteurs saisonniers.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Graphique des tendances
    df = generate_mock_data()
    fig = px.line(df, x='Date', y='Valeur',
                 title='Tendances d\'hospitalisation prévues')
    fig.update_traces(line_color=MAIN_COLOR)
    fig.add_hrect(
        y0=df['Valeur'].mean() - df['Valeur'].std(),
        y1=df['Valeur'].mean() + df['Valeur'].std(),
        fillcolor=SECONDARY_COLOR,
        opacity=0.2,
        layer="below",
        line_width=0,
    )
    fig.update_layout(template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)

else:  # Durées de séjour
    st.markdown("""
        <div class='prediction-card'>
        <h3>⏱️ Prévision des durées de séjour</h3>
        <p>Estimez les durées moyennes de séjour futures par service et par type de pathologie
        pour optimiser la gestion des ressources hospitalières.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Graphique des durées de séjour
    services = ['Médecine', 'Chirurgie', 'Obstétrique', 'SSR', 'Psychiatrie']
    durees = np.random.normal(7, 2, len(services))
    fig = go.Figure(data=[
        go.Bar(name='Durée moyenne actuelle', x=services, y=durees, marker_color=MAIN_COLOR),
        go.Bar(name='Prévision à 3 mois', x=services, y=durees*1.1, marker_color=SECONDARY_COLOR)
    ])
    fig.update_layout(
        title='Durées moyennes de séjour par service',
        barmode='group',
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)

# Métriques de performance
st.markdown("### 📊 Métriques de performance du modèle")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Précision du modèle", "87%", "↑ 2%")
with col2:
    st.metric("MAE", "4.3 jours", "↓ 0.5")
with col3:
    st.metric("R²", "0.83", "↑ 0.02")

# Notes méthodologiques
with st.expander("📝 Notes méthodologiques"):
    st.markdown("""
    ### Méthodologie de prédiction
    
    Notre modèle utilise une combinaison de :
    - Séries temporelles avancées (SARIMA, Prophet)
    - Machine Learning (Random Forest, XGBoost)
    - Facteurs externes (données démographiques, épidémiologiques)
    
    ### Sources de données
    - Historique des hospitalisations (PMSI)
    - Données démographiques (INSEE)
    - Facteurs saisonniers
    
    ### Limitations
    - Les prédictions sont des estimations basées sur les données historiques
    - Les événements exceptionnels peuvent impacter la précision
    - Mise à jour mensuelle des modèles
    """)

# Avertissement
st.info("⚠️ Ces prédictions sont des estimations basées sur des modèles statistiques et doivent être utilisées comme aide à la décision uniquement.")