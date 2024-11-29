import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer
import pygwalker as pyg

def show_interactive_analysis(df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi):
    st.title("Analyse Interactive des Données")
    
    # Sélection du dataset à analyser
    dataset_choice = st.selectbox(
        "Choisir le dataset à analyser",
        ["Nombre d'hospitalisations", "Durée des séjours", "Tranches d'âge", "Capacité hospitalière"]
    )
    
    # Sélection du dataset en fonction du choix
    if dataset_choice == "Nombre d'hospitalisations":
        df = df_nbr_hospi
    elif dataset_choice == "Durée des séjours":
        df = df_duree_hospi
    elif dataset_choice == "Tranches d'âge":
        df = df_tranche_age_hospi
    else:
        df = df_capacite_hospi
    
    # Création du renderer PyGWalker
    pyg_html = StreamlitRenderer(df, spec="./gw_config.json", debug=False)
    
    # Affichage de l'interface PyGWalker
    st.components.v1.html(pyg_html.render_html(), height=1000, scrolling=True)
