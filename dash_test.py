import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from google.cloud import bigquery

# BigQuery Data Loading
def load_data():
    try:
        service_account_path = "projet-jbn-data-le-wagon-533639ce801d.json"

        # Initialize BigQuery client with service account key file
        client = bigquery.Client.from_service_account_json(service_account_path)


        # Load datasets
        df_nbr_hospi = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.morbidite_h.nbr_hospi_intermediate`
        ''').to_dataframe()

        df_duree_hospi = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.duree_hospitalisation_par_patho.duree_hospi_region_et_dpt_clean_classifie`
        ''').to_dataframe()

        df_tranche_age_hospi = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.morbidite_h.tranche_age_intermediate`
        ''').to_dataframe()

        df_capacite_hospi = client.query('''
            SELECT * FROM `projet-jbn-data-le-wagon.capacite_services_h.capacite_etablissement_intermediate_class`
        ''').to_dataframe()

        return df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi

    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None, None

# Calculate main metrics
def calculate_main_metrics(df_nbr_hospi, df_capacite_hospi):
    metrics = {}
    
    # Convertir les dates en années
    df_nbr_hospi['year'] = pd.to_datetime(df_nbr_hospi['year']).dt.year
    df_capacite_hospi['year'] = pd.to_datetime(df_capacite_hospi['year']).dt.year
    
    for year in range(2018, 2023):
        # Hospitalisations by year
        total_hospi = df_nbr_hospi[df_nbr_hospi['year'] == year]['nbr_hospi'].sum()
        metrics[f"hospi_{year}"] = total_hospi

        # Available beds by year
        lits_disponibles = df_capacite_hospi[df_capacite_hospi['year'] == year]['total_lit_hospi_complete'].sum()
        metrics[f"lits_{year}"] = lits_disponibles
    
    return metrics
# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load data
df_nbr_hospi, df_duree_hospi, df_tranche_age_hospi, df_capacite_hospi = load_data()
main_metrics = calculate_main_metrics(df_nbr_hospi, df_capacite_hospi)

# App layout
app.layout = dbc.Container([
    html.H1("🏥 Dashboard d'Analyse Hospitalière", className="text-center my-4"),
    
    # Filters
    dbc.Row([
        dbc.Col([
            html.H4("Filtres"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in sorted(df_nbr_hospi['year'].unique())],
                multi=True,
                value=sorted(df_nbr_hospi['year'].unique()),
                placeholder="Sélectionner les années"
            ),
            dcc.Dropdown(
                id='department-dropdown',
                options=[{'label': dept, 'value': dept} for dept in sorted(df_nbr_hospi['nom_departement'].unique())],
                multi=True,
                value=sorted(df_nbr_hospi['nom_departement'].unique()),
                placeholder="Sélectionner les départements"
            )
        ], width=3)
    ]),
    
    # Tabs
    dbc.Tabs([
        dbc.Tab(label="Vue Générale", children=[
            # Hospitalisations metrics
            dbc.Row([
                dbc.Col(html.Div(id='hospi-metrics'), width=12)
            ]),
            # Temporal trends
            dbc.Row([
                dbc.Col(dcc.Graph(id='hospi-by-year-chart'), width=6),
                dbc.Col(dcc.Graph(id='duration-by-year-chart'), width=6)
            ])
        ]),
        dbc.Tab(label="Analyse Géographique", children=[
            dbc.Row([
                dbc.Col(dcc.Graph(id='hospi-by-department-chart'), width=6),
                dbc.Col(dcc.Graph(id='duration-by-department-chart'), width=6)
            ])
        ]),
        dbc.Tab(label="Pathologies", children=[
            dbc.Row([
                dbc.Col(dcc.Graph(id='top-pathologies-chart'), width=12),
                dbc.Col(dcc.Graph(id='pathology-duration-chart'), width=12)
            ])
        ]),
        dbc.Tab(label="Démographie", children=[
            dbc.Row([
                dbc.Col(dcc.Graph(id='age-groups-chart'), width=12)
            ])
        ])
    ])
], fluid=True)

