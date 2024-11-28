import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
from shiny import App, render, ui, reactive
from shinyswatch import theme
import asyncio

class HospitalDashboard:
    def __init__(self):
        # Initialize BigQuery client and load data
        gcp_service_account = {
            # Your GCP service account credentials here
        }
        self.client = bigquery.Client.from_service_account_info(gcp_service_account)
        self.load_data()

    def load_data(self):
        # BigQuery data loading similar to Streamlit version
        try:
            self.df_nbr_hospi = self.client.query(
                'SELECT * FROM `projet-jbn-data-le-wagon.morbidite_h.nbr_hospi_intermediate`'
            ).to_dataframe()
            
            self.df_duree_hospi = self.client.query(
                'SELECT * FROM `projet-jbn-data-le-wagon.duree_hospitalisation_par_patho.duree_hospi_region_et_dpt_clean_classifie`'
            ).to_dataframe()
            
            self.df_tranche_age_hospi = self.client.query(
                'SELECT * FROM `projet-jbn-data-le-wagon.morbidite_h.tranche_age_intermediate`'
            ).to_dataframe()
            
            self.df_capacite_hospi = self.client.query(
                'SELECT * FROM `projet-jbn-data-le-wagon.capacite_services_h.capacite_etablissement_intermediate_class`'
            ).to_dataframe()
        except Exception as e:
            print(f"Data loading error: {e}")

    def calculate_main_metrics(self):
        metrics = {}
        
        # Hospitalisations by year
        for year in range(2018, 2023):
            total_hospi = self.df_nbr_hospi["nbr_hospi"][
                pd.to_datetime(self.df_nbr_hospi["year"]).dt.year == year
            ].sum()
            metrics[f"hospi_{year}"] = total_hospi

        # Available beds by year
        lits_disponibles = self.df_capacite_hospi.groupby('year')['total_lit_hospi_complete'].sum().reset_index()
        for year in range(2018, 2023):
            metrics[f"lits_{year}"] = lits_disponibles[
                lits_disponibles['year'] == year
            ]['total_lit_hospi_complete'].sum()
        
        return metrics

