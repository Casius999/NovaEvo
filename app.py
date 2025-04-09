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
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')

# Créer le dossier d'upload si nécessaire
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Importer les modules
from ocr.ocr_main import OCRProcessor
from obd2.obd_main import OBDManager
from nlp.nlp_main import AutoAssistantNLP
# from image_recognition import image_recognition_main
# from ecu_flash import ecu_flash_main
# from parts_finder import parts_finder_main

# Initialiser les gestionnaires des modules
ocr_processor = OCRProcessor()
obd_manager = OBDManager()
nlp_assistant = AutoAssistantNLP()

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
    """
    Endpoint pour le module OCR
    
    Accepte une image de carte grise, la traite avec l'OCR, et retourne les informations extraites
    """
    # Vérifier si une image a été envoyée
    if 'image' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'Aucune image fournie. Veuillez envoyer une image dans le champ "image".'
        }), 400
    
    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({
            'status': 'error',
            'message': 'Aucun fichier sélectionné'
        }), 400
    
    try:
        # Sauvegarder temporairement l'image
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
        image_file.save(image_path)
        
        # Traiter l'image avec OCR
        ocr_result = ocr_processor.process_image(image_path=image_path)
        
        # Extraire les informations du véhicule
        if 'error' not in ocr_result:
            vehicle_info = ocr_processor.extract_vehicle_info(ocr_result)
            return jsonify(vehicle_info)
        else:
            return jsonify({
                'status': 'error',
                'message': ocr_result['error']
            }), 500
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors du traitement de l\'image: {str(e)}'
        }), 500
    finally:
        # Nettoyer le fichier temporaire
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except:
            pass  # Ignorer les erreurs de nettoyage

@app.route('/obd2', methods=['GET'])
def obd2_endpoint():
    """Endpoint pour le module OBD-II"""
    try:
        # Récupérer les données du véhicule via le module OBD-II
        data = get_vehicle_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la récupération des données OBD-II: {str(e)}'
        }), 500

def get_vehicle_data():
    """
    Fonction pour récupérer les données du véhicule via OBD-II
    
    Returns:
        dict: Données du véhicule (RPM, vitesse, codes d'erreur)
    """
    # Tenter de se connecter au dongle OBD-II
    connected = obd_manager.connect()
    
    # Préparer la structure de retour
    data = {}
    
    # Si la connexion échoue
    if not connected:
        return {
            "error": "Connexion OBD-II échouée. Vérifiez que le dongle est bien connecté et que le moteur est allumé."
        }
    
    try:
        # Récupérer le régime moteur (RPM)
        rpm_data = obd_manager.get_rpm()
        if "error" not in rpm_data:
            data["RPM"] = rpm_data.get("value", "Non disponible")
        else:
            data["RPM"] = "Non disponible"
        
        # Récupérer la vitesse
        speed_data = obd_manager.get_speed()
        if "error" not in speed_data:
            data["Speed"] = speed_data.get("value", "Non disponible")
        else:
            data["Speed"] = "Non disponible"
        
        # Récupérer les codes d'erreur (DTC)
        dtc_data = obd_manager.get_dtc_codes()
        if "error" not in dtc_data:
            if dtc_data.get("codes", []):
                data["DTC"] = dtc_data.get("codes", [])
            else:
                data["DTC"] = "Aucun code détecté"
        else:
            data["DTC"] = "Non disponible"
        
        return data
    
    finally:
        # S'assurer de fermer la connexion
        obd_manager.disconnect()

@app.route('/nlp', methods=['POST'])
def nlp_endpoint():
    """
    Endpoint pour le module NLP
    
    Accepte une commande en langage naturel et retourne une interprétation/réponse
    """
    # Vérifier si les données sont présentes dans la requête
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Requête invalide. Veuillez envoyer un JSON avec le champ "command".'
        }), 400
    
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Aucune commande trouvée dans la requête. Le champ "command" est requis.'
        }), 400
    
    # Récupérer la commande
    command = data['command']
    
    try:
        # Traiter la commande avec le module NLP
        response = process_command(command)
        
        # Retourner la réponse
        return jsonify({
            'status': 'success',
            'response': response
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors du traitement de la commande: {str(e)}'
        }), 500

def process_command(command: str) -> str:
    """
    Traite une commande en langage naturel et retourne une réponse
    
    Args:
        command (str): La commande en langage naturel
        
    Returns:
        str: La réponse générée par l'assistant
    """
    # Utiliser notre assistant NLP pour interpréter la commande
    result = nlp_assistant.interpret_command(command)
    
    # Si une erreur est détectée
    if "error" in result:
        return f"Je n'ai pas pu traiter votre demande : {result['error']}"
    
    # Si c'est un code d'erreur ou une demande d'entretien, on peut utiliser directement la description
    if "description" in result:
        return result["description"]
    
    # Pour les autres types de requêtes, utiliser le module OpenAI pour générer une réponse
    system_prompt = """
    Tu es un assistant automobile expert qui répond aux questions des utilisateurs.
    Ta réponse doit être informative, précise et sécuritaire.
    Pour les modifications mécaniques, mentionne toujours les précautions de sécurité.
    """
    
    try:
        # Créer un message pour OpenAI qui inclut la catégorie détectée
        context = f"L'utilisateur pose une question dans la catégorie: {result.get('category', 'générale')}"
        if "intent" in result:
            context += f", avec l'intention de: {result['intent']}"
        if "entities" in result:
            for key, value in result["entities"].items():
                context += f"\n- {key}: {value}"
        
        # Utiliser OpenAI pour générer une réponse plus complète
        import openai
        response = openai.chat.completions.create(
            model=nlp_assistant.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{context}\n\nQuestion: {command}"}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        # Extraire la réponse
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # En cas d'erreur avec OpenAI, utiliser les informations extraites
        fallback_response = f"Catégorie détectée: {result.get('category', 'inconnue')}"
        if "suggested_action" in result:
            fallback_response += f"\nSuggestion: {result['suggested_action']}"
        
        return fallback_response

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
