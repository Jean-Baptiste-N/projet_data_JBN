from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from google.cloud import bigquery
import os
import pandas as pd
import numpy as np
import json
import logging
import traceback

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.')
CORS(app)

# Configuration de BigQuery
credentials_path = 'projet-jbn-data-le-wagon-533639ce801d.json'

# Vérifier que le fichier de credentials existe
if not os.path.exists(credentials_path):
    logger.error(f"Le fichier de credentials '{credentials_path}' n'existe pas!")
    raise FileNotFoundError(f"Le fichier de credentials '{credentials_path}' n'existe pas!")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

try:
    client = bigquery.Client()
    # Test de connexion
    client.query("SELECT 1").result()
    logger.info("Connexion à BigQuery établie avec succès")
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation de BigQuery: {str(e)}")
    logger.error(traceback.format_exc())
    raise

def clean_dataframe(df):
    try:
        # Remplacer les valeurs NaN par None pour une sérialisation JSON correcte
        cleaned_df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
        # Convertir les types numpy en types Python standards
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype.name.startswith(('int', 'float')):
                cleaned_df[col] = cleaned_df[col].astype(float)
        return cleaned_df
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage du DataFrame: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.route('/')
def serve_dashboard():
    return send_from_directory('.', 'd3-hospital-dashboard.html')

@app.route('/api/hospitalizations')
def get_hospitalizations():
    query = '''
        SELECT * 
        FROM `projet-jbn-data-le-wagon.morbidite_h.nbr_hospi_intermediate`
    '''
    try:
        logger.info("Exécution de la requête hospitalizations")
        df = client.query(query).to_dataframe()
        logger.info(f"Données récupérées: {len(df)} lignes")
        df = clean_dataframe(df)
        result = df.to_dict(orient='records')
        return jsonify(result)
    except Exception as e:
        error_msg = f"Erreur dans get_hospitalizations: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({'error': error_msg}), 500

@app.route('/api/duration')
def get_duration():
    query = '''
        SELECT * 
        FROM `projet-jbn-data-le-wagon.duree_hospitalisation_par_patho.duree_hospi_region_et_dpt_clean_classifie`
    '''
    try:
        logger.info("Exécution de la requête duration")
        df = client.query(query).to_dataframe()
        logger.info(f"Données récupérées: {len(df)} lignes")
        df = clean_dataframe(df)
        result = df.to_dict(orient='records')
        return jsonify(result)
    except Exception as e:
        error_msg = f"Erreur dans get_duration: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({'error': error_msg}), 500

@app.route('/api/demographics')
def get_demographics():
    query = '''
        SELECT * 
        FROM `projet-jbn-data-le-wagon.morbidite_h.tranche_age_intermediate`
    '''
    try:
        logger.info("Exécution de la requête demographics")
        df = client.query(query).to_dataframe()
        logger.info(f"Données récupérées: {len(df)} lignes")
        df = clean_dataframe(df)
        result = df.to_dict(orient='records')
        return jsonify(result)
    except Exception as e:
        error_msg = f"Erreur dans get_demographics: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({'error': error_msg}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    logger.info("Démarrage du serveur sur http://localhost:8000")
    app.run(host='localhost', port=8000, debug=True)