def create_app():
    dashboard = HospitalDashboard()
    main_metrics = dashboard.calculate_main_metrics()

    app_ui = ui.page_fluid(
        theme.superhero(),
        ui.panel_title("🏥 Hospital Analysis Dashboard"),
        
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.input_checkbox_group(
                    "selected_years", 
                    "Select Years", 
                    choices=sorted(dashboard.df_nbr_hospi['year'].unique()),
                    selected=sorted(dashboard.df_nbr_hospi['year'].unique())
                ),
                ui.input_checkbox_group(
                    "selected_departments", 
                    "Select Departments", 
                    choices=sorted(dashboard.df_nbr_hospi['nom_departement'].unique()),
                    selected=sorted(dashboard.df_nbr_hospi['nom_departement'].unique())
                )
            ),
            
            ui.panel_main(
                ui.navset_tab(
                    ui.nav("General View",
                        ui.output_data_frame("general_metrics"),
                        ui.output_plot("hospitalization_trend"),
                        ui.output_plot("duration_trend")
                    ),
                    ui.nav("Geographic Analysis",
                        ui.output_plot("hospitalizations_by_department"),
                        ui.output_plot("duration_by_department")
                    ),
                    ui.nav("Pathologies",
                        ui.output_plot("top_pathologies"),
                        ui.output_plot("pathology_duration")
                    ),
                    ui.nav("Demographics",
                        ui.output_plot("age_group_recourse")
                    ),
                    ui.nav("Geographic Map",
                        ui.output_plot("department_map")
                    )
                )
            )
        )
    )

    def server(input, output, session):
        @output
        @render.data_frame
        def general_metrics():
            metrics_data = []
            for year in range(2018, 2023):
                metrics_data.append({
                    'Year': year, 
                    'Hospitalizations': f"{main_metrics[f'hospi_{year}'] / 1_000_000:.2f}M",
                    'Available Beds': main_metrics[f'lits_{year}']
                })
            return pd.DataFrame(metrics_data)

        @output
        @render.plot
        def hospitalization_trend():
            hospi_by_year = dashboard.df_nbr_hospi.groupby('year')['nbr_hospi'].sum().reset_index()
            return px.line(hospi_by_year, x='year', y='nbr_hospi', title='Hospitalizations by Year')

        @output
        @render.plot
        def duration_trend():
            duree_by_year = dashboard.df_duree_hospi.groupby('year')['AVG_duree_hospi'].mean().reset_index()
            return px.line(duree_by_year, x='year', y='AVG_duree_hospi', title='Average Hospitalization Duration by Year')

        @output
        @render.plot
        def hospitalizations_by_department():
            filtered_df = dashboard.df_nbr_hospi[
                dashboard.df_nbr_hospi['year'].isin(input.selected_years()) & 
                dashboard.df_nbr_hospi['nom_departement'].isin(input.selected_departments())
            ]
            hospi_by_departement = filtered_df.groupby('nom_departement')['nbr_hospi'].sum().reset_index()
            hospi_by_departement = hospi_by_departement.sort_values(by='nbr_hospi', ascending=True)
            return px.bar(hospi_by_departement, x='nbr_hospi', y='nom_departement', orientation='h')

        @output
        @render.plot
        def duration_by_department():
            filtered_df = dashboard.df_duree_hospi[
                dashboard.df_duree_hospi['year'].isin(input.selected_years()) & 
                dashboard.df_duree_hospi['nom_departement_region'].isin(input.selected_departments())
            ]
            duree_by_departement = filtered_df.groupby('nom_departement_region')['AVG_duree_hospi'].mean().reset_index()
            duree_by_departement = duree_by_departement.sort_values(by='AVG_duree_hospi', ascending=True)
            return px.bar(duree_by_departement, x='AVG_duree_hospi', y='nom_departement_region', orientation='h')

        @output
        @render.plot
        def top_pathologies():
            filtered_df = dashboard.df_nbr_hospi[
                dashboard.df_nbr_hospi['year'].isin(input.selected_years()) & 
                dashboard.df_nbr_hospi['nom_departement'].isin(input.selected_departments())
            ]
            hospi_by_pathology = filtered_df.groupby('nom_pathologie')['nbr_hospi'].sum().reset_index()
            hospi_by_pathology = hospi_by_pathology.sort_values(by='nbr_hospi', ascending=True).tail(20)
            return px.bar(hospi_by_pathology, x='nbr_hospi', y='nom_pathologie', orientation='h')

        @output
        @render.plot
        def pathology_duration():
            filtered_df = dashboard.df_duree_hospi[
                dashboard.df_duree_hospi['year'].isin(input.selected_years()) & 
                dashboard.df_duree_hospi['nom_departement_region'].isin(input.selected_departments())
            ]
            duree_by_pathology = filtered_df.groupby('nom_pathologie')['AVG_duree_hospi'].mean().reset_index()
            duree_by_pathology = duree_by_pathology.sort_values(by='AVG_duree_hospi', ascending=True).tail(20)
            return px.bar(duree_by_pathology, x='AVG_duree_hospi', y='nom_pathologie', orientation='h')

        @output
        @render.plot
        def age_group_recourse():
            filtered_df = dashboard.df_tranche_age_hospi[
                dashboard.df_tranche_age_hospi['year'].isin(input.selected_years()) & 
                dashboard.df_tranche_age_hospi['nom_region'].isin(input.selected_departments())
            ]
            age_groups = ['tranche_age_1_4', 'tranche_age_5_14', 'tranche_age_15_24', 
                          'tranche_age_25_34', 'tranche_age_35_44', 'tranche_age_45_54', 
                          'tranche_age_55_64', 'tranche_age_65_74', 'tranche_age_75_84', 
                          'tranche_age_85_et_plus']
            recourse_by_age = filtered_df[age_groups].mean()
            return px.bar(x=recourse_by_age.index, y=recourse_by_age.values)

        @output
        @render.plot
        def department_map():
            filtered_df = dashboard.df_nbr_hospi[
                dashboard.df_nbr_hospi['year'].isin(input.selected_years()) & 
                dashboard.df_nbr_hospi['nom_departement'].isin(input.selected_departments())
            ]
            hospi_by_departement = filtered_df.groupby('nom_departement')['nbr_hospi'].sum().reset_index()
            return px.choropleth(
                hospi_by_departement,
                locations='nom_departement',
                color='nbr_hospi',
                color_continuous_scale="Viridis",
                title="Hospitalizations by Department"
            )

    return App(app_ui, server)

app = create_app()