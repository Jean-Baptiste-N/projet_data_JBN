import streamlit as st
import base64
from streamlit_lottie import st_lottie
import requests


# CSS personnalisé pour le style
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #2c3e50;
        padding: 1.5rem 0;
    }
    .section-title {
        color: #34495e;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Fonction pour afficher un GIF centré
def display_centered_gif(gif_path):
    st.markdown(
        f'<div style="display: flex; justify-content: center;">'
        f'<img src="{gif_path}" width="600px">'
        f'</div>',
        unsafe_allow_html=True
    )

# En-tête
st.markdown("<h1 class='main-title' style='margin-top: -70px; margin-bottom: -8000px;'>🏥 Projet d'analyse et de prédiction hospitalière</h1>", unsafe_allow_html=True)

# Charger et afficher l'animation Lottie
lottie_url = "https://lottie.host/01b53e9b-fb22-4256-b630-fe179a862c14/SpE9Sq2zVA.json"
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_animation = load_lottieurl(lottie_url)
if lottie_animation is not None:
    st.markdown('<div style="margin: -10px 0;">', unsafe_allow_html=True)  
    st_lottie(lottie_animation, speed=1, height=300, key="initial")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("Impossible de charger l'animation")
    
# Introduction
st.markdown("""
    <div class="feature-card" style="margin-top: -90px; padding: 1rem;">
    Cette application a été développée dans le cadre d'un projet de fin d'études pour la certification Data Analyste au sein du Wagon. 
    Notre équipe a créé cette plateforme interactive pour explorer et analyser les données hospitalières en France, 
    offrant des insights précieux sur différentes spécialités médicales et les tendances d'hospitalisation.
    </div>
""", unsafe_allow_html=True)
# Sections principales
st.markdown('<h2 class="section-title" style="margin-top: -1px;">📊 Fonctionnalités principales</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="feature-card" style="margin-bottom: -80px;">
        <h3>🔍 Vue générale</h3>
        <p>Explorez les tendances nationales et régionales des hospitalisations en France</p>
        <ul>
            <li>Statistiques nationales</li>
            <li>Comparaisons régionales</li>
            <li>Évolution temporelle</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card" style="margin-bottom: -40px;">
        <h3>🏥 Focus spécialités</h3>
        <p>Analyses détaillées par spécialité médicale</p>
        <ul>
            <li>Chirurgie</li>
            <li>Médecine</li>
            <li>Obstétrique</li>
            <li>Psychiatrie</li>
            <li>SSR</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
        <h3>🤖 Outils interactifs</h3>
        <p>Personnalisez votre analyse</p>
        <ul>
            <li>Générateur de graphiques</li>
            <li>Assistant virtuel IA</li>
            <li>Requêtes personnalisées</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

# Section Prédictions
st.markdown('<h2 class="section-title";>🔮 Modèles prédictifs</h2>', unsafe_allow_html=True)
st.markdown("""
    <div class="feature-card">
    <h3>📈 Prévisions hospitalières</h3>
    <p>Notre application intègrera bientôt des modèles prédictifs avancés pour :</p>
    <ul>
        <li>Prédire les besoins en lits hospitaliers par région et spécialité</li>
        <li>Anticiper les tendances d'hospitalisation saisonnières</li>
        <li>Optimiser la gestion des capacités hospitalières</li>
        <li>Prévoir les durées moyennes de séjour</li>
    </ul>
    <p><i>Cette fonctionnalité est en cours de développement et sera disponible prochainement.</i></p>
    </div>
""", unsafe_allow_html=True)

# Guide d'utilisation
st.markdown('<h2 class="section-title" style="margin-top: -10px;">📚 Comment utiliser l\'application</h2>', unsafe_allow_html=True)

# Tabs pour le guide d'utilisation
tab1, tab2, tab3 = st.tabs(["🚀 Démarrage", "📊 Analyses", "💡 Conseils"])

with tab1:
    st.markdown("""
        ### Pour commencer
        1. Utilisez la barre de navigation à gauche pour accéder aux différentes sections
        2. Commencez par la "Vue générale" pour une vision d'ensemble
        3. Explorez ensuite les focus spécifiques selon vos intérêts
    """)
    st.info("Emplacement pour GIF de navigation")

with tab2:
    st.markdown("""
        ### Créer vos analyses
        1. Accédez au "Générateur de graphiques"
        2. Sélectionnez vos variables d'intérêt
        3. Personnalisez vos visualisations
        4. Exportez ou partagez vos résultats
    """)
    st.info("Emplacement pour GIF de démonstration d'analyse")

with tab3:
    st.markdown("""
        ### Conseils d'utilisation
        - Utilisez les filtres pour affiner vos recherches
        - N'hésitez pas à combiner différentes visualisations
        - Consultez l'assistant IA pour des analyses approfondies
        - Explorez les comparaisons temporelles et géographiques
    """)

# Section Sources de données
st.markdown('<h2 class="section-title" style="margin-top: -10px;">📊 Sources des données</h2>', unsafe_allow_html=True)
st.markdown("""
    <div class="feature-card">
    <p>Cette analyse s'appuie sur des données officielles de la DREES (Direction de la Recherche, des Études, de l'Évaluation et des Statistiques) :</p>
    
    <ul style="list-style-type: none; padding-left: 0;">
        <li>📍 <a href="https://data.drees.solidarites-sante.gouv.fr/explore/dataset/500_morbidite-hospitaliere/information/">Morbidité hospitalière — DATA.DREES</a></li>
        <li>📍 <a href="https://data.drees.solidarites-sante.gouv.fr/explore/dataset/708_bases-statistiques-sae/information/">Bases statistiques SAE — DATA.DREES</a></li>
        <li>📍 <a href="https://data.drees.solidarites-sante.gouv.fr/explore/dataset/bases-ares/information/">Base ARES - Agrégats régionaux sur les établissements de santé</a></li>
        <li>📍 <a href="https://drees.solidarites-sante.gouv.fr/publications-communique-de-presse-documents-de-reference/panoramas-de-la-drees/les-depenses-de">Dépenses santé 2022 - Édition 2023</a></li>
    </ul>
    </div>
""", unsafe_allow_html=True)

# Section Contact et Aide
st.markdown('<h2 class="section-title" style="margin-top: -10px;">👥 Notre équipe</h2>', unsafe_allow_html=True)
st.markdown("""
    <div class="feature-card">
    Ce projet a été réalisé dans le cadre de la formation Data Analyste au Wagon par :
    
    <br>
    <ul style="list-style-type: none; padding-left: 0;">
        <li>👨‍💻 <b>Jean-Baptiste Nez</b> - <a href="https://www.linkedin.com/in/jean-baptiste-nez">LinkedIn</a></li>
        <li>👨‍💻 <b>Antonin Bourdelle</b> - <a href="https://www.linkedin.com/in/antonin-bourdelle">LinkedIn</a></li>
        <li>👩‍💻 <b>Astrid</b> - <a href="https://www.linkedin.com/in/astrid">LinkedIn</a></li>
    </ul>
    </br>

    <p>🎓 Projet de certification Data Analyste - Le Wagon - 2024</p>
    
    <p>📚 <a href="https://github.com/votre-repo">Voir le projet sur GitHub</a></p>
    </div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Développé avec ❤️ par l'équipe JBN | Le Wagon - Promotion 2024")
