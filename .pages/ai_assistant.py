import streamlit as st
from langchain_openai import AzureChatOpenAI

def get_data_context():
    return """
    Les données disponibles sont :
    1. Nombre d'hospitalisations par année, région, département et pathologie
    2. Durée moyenne des séjours hospitaliers
    3. Répartition par tranches d'âge
    4. Capacité des services hospitaliers
    """

def show_ai_assistant(df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi):
    st.title("Assistant IA pour l'Analyse des Données")
    
    # Initialisation de l'historique des conversations
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        # Message de contexte initial
        context = get_data_context()
        st.session_state.messages.append({"role": "assistant", "content": f"""
        Bonjour! Je suis votre assistant IA pour l'analyse des données hospitalières.
        
        {context}
        
        Comment puis-je vous aider dans votre analyse ?
        """})
    
    # Affichage de l'historique des conversations
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Zone de saisie pour la question
    if prompt := st.chat_input("Posez votre question sur les données..."):
        # Ajout de la question à l'historique
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Affichage de la question
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Traitement de la réponse (à implémenter avec Azure OpenAI)
        with st.chat_message("assistant"):
            response = "Cette fonctionnalité nécessite une configuration avec Azure OpenAI. Veuillez configurer vos clés API pour activer l'assistant."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
