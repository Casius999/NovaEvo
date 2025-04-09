"""
Assistant Auto Ultime - Application Principale
"""
import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Initialiser l'application Flask
app = Flask(__name__)
CORS(app)  # Activer CORS pour toutes les routes

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')
app.config['DEBUG'] = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

# Importer les modules (à mesure qu'ils sont développés)
# from ocr import ocr_main
# from obd2 import obd_main
# from nlp import nlp_main
# from image_recognition import image_recognition_main
# from ecu_flash import ecu_flash_main
# from parts_finder import parts_finder_main

# Routes principales

@app.route('/')
def index():
    """Route principale - Page d'accueil"""
    return jsonify({
        'status': 'success',
        'message': 'API Assistant Auto Ultime opérationnelle',
        'modules': [
            '/ocr', '/obd2', '/nlp', '/image_recognition', 
            '/ecu_flash', '/parts_finder'
        ]
    })

# Routes pour chaque module

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    """Endpoint pour le module OCR"""
    # Pour le moment, simuler une réponse
    return jsonify({
        'status': 'success',
        'message': 'Module OCR prêt à recevoir des images',
        'endpoint': '/ocr'
    })

@app.route('/obd2', methods=['GET'])
def obd2_endpoint():
    """Endpoint pour le module OBD-II"""
    return jsonify({
        'status': 'success',
        'message': 'Module OBD-II prêt à se connecter',
        'endpoint': '/obd2'
    })

@app.route('/nlp', methods=['POST'])
def nlp_endpoint():
    """Endpoint pour le module NLP"""
    query = request.json.get('query', '')
    return jsonify({
        'status': 'success',
        'message': f'Module NLP a reçu: {query}',
        'endpoint': '/nlp'
    })

@app.route('/image_recognition', methods=['POST'])
def image_recognition_endpoint():
    """Endpoint pour le module de reconnaissance d'image"""
    return jsonify({
        'status': 'success',
        'message': 'Module de reconnaissance d\'image prêt à analyser',
        'endpoint': '/image_recognition'
    })

@app.route('/ecu_flash', methods=['GET', 'POST'])
def ecu_flash_endpoint():
    """Endpoint pour le module ECU Flash"""
    return jsonify({
        'status': 'success',
        'message': 'Module ECU Flash initialisé',
        'endpoint': '/ecu_flash'
    })

@app.route('/parts_finder', methods=['GET'])
def parts_finder_endpoint():
    """Endpoint pour le module de recherche de pièces"""
    part_type = request.args.get('type', 'all')
    return jsonify({
        'status': 'success',
        'message': f'Recherche de pièces de type: {part_type}',
        'endpoint': '/parts_finder'
    })

# Fonction principale
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
