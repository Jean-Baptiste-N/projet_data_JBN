import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def show_demographics_analysis(df_tranche_age_hospi):
    st.subheader("👥 Analyse démographique")
    
    # Taux de recours par tranche d'âge
    age_groups = ['tranche_age_1_4', 'tranche_age_5_14', 'tranche_age_15_24', 
                 'tranche_age_25_34', 'tranche_age_35_44', 'tranche_age_45_54',
                 'tranche_age_55_64', 'tranche_age_65_74', 'tranche_age_75_84',
                 'tranche_age_85_et_plus']
    
    # Calcul des moyennes par tranche d'âge
    age_means = []
    for group in age_groups:
        mean_value = df_tranche_age_hospi[group].mean()
        age_means.append({'tranche': group.replace('tranche_age_', ''), 'moyenne': mean_value})
    
    # Création du graphique
    fig = px.bar(
        age_means,
        x='tranche',
        y='moyenne',
        title="Taux de recours moyen par tranche d'âge",
        labels={'tranche': "Tranche d'âge", 'moyenne': 'Taux de recours moyen'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Evolution temporelle par tranche d'âge
    df_melted = df_tranche_age_hospi.melt(
        id_vars=['year'],
        value_vars=age_groups,
        var_name='tranche_age',
        value_name='taux_recours'
    )
    
    df_melted['tranche_age'] = df_melted['tranche_age'].str.replace('tranche_age_', '')
    
    fig = px.line(
        df_melted,
        x='year',
        y='taux_recours',
        color='tranche_age',
        title="Evolution du taux de recours par tranche d'âge",
        labels={
            'year': 'Année',
            'taux_recours': 'Taux de recours',
            'tranche_age': "Tranche d'âge"
        }
    )
    st.plotly_chart(fig, use_container_width=True)
