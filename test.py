import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery

# Load secrets
gcp_service_account = st.secrets["gcp_service_account"]

# Initialize BigQuery client
client = bigquery.Client.from_service_account_info(gcp_service_account)

# Load datasets
df_nbr_hospi = client.query('''
  SELECT
    *
  FROM
    `projet-jbn-data-le-wagon.morbidite_h.nbr_hospi_intermediate`
''').to_dataframe()

df_duree_hospi = client.query('''
  SELECT
    *
  FROM
    `projet-jbn-data-le-wagon.morbidite_h.duree_hospi_dpt_intermediate`
''').to_dataframe()

df_tranche_age_hospi = client.query('''
  SELECT
    *
  FROM
    `projet-jbn-data-le-wagon.morbidite_h.tranche_age_hospi_dpt_intermediate`
''').to_dataframe()

# Check for missing values
st.write("Missing values in df_nbr_hospi:", df_nbr_hospi.isnull().sum())
st.write("Missing values in df_duree_hospi:", df_duree_hospi.isnull().sum())
st.write("Missing values in df_tranche_age_hospi:", df_tranche_age_hospi.isnull().sum())

# Number of hospitalizations by year
hospi_by_year = df_nbr_hospi.groupby('year')['nbr_hospi'].sum().reset_index()
fig = px.line(hospi_by_year, x='year', y='nbr_hospi', title='Number of Hospitalizations by Year')
st.plotly_chart(fig)

# Number of hospitalizations by departement
hospi_by_departement = df_nbr_hospi.groupby('nom_departement')['nbr_hospi'].sum().reset_index().sort_values(by='nbr_hospi', ascending=False)
fig = px.bar(hospi_by_departement, x='nbr_hospi', y='nom_departement', title='Number of Hospitalizations by departement')
st.plotly_chart(fig)

# Number of hospitalizations by pathology
hospi_by_pathology = df_nbr_hospi.groupby('nom_pathologie')['nbr_hospi'].sum().reset_index().sort_values(by='nbr_hospi', ascending=False)
fig = px.bar(hospi_by_pathology.head(20), x='nbr_hospi', y='nom_pathologie', title='Top 20 Pathologies by Number of Hospitalizations')
st.plotly_chart(fig)

# Average duration of hospitalizations by year
duree_by_year = df_duree_hospi.groupby('year')['AVG_duree_hospi'].mean().reset_index()
fig = px.line(duree_by_year, x='year', y='AVG_duree_hospi', title='Average Duration of Hospitalizations by Year')
st.plotly_chart(fig)

# Average duration of hospitalizations by departement
duree_by_departement = df_duree_hospi.groupby('nom_departement')['AVG_duree_hospi'].mean().reset_index().sort_values(by='AVG_duree_hospi', ascending=False)
fig = px.bar(duree_by_departement, x='AVG_duree_hospi', y='nom_departement', title='Average Duration of Hospitalizations by departement')
st.plotly_chart(fig)

# Average duration of hospitalizations by pathology
duree_by_pathology = df_duree_hospi.groupby('nom_pathologie')['AVG_duree_hospi'].mean().reset_index().sort_values(by='AVG_duree_hospi', ascending=False)
fig = px.bar(duree_by_pathology.head(20), x='AVG_duree_hospi', y='nom_pathologie', title='Top 20 Pathologies by Average Duration of Hospitalizations')
st.plotly_chart(fig)

# Rate of recourse by age group
age_groups = ['tranche_age_1_4', 'tranche_age_5_14', 'tranche_age_15_24', 'tranche_age_25_34', 'tranche_age_35_44', 'tranche_age_45_54', 'tranche_age_55_64', 'tranche_age_65_74', 'tranche_age_75_84', 'tranche_age_85_et_plus']
recourse_by_age = df_tranche_age_hospi[age_groups].mean().reset_index()
recourse_by_age.columns = ['Age Group', 'Rate of Recourse']
fig = px.bar(recourse_by_age, x='Rate of Recourse', y='Age Group', title='Rate of Recourse by Age Group')
st.plotly_chart(fig)

# Comparative indices by pathology
comparative_indices = df_tranche_age_hospi.groupby('nom_pathologie')['indice_comparatif_tt_age_percent'].mean().reset_index().sort_values(by='indice_comparatif_tt_age_percent', ascending=False)
fig = px.bar(comparative_indices.head(20), x='indice_comparatif_tt_age_percent', y='nom_pathologie', title='Top 20 Pathologies by Comparative Indices')
st.plotly_chart(fig)