# Callback for dynamic charts
@app.callback(
    [Output('hospi-metrics', 'children'),
     Output('hospi-by-year-chart', 'figure'),
     Output('duration-by-year-chart', 'figure'),
     Output('hospi-by-department-chart', 'figure'),
     Output('duration-by-department-chart', 'figure'),
     Output('top-pathologies-chart', 'figure'),
     Output('pathology-duration-chart', 'figure'),
     Output('age-groups-chart', 'figure')],
    [Input('year-dropdown', 'value'),
     Input('department-dropdown', 'value')]
)
def update_dashboard(selected_years, selected_departments):
    # Filter DataFrames
    df_nbr_hospi_filtered = df_nbr_hospi[
        df_nbr_hospi['year'].isin(selected_years) & 
        df_nbr_hospi['nom_departement'].isin(selected_departments)
    ]
    df_duree_hospi_filtered = df_duree_hospi[
        df_duree_hospi['year'].isin(selected_years) & 
        df_duree_hospi['nom_departement_region'].isin(selected_departments)
    ]
    df_tranche_age_hospi_filtered = df_tranche_age_hospi[
        df_tranche_age_hospi['year'].isin(selected_years) & 
        df_tranche_age_hospi['nom_region'].isin(selected_departments)
    ]

    # Hospitalisations metrics
    metrics_cards = [
        dbc.Card(
            dbc.CardBody([
                html.H4(f"Hospitalisations {year}", className="card-title"),
                html.P(f"{main_metrics[f'hospi_{year}'] / 1_000_000:.2f}M", className="card-text")
            ]),
            className="mb-3"
        ) for year in selected_years
    ]
    
    # Hospitalisations by year
    hospi_by_year = df_nbr_hospi_filtered.groupby('year')['nbr_hospi'].sum().reset_index()
    hospi_chart = px.line(hospi_by_year, x='year', y='nbr_hospi', title='Nombre d\'hospitalisations par année')
    
    # Duration by year
    duree_by_year = df_duree_hospi_filtered.groupby('year')['AVG_duree_hospi'].mean().reset_index()
    duree_chart = px.line(duree_by_year, x='year', y='AVG_duree_hospi', title='Durée moyenne des hospitalisations')
    
    # Hospitalisations by department
    hospi_by_departement = df_nbr_hospi_filtered.groupby('nom_departement')['nbr_hospi'].sum().reset_index()
    hospi_dept_chart = px.bar(hospi_by_departement, x='nom_departement', y='nbr_hospi', 
                               title='Hospitalisations par département', orientation='v')
    
    # Duration by department
    duree_by_departement = df_duree_hospi_filtered.groupby('nom_departement_region')['AVG_duree_hospi'].mean().reset_index()
    duree_dept_chart = px.bar(duree_by_departement, x='nom_departement_region', y='AVG_duree_hospi', 
                               title='Durée moyenne par département', orientation='v')
    
    # Top pathologies by hospitalizations
    hospi_by_pathology = df_nbr_hospi_filtered.groupby('nom_pathologie')['nbr_hospi'].sum().nlargest(20).reset_index()
    top_pathologies_chart = px.bar(hospi_by_pathology, x='nom_pathologie', y='nbr_hospi', 
                                    title='Top 20 Pathologies par nombre d\'hospitalisations')
    
    # Pathology duration
    duree_by_pathology = df_duree_hospi_filtered.groupby('nom_pathologie')['AVG_duree_hospi'].mean().nlargest(20).reset_index()
    pathology_duration_chart = px.bar(duree_by_pathology, x='nom_pathologie', y='AVG_duree_hospi', 
                                       title='Top 20 Pathologies par durée moyenne')
       
    # Age groups
    age_groups = ['tranche_age_1_4', 'tranche_age_5_14', 'tranche_age_15_24', 
                  'tranche_age_25_34', 'tranche_age_35_44', 'tranche_age_45_54', 
                  'tranche_age_55_64', 'tranche_age_65_74', 'tranche_age_75_84', 
                  'tranche_age_85_et_plus']
    recourse_by_age = df_tranche_age_hospi_filtered[age_groups].mean()
    age_chart = px.bar(x=recourse_by_age.index, y=recourse_by_age.values, 
                       title='Taux de recours par tranche d\'âge')

    return metrics_cards, hospi_chart, duree_chart, hospi_dept_chart, \
           duree_dept_chart, top_pathologies_chart, pathology_duration_chart, age_chart


if __name__ == '__main__':
    app.run_server(debug=True)