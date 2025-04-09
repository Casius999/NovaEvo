"""
NovaEvo - Application Principale
"""
import os
import json
import logging
import requests
import threading
import time
from datetime import datetime
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
app.config['CONTEXT_SERVERS'] = os.getenv('CONTEXT_SERVERS', '').split(',')
app.config['SYNC_INTERVAL'] = int(os.getenv('SYNC_INTERVAL', '300'))  # En secondes, défaut: 5 minutes

# Créer le dossier d'upload si nécessaire
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuration du logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_file = os.getenv('LOG_FILE', 'logs/novaevo.log')

# Créer le dossier de logs si nécessaire
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Configuration du logger
logger = logging.getLogger('novaevo')
logger.setLevel(getattr(logging, log_level))

# Handler pour le fichier
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Handler pour la console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Intégration de Sentry pour le monitoring des erreurs
if os.getenv('SENTRY_DSN'):
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        environment=os.getenv('ENVIRONMENT', 'development')
    )
    logger.info("Sentry initialized for error tracking")

# Importer les modules
from ocr.ocr_main import OCRProcessor
from obd2.obd_main import OBDManager
from nlp.nlp_main import AutoAssistantNLP
from image_recognition.image_recognition_main import ImageRecognitionEngine, detect_labels
from ecu_flash.ecu_flash_main import flash_ecu, ECUFlashManager
from parts_finder.parts_finder_main import PartsFinderManager, search_parts

# Nouveaux modules
from subscriptions.subscriptions_main import process_subscription, app as subscriptions_app, webhook_handler

# Dictionnaire pour stocker les modules contextuels
context_modules = {}
context_data = {}
sync_running = False

class ContextModuleManager:
    """
    Gestionnaire pour les modules contextuels.
    Permet de charger, synchroniser et accéder aux données contextuelles
    depuis des serveurs dédiés.
    """
    
    def __init__(self):
        self.modules = {}
        self.last_sync = {}
        self.sync_interval = app.config['SYNC_INTERVAL']
        
    def register_module(self, module_id, server_url, api_key=None):
        """
        Enregistre un nouveau module contextuel
        
        Args:
            module_id (str): Identifiant unique du module
            server_url (str): URL du serveur dédié
            api_key (str, optional): Clé API pour l'authentification
        """
        self.modules[module_id] = {
            'server_url': server_url,
            'api_key': api_key,
            'data': {},
            'last_sync': None,
            'status': 'registered'
        }
        logger.info(f"Module contextuel enregistré: {module_id} -> {server_url}")
        
    def sync_module(self, module_id):
        """
        Synchronise les données d'un module spécifique avec son serveur
        
        Args:
            module_id (str): Identifiant du module à synchroniser
            
        Returns:
            bool: True si la synchronisation a réussi, False sinon
        """
        if module_id not in self.modules:
            logger.error(f"Tentative de synchronisation d'un module non enregistré: {module_id}")
            return False
            
        module = self.modules[module_id]
        
        try:
            headers = {}
            if module['api_key']:
                headers['Authorization'] = f"Bearer {module['api_key']}"
                
            # Récupérer les données du serveur
            response = requests.get(
                f"{module['server_url']}/api/data",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                module['data'] = response.json()
                module['last_sync'] = datetime.now()
                module['status'] = 'active'
                
                logger.info(f"Module {module_id} synchronisé avec succès")
                return True
            else:
                logger.warning(f"Échec de synchronisation du module {module_id}: {response.status_code}")
                module['status'] = 'error'
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation du module {module_id}: {str(e)}")
            module['status'] = 'error'
            return False
            
    def sync_all_modules(self):
        """
        Synchronise tous les modules enregistrés
        
        Returns:
            dict: Résultats de synchronisation par module
        """
        results = {}
        for module_id in self.modules:
            results[module_id] = self.sync_module(module_id)
            
        return results
        
    def get_context_data(self, module_id, path=None):
        """
        Récupère les données contextuelles d'un module
        
        Args:
            module_id (str): Identifiant du module
            path (str, optional): Chemin d'accès spécifique dans les données
            
        Returns:
            dict/any: Données contextuelles demandées
        """
        if module_id not in self.modules:
            logger.warning(f"Tentative d'accès à un module non enregistré: {module_id}")
            return None
            
        module = self.modules[module_id]
        
        # Vérifier si une synchronisation est nécessaire
        if module['last_sync'] is None:
            self.sync_module(module_id)
        elif (datetime.now() - module['last_sync']).total_seconds() > self.sync_interval:
            # Synchronisation en arrière-plan si les données sont trop anciennes
            threading.Thread(target=self.sync_module, args=(module_id,)).start()
            
        # Retourner les données demandées
        if path:
            # Naviguer dans la structure de données selon le chemin
            data = module['data']
            for key in path.split('.'):
                if isinstance(data, dict) and key in data:
                    data = data[key]
                else:
                    return None
            return data
        else:
            return module['data']

    def start_background_sync(self):
        """
        Démarre la synchronisation périodique en arrière-plan
        """
        def sync_worker():
            while True:
                self.sync_all_modules()
                time.sleep(self.sync_interval)
                
        thread = threading.Thread(target=sync_worker, daemon=True)
        thread.start()
        logger.info("Synchronisation en arrière-plan démarrée")
        
# Initialiser le gestionnaire de modules contextuels
context_manager = ContextModuleManager()

# Enregistrer les modules contextuels depuis la configuration
for server_url in app.config['CONTEXT_SERVERS']:
    if server_url:
        module_id = server_url.split('/')[-1].replace('.', '_')
        api_key = os.getenv(f"API_KEY_{module_id.upper()}")
        context_manager.register_module(module_id, server_url, api_key)

# Initialiser les gestionnaires des modules
ocr_processor = OCRProcessor()
obd_manager = OBDManager()
nlp_assistant = AutoAssistantNLP()
image_recognition_engine = ImageRecognitionEngine()
ecu_flash_manager = ECUFlashManager()
parts_finder_manager = PartsFinderManager()

# Démarrer la synchronisation en arrière-plan si des modules sont configurés
if context_manager.modules:
    context_manager.start_background_sync()

# Routes principales

@app.route('/')
def index():
    """Route principale - Page d'accueil"""
    return jsonify({
        'status': 'success',
        'message': 'API NovaEvo opérationnelle',
        'modules': [
            '/ocr', '/obd2', '/nlp', '/image_recognition', 
            '/ecu_flash', '/parts_finder', '/subscriptions', '/mapping_affiliations',
            '/feedback', '/context_modules'  # Nouvelle route pour les modules contextuels
        ]
    })

# Nouvelle route pour les modules contextuels
@app.route('/context_modules', methods=['GET'])
def list_context_modules():
    """
    Liste tous les modules contextuels disponibles et leur statut
    """
    result = {}
    for module_id, module in context_manager.modules.items():
        result[module_id] = {
            'status': module['status'],
            'last_sync': module['last_sync'].isoformat() if module['last_sync'] else None,
            'server_url': module['server_url']
        }
    
    return jsonify({
        'status': 'success',
        'modules': result
    })

@app.route('/context_modules/<module_id>', methods=['GET'])
def get_module_data(module_id):
    """
    Récupère les données d'un module contextuel spécifique
    """
    path = request.args.get('path')
    data = context_manager.get_context_data(module_id, path)
    
    if data is None:
        return jsonify({
            'status': 'error',
            'message': f'Module {module_id} non trouvé ou données indisponibles'
        }), 404
        
    return jsonify({
        'status': 'success',
        'module_id': module_id,
        'path': path,
        'data': data
    })

@app.route('/context_modules/<module_id>/sync', methods=['POST'])
def sync_module(module_id):
    """
    Force la synchronisation d'un module contextuel
    """
    if module_id not in context_manager.modules:
        return jsonify({
            'status': 'error',
            'message': f'Module {module_id} non trouvé'
        }), 404
        
    success = context_manager.sync_module(module_id)
    
    if success:
        return jsonify({
            'status': 'success',
            'message': f'Module {module_id} synchronisé avec succès',
            'last_sync': context_manager.modules[module_id]['last_sync'].isoformat()
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Échec de la synchronisation du module {module_id}'
        }), 500

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
            
            # Enrichir avec des données contextuelles si disponibles
            try:
                if 'immatriculation' in vehicle_info and 'vehicles_data' in context_manager.modules:
                    immat = vehicle_info['immatriculation']
                    extra_data = context_manager.get_context_data('vehicles_data', f'registrations.{immat}')
                    if extra_data:
                        vehicle_info['context_data'] = extra_data
                        logger.info(f"Données contextuelles ajoutées pour {immat}")
            except Exception as context_err:
                logger.warning(f"Impossible d'ajouter des données contextuelles: {str(context_err)}")
                
            return jsonify(vehicle_info)
        else:
            return jsonify({
                'status': 'error',
                'message': ocr_result['error']
            }), 500
    
    except Exception as e:
        logger.error(f"Erreur lors du traitement OCR: {str(e)}")
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
        logger.error(f"Erreur OBD-II: {str(e)}")
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
        
        # Ajouter des données contextuelles pour les codes d'erreur
        if "DTC" in data and isinstance(data["DTC"], list) and len(data["DTC"]) > 0:
            try:
                dtc_context = []
                for code in data["DTC"]:
                    if 'dtc_database' in context_manager.modules:
                        code_data = context_manager.get_context_data('dtc_database', f'codes.{code}')
                        if code_data:
                            dtc_context.append({
                                'code': code,
                                'description': code_data.get('description', ''),
                                'severity': code_data.get('severity', 'unknown'),
                                'possible_causes': code_data.get('causes', []),
                                'recommended_actions': code_data.get('actions', [])
                            })
                
                if dtc_context:
                    data["DTC_details"] = dtc_context
            except Exception as context_err:
                logger.warning(f"Erreur lors de l'ajout des contextes DTC: {str(context_err)}")
        
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
    
    # Obtenir le contexte utilisateur si disponible
    user_id = data.get('user_id')
    vehicle_id = data.get('vehicle_id')
    
    try:
        # Traiter la commande avec le module NLP
        response = process_command(command, user_id, vehicle_id)
        
        # Retourner la réponse
        return jsonify({
            'status': 'success',
            'response': response
        })
        
    except Exception as e:
        logger.error(f"Erreur NLP: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors du traitement de la commande: {str(e)}'
        }), 500

def process_command(command: str, user_id=None, vehicle_id=None) -> str:
    """
    Traite une commande en langage naturel et retourne une réponse
    
    Args:
        command (str): La commande en langage naturel
        user_id (str, optional): ID de l'utilisateur pour la personnalisation
        vehicle_id (str, optional): ID du véhicule pour la personnalisation
        
    Returns:
        str: La réponse générée par l'assistant
    """
    # Obtenir le contexte utilisateur et véhicule si disponible
    user_context = {}
    vehicle_context = {}
    
    if user_id and 'users_data' in context_manager.modules:
        user_context = context_manager.get_context_data('users_data', f'users.{user_id}') or {}
        
    if vehicle_id and 'vehicles_data' in context_manager.modules:
        vehicle_context = context_manager.get_context_data('vehicles_data', f'vehicles.{vehicle_id}') or {}
    
    # Adapter le modèle NLP en fonction du contexte
    if user_context.get('expertise_level') == 'expert':
        nlp_assistant.set_expertise_level('expert')
    elif user_context.get('expertise_level') == 'beginner':
        nlp_assistant.set_expertise_level('beginner')
    else:
        nlp_assistant.set_expertise_level('intermediate')  # Valeur par défaut
    
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
    
    # Ajouter le contexte utilisateur et véhicule au prompt système
    if user_context or vehicle_context:
        system_prompt += "\n\nInformations contextuelles :"
        
        if user_context:
            system_prompt += f"\n- Utilisateur: Niveau d'expertise '{user_context.get('expertise_level', 'intermédiaire')}'"
            if 'preferences' in user_context:
                system_prompt += f"\n- Préférences: {', '.join(user_context['preferences'])}"
        
        if vehicle_context:
            system_prompt += f"\n- Véhicule: {vehicle_context.get('make', '')} {vehicle_context.get('model', '')}, année {vehicle_context.get('year', '')}"
            system_prompt += f"\n- Moteur: {vehicle_context.get('engine_type', '')}, {vehicle_context.get('engine_power', '')} ch"
    
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
        logger.error(f"Erreur OpenAI: {str(e)}")
        # En cas d'erreur avec OpenAI, utiliser les informations extraites
        fallback_response = f"Catégorie détectée: {result.get('category', 'inconnue')}"
        if "suggested_action" in result:
            fallback_response += f"\nSuggestion: {result['suggested_action']}"
        
        return fallback_response

@app.route('/image_recognition', methods=['POST'])
def image_recognition_endpoint():
    """
    Endpoint pour le module de reconnaissance d'image
    
    Accepte une image et retourne l'analyse des labels détectés via Google Cloud Vision
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
        
        # Déterminer le type d'analyse à effectuer (standard ou avancée)
        analysis_type = request.args.get('type', 'standard')
        
        if analysis_type == 'advanced':
            # Utiliser la classe pour une analyse complète (OpenCV + Vision API)
            results = image_recognition_engine.detect_labels(image_path)
        else:
            # Utiliser la fonction autonome pour la détection simple de labels
            results = detect_labels(image_path)
        
        # Enrichir avec des données contextuelles
        if 'parts_database' in context_manager.modules and results.get('labels'):
            try:
                for i, label in enumerate(results['labels']):
                    label_key = label['description'].lower().replace(' ', '_')
                    part_data = context_manager.get_context_data('parts_database', f'parts.{label_key}')
                    if part_data:
                        results['labels'][i]['context_data'] = part_data
            except Exception as context_err:
                logger.warning(f"Erreur lors de l'enrichissement des détections: {str(context_err)}")
        
        # Retourner les résultats
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Erreur reconnaissance d'image: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de l\'analyse de l\'image: {str(e)}'
        }), 500
    finally:
        # Nettoyer le fichier temporaire
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except:
            pass  # Ignorer les erreurs de nettoyage

@app.route('/ecu_flash', methods=['POST'])
def ecu_flash_endpoint():
    """
    Endpoint pour le module ECU Flash
    
    Accepte un JSON contenant les paramètres de tuning et les envoie au module de flashage ECU
    """
    # Vérifier si les données sont présentes dans la requête
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Requête invalide. Veuillez envoyer un JSON avec les paramètres de tuning.'
        }), 400
    
    tuning_parameters = request.get_json()
    if not tuning_parameters:
        return jsonify({
            'status': 'error',
            'message': 'Aucun paramètre de tuning fourni.'
        }), 400
    
    # Utiliser la fonction flash_ecu pour appliquer les paramètres
    try:
        # Loguer l'opération pour suivi et audit
        logger.info(f"Tentative de flash ECU avec paramètres: {json.dumps(tuning_parameters)}")
        
        # Vérifier si le véhicule est compatible via le module contextuel
        if 'vehicle_id' in tuning_parameters and 'ecu_compatibility' in context_manager.modules:
            vehicle_id = tuning_parameters['vehicle_id']
            compatibility = context_manager.get_context_data('ecu_compatibility', f'vehicles.{vehicle_id}')
            
            if compatibility:
                if not compatibility.get('compatible', True):
                    return jsonify({
                        'status': 'error',
                        'message': f"Véhicule incompatible: {compatibility.get('reason', 'Non spécifié')}"
                    }), 400
                    
                # Ajouter des limites spécifiques au véhicule
                if 'safe_limits' in compatibility:
                    for param, limit in compatibility['safe_limits'].items():
                        if param in tuning_parameters and tuning_parameters[param] > limit:
                            tuning_parameters[param] = limit
                            logger.warning(f"Paramètre {param} limité à {limit} pour la sécurité")
        
        result = flash_ecu(tuning_parameters)
        
        # Ajouter entrée dans les metrics de performance
        try:
            log_performance_metrics(tuning_parameters, result.get('success', False))
        except Exception as metrics_err:
            logger.error(f"Erreur lors de l'enregistrement des métriques: {str(metrics_err)}")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur ECU flash: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors du flash ECU: {str(e)}'
        }), 500

def log_performance_metrics(parameters, success):
    """
    Enregistre les métriques de performance pour l'analyse
    
    Args:
        parameters (dict): Paramètres utilisés pour le flash
        success (bool): Si l'opération a réussi
    """
    metrics_dir = os.path.join('data', 'metrics')
    os.makedirs(metrics_dir, exist_ok=True)
    
    metrics_file = os.path.join(metrics_dir, 'ecu_performance.json')
    
    # Charger les métriques existantes ou créer une nouvelle structure
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)
    else:
        metrics = {
            'flashes': [],
            'success_rate': 0,
            'total_flashes': 0,
            'successful_flashes': 0
        }
    
    # Ajouter la nouvelle entrée
    timestamp = datetime.now().isoformat()
    metrics['flashes'].append({
        'timestamp': timestamp,
        'parameters': parameters,
        'success': success
    })
    
    # Mettre à jour les statistiques
    metrics['total_flashes'] += 1
    if success:
        metrics['successful_flashes'] += 1
    
    metrics['success_rate'] = metrics['successful_flashes'] / metrics['total_flashes']
    
    # Enregistrer les métriques mises à jour
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

@app.route('/ecu_flash/connect', methods=['POST'])
def ecu_flash_connect_endpoint():
    """
    Endpoint pour établir une connexion avec l'ECU
    """
    try:
        result = ecu_flash_manager.connect_ecu()
        if result.get('success', False):
            return jsonify(result)
        else:
            return jsonify(result), 500
    except Exception as e:
        logger.error(f"Erreur connexion ECU: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la connexion à l\'ECU: {str(e)}'
        }), 500

@app.route('/ecu_flash/read', methods=['GET'])
def ecu_flash_read_endpoint():
    """
    Endpoint pour lire la configuration actuelle de l'ECU
    """
    try:
        result = ecu_flash_manager.read_ecu()
        if "error" in result:
            return jsonify(result), 500
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur lecture ECU: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la lecture de l\'ECU: {str(e)}'
        }), 500

@app.route('/ecu_flash/parameters', methods=['GET'])
def ecu_flash_parameters_endpoint():
    """
    Endpoint pour récupérer les limites sécurisées des paramètres de tuning
    """
    from ecu_flash.ecu_flash_main import SECURE_LIMITS
    
    # Enrichir avec des données contextuelles si disponibles
    vehicle_id = request.args.get('vehicle_id')
    if vehicle_id and 'ecu_compatibility' in context_manager.modules:
        try:
            vehicle_limits = context_manager.get_context_data('ecu_compatibility', f'vehicles.{vehicle_id}.safe_limits')
            if vehicle_limits:
                # Fusionner les limites par défaut avec celles spécifiques au véhicule
                combined_limits = SECURE_LIMITS.copy()
                for param, limit in vehicle_limits.items():
                    if param in combined_limits:
                        combined_limits[param] = limit
                
                return jsonify({
                    'status': 'success',
                    'parameters': combined_limits,
                    'vehicle_specific': True
                })
        except Exception as e:
            logger.warning(f"Impossible de récupérer les limites spécifiques au véhicule: {str(e)}")
    
    return jsonify({
        'status': 'success',
        'parameters': SECURE_LIMITS,
        'vehicle_specific': False
    })

@app.route('/parts_finder', methods=['POST'])
def parts_finder_endpoint():
    """
    Endpoint pour le module de recherche de pièces
    
    Accepte une requête POST contenant reference et type, effectue la recherche
    multi-sources et retourne les résultats
    """
    # Vérifier si les données sont présentes dans la requête
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Requête invalide. Veuillez envoyer un JSON avec les paramètres requis.'
        }), 400
    
    data = request.get_json()
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Aucune donnée fournie.'
        }), 400
    
    reference = data.get("reference")
    type_piece = data.get("type")
    
    if not reference or not type_piece:
        return jsonify({
            'status': 'error',
            'message': 'Les paramètres "reference" et "type" sont obligatoires.'
        }), 400
    
    # Récupérer le contexte véhicule si disponible
    vehicle_id = data.get('vehicle_id')
    urgency = data.get('urgency', 'normal')
    
    # Lancer la recherche multi-sources
    try:
        # Planification automatique des rendez-vous en fonction de l'urgence
        planning_data = None
        
        if urgency in ['high', 'emergency'] and 'repair_shops' in context_manager.modules:
            try:
                # Trouver les créneaux disponibles en urgence
                planning_data = find_emergency_slots(vehicle_id, urgency)
            except Exception as planning_err:
                logger.warning(f"Erreur lors de la planification d'urgence: {str(planning_err)}")
        
        # Recherche standard des pièces
        offers = search_parts(reference, type_piece)
        
        # Vérifier s'il y a des erreurs
        errors = [offer for offer in offers if "error" in offer]
        if errors and len(errors) == len(offers):
            # Toutes les recherches ont échoué
            return jsonify({
                'status': 'error',
                'message': 'Toutes les recherches ont échoué',
                'errors': errors
            }), 500
        
        # Filtrer les erreurs avant de retourner les résultats
        offers = [offer for offer in offers if "error" not in offer]
        
        # Créer la réponse
        response = {
            'status': 'success',
            'count': len(offers),
            'reference': reference,
            'type': type_piece,
            'offers': offers
        }
        
        # Ajouter les informations de planification si disponibles
        if planning_data:
            response['emergency_planning'] = planning_data
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erreur recherche pièces: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la recherche de pièces: {str(e)}'
        }), 500

def find_emergency_slots(vehicle_id, urgency_level):
    """
    Trouve des créneaux d'urgence disponibles pour l'installation des pièces
    
    Args:
        vehicle_id (str): ID du véhicule
        urgency_level (str): Niveau d'urgence ('high' ou 'emergency')
        
    Returns:
        dict: Données de planification d'urgence
    """
    # Récupérer les données de garages à proximité
    if not vehicle_id:
        return None
        
    vehicle_data = context_manager.get_context_data('vehicles_data', f'vehicles.{vehicle_id}')
    if not vehicle_data or 'location' not in vehicle_data:
        return None
        
    location = vehicle_data['location']
    
    # Rechercher les garages à proximité avec des créneaux disponibles
    shops_data = context_manager.get_context_data('repair_shops', 'shops')
    if not shops_data:
        return None
    
    # Filtrer les garages à proximité
    nearby_shops = []
    for shop in shops_data:
        if 'emergency_slots' in shop and len(shop['emergency_slots']) > 0:
            # Calculer la distance (simplifiée)
            distance = calculate_distance(location, shop['location'])
            if distance < 50:  # Moins de 50km
                nearby_shops.append({
                    'id': shop['id'],
                    'name': shop['name'],
                    'distance': distance,
                    'address': shop['address'],
                    'phone': shop['phone'],
                    'slots': shop['emergency_slots'][:3]  # Limiter à 3 créneaux
                })
    
    # Trier par distance
    nearby_shops.sort(key=lambda x: x['distance'])
    
    # Retourner les 3 garages les plus proches
    return {
        'urgency_level': urgency_level,
        'nearby_shops': nearby_shops[:3]
    }

def calculate_distance(loc1, loc2):
    """
    Calcule la distance entre deux points (simplifiée)
    """
    # Version simplifiée pour démonstration
    lat1, lon1 = loc1['latitude'], loc1['longitude']
    lat2, lon2 = loc2['latitude'], loc2['longitude']
    
    # Distance euclidienne approximative pour démonstration
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 111  # 111km par degré

@app.route('/parts_finder/local', methods=['GET'])
def parts_finder_local_endpoint():
    """
    Endpoint pour la recherche de pièces dans la base de données locale
    """
    # Extraire les paramètres de requête
    manufacturer = request.args.get('manufacturer')
    model = request.args.get('model')
    category = request.args.get('category')
    part_type = request.args.get('type')
    keyword = request.args.get('keyword')
    reference = request.args.get('reference')
    
    try:
        # Rechercher dans la base locale
        results = parts_finder_manager.search_parts_local(
            manufacturer=manufacturer,
            model=model,
            category=category,
            part_type=part_type,
            keyword=keyword,
            reference=reference
        )
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Erreur recherche locale: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la recherche locale: {str(e)}'
        }), 500

@app.route('/parts_finder/detail', methods=['GET'])
def parts_finder_detail_endpoint():
    """
    Endpoint pour obtenir les détails d'une pièce spécifique
    """
    part_id = request.args.get('id')
    reference = request.args.get('reference')
    
    if not part_id and not reference:
        return jsonify({
            'status': 'error',
            'message': 'ID ou référence de pièce requis.'
        }), 400
    
    try:
        # Récupérer les détails
        result = parts_finder_manager.get_part_details(
            part_id=int(part_id) if part_id else None,
            reference=reference
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur détails pièce: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la récupération des détails: {str(e)}'
        }), 500

# Endpoints pour le module d'abonnements

@app.route('/subscribe', methods=['POST'])
def subscribe_endpoint():
    """
    Endpoint pour le module de gestion des abonnements
    
    Accepte une requête POST avec les informations d'inscription (JSON avec "email" et "password")
    et lance la souscription Stripe à 19,90€/mois
    """
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Requête invalide. Veuillez envoyer un JSON avec les informations requises.'
        }), 400
    
    user_data = request.get_json()
    if not user_data or "email" not in user_data or "password" not in user_data:
        return jsonify({
            'status': 'error',
            'message': 'Les informations "email" et "password" sont obligatoires.'
        }), 400
    
    try:
        result = process_subscription(user_data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur souscription: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la souscription: {str(e)}'
        }), 500

@app.route('/subscribe/webhook', methods=['POST'])
def subscribe_webhook_endpoint():
    """
    Endpoint pour les webhooks Stripe
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    if not sig_header:
        return jsonify({
            'status': 'error',
            'message': 'En-tête Stripe-Signature manquant'
        }), 400
    
    try:
        result = webhook_handler(payload, sig_header)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur webhook: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors du traitement du webhook: {str(e)}'
        }), 500

@app.route('/subscribe/plans', methods=['GET'])
def subscription_plans_endpoint():
    """
    Endpoint pour récupérer les plans d'abonnement disponibles
    """
    plans = [
        {
            "id": "price_basic",
            "name": "Formule Standard",
            "price": 19.90,
            "currency": "EUR",
            "interval": "month",
            "description": "Abonnement mensuel à 19,90€ avec dongle OBD-II offert",
            "features": [
                "Diagnostic OBD-II en temps réel",
                "Reconnaissance de pièces par image",
                "Assistant NLP automobile",
                "Recherche de pièces détachées",
                "OCR pour cartes grises",
                "Cartographies moteur standard",
                "Dongle OBD-II inclus"
            ]
        },
        {
            "id": "price_premium",
            "name": "Formule Premium",
            "price": 29.90,
            "currency": "EUR",
            "interval": "month",
            "description": "Abonnement premium avec fonctionnalités avancées",
            "features": [
                "Toutes les fonctionnalités Standard",
                "Cartographies moteur avancées",
                "Flash ECU illimité",
                "Support technique prioritaire",
                "Dongle OBD-II Pro inclus",
                "Mise à jour hebdomadaire des bases de données"
            ]
        }
    ]
    
    return jsonify({
        "status": "success",
        "plans": plans
    })

# Endpoints pour le module Mapping Affiliations

@app.route('/mapping_affiliations', methods=['POST'])
def mapping_affiliations_endpoint():
    """
    Endpoint pour le module d'affiliation cartographies
    
    Accepte une requête POST avec un JSON contenant "query" et optionnellement "category"
    """
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Requête invalide. Veuillez envoyer un JSON avec les informations requises.'
        }), 400
    
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({
            'status': 'error',
            'message': 'Le paramètre "query" est obligatoire.'
        }), 400
    
    query = data["query"]
    category = data.get("category")
    session_id = data.get("session_id")
    user_id = data.get("user_id")
    
    # Ajouter des données de tracking pour l'affiliation
    tracking_data = {
        "session_id": session_id,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "category": category
    }
    
    # Import et utilisation du module mapping_affiliations
    try:
        from mapping_affiliations.mapping_affiliations_main import search_mapping_offers, track_search_activity
        
        # Enregistrer l'activité de recherche pour le suivi d'affiliation
        if session_id:
            track_search_activity(tracking_data)
            
        offers = search_mapping_offers(query, category)
        
        # Ajouter des paramètres de tracking aux liens d'affiliation
        if session_id:
            for offer in offers:
                if "affiliate_link" in offer:
                    separator = "&" if "?" in offer["affiliate_link"] else "?"
                    offer["affiliate_link"] += f"{separator}sid={session_id}"
                    if user_id:
                        offer["affiliate_link"] += f"&uid={user_id}"
        
        return jsonify({"offers": offers})
    
    except ImportError:
        # Si le module n'est pas encore disponible, retourner un exemple de données
        example_offers = [
            {
                "preparateur": "TuningBox France",
                "description": "Cartographie Stage 1 pour moteurs TSI 2.0L",
                "price": "249.90€",
                "affiliate_link": "https://tuningbox-france.com/cart/stage1-tsi?ref=novaevo",
                "category": category or "sport",
                "source": "API Partenaire"
            },
            {
                "preparateur": "DigiTech Performance",
                "description": "Reprogrammation origine pour économie de carburant",
                "price": "189.00€",
                "affiliate_link": "https://digitech-perf.fr/eco?ref=novaevo",
                "category": category or "origine",
                "source": "Facebook Marketplace"
            }
        ]
        
        # Ajouter des paramètres de tracking aux liens d'affiliation
        if session_id:
            for offer in example_offers:
                separator = "&" if "?" in offer["affiliate_link"] else "?"
                offer["affiliate_link"] += f"{separator}sid={session_id}"
                if user_id:
                    offer["affiliate_link"] += f"&uid={user_id}"
                    
        return jsonify({"offers": example_offers})
        
    except Exception as e:
        logger.error(f"Erreur recherche cartographies: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la recherche de cartographies: {str(e)}'
        }), 500

# Endpoint pour la collecte de feedback

@app.route('/feedback', methods=['POST'])
def feedback_endpoint():
    """
    Endpoint pour la collecte de feedback utilisateur
    
    Accepte les retours utilisateurs (commentaires, signalements de bugs, suggestions)
    et les stocke pour analyse ultérieure
    """
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Requête invalide. Veuillez envoyer un JSON avec les informations de feedback.'
        }), 400
    
    # Récupérer les données du feedback
    feedback_data = request.get_json()
    
    # Validation minimale des données
    if not feedback_data or 'message' not in feedback_data:
        return jsonify({
            'status': 'error',
            'message': 'Données de feedback incomplètes. Le champ "message" est requis.'
        }), 400
    
    # Ajouter un timestamp s'il n'est pas déjà présent
    if 'timestamp' not in feedback_data:
        feedback_data['timestamp'] = datetime.now().isoformat()
    
    # Structure pour stocker le feedback
    feedback_entry = {
        'type': feedback_data.get('type', 'comment'),
        'message': feedback_data['message'],
        'email': feedback_data.get('email', 'anonymous'),
        'timestamp': feedback_data['timestamp'],
        'source': feedback_data.get('source', 'unknown'),
        'user_agent': feedback_data.get('userAgent', 'not_provided'),
        'ip_address': request.remote_addr
    }
    
    try:
        # Créer le dossier de feedback s'il n'existe pas
        feedback_dir = os.path.join('data', 'feedback')
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Générer un nom de fichier unique
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"feedback_{timestamp_str}_{feedback_entry['type']}.json"
        file_path = os.path.join(feedback_dir, file_name)
        
        # Enregistrer le feedback dans un fichier JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(feedback_entry, f, ensure_ascii=False, indent=2)
        
        # Log le feedback pour suivi (version anonymisée)
        logger.info(f"Nouveau feedback reçu: Type={feedback_entry['type']}, Source={feedback_entry['source']}")
        
        # Mise à jour des métriques de qualité en temps réel
        try:
            update_quality_metrics(feedback_entry)
        except Exception as metrics_err:
            logger.warning(f"Erreur lors de la mise à jour des métriques: {str(metrics_err)}")
            
        # Notification par email (exemple, à implémenter avec un service d'envoi d'emails)
        if feedback_entry['type'] in ['bug', 'feature'] and os.getenv('ENABLE_EMAIL_NOTIFICATIONS') == 'True':
            try:
                send_feedback_notification(feedback_entry)
            except Exception as e:
                logger.warning(f"Impossible d'envoyer la notification par email: {str(e)}")
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback enregistré avec succès',
            'reference_id': os.path.splitext(file_name)[0]
        }), 201
        
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du feedback: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de l\'enregistrement du feedback: {str(e)}'
        }), 500

def update_quality_metrics(feedback_entry):
    """
    Met à jour les métriques de qualité en temps réel basées sur le feedback utilisateur
    """
    metrics_file = os.path.join('data', 'metrics', 'quality_metrics.json')
    os.makedirs(os.path.dirname(metrics_file), exist_ok=True)
    
    # Charger les métriques existantes ou créer une nouvelle structure
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)
    else:
        metrics = {
            'feedback_count': 0,
            'by_type': {},
            'by_source': {},
            'sentiment_score': 0,
            'bug_reports': 0,
            'feature_requests': 0,
            'active_users': set(),  # Sera converti en liste pour JSON
            'response_time_avg': 0,
            'timestamps': []
        }
    
    # Mettre à jour les métriques
    metrics['feedback_count'] += 1
    
    # Par type
    feedback_type = feedback_entry['type']
    metrics['by_type'][feedback_type] = metrics['by_type'].get(feedback_type, 0) + 1
    
    # Par source
    source = feedback_entry['source']
    metrics['by_source'][source] = metrics['by_source'].get(source, 0) + 1
    
    # Bugs et fonctionnalités
    if feedback_type == 'bug':
        metrics['bug_reports'] += 1
    elif feedback_type == 'feature':
        metrics['feature_requests'] += 1
    
    # Utilisateurs actifs (convertir set en liste pour JSON)
    if 'email' in feedback_entry and feedback_entry['email'] != 'anonymous':
        if isinstance(metrics['active_users'], list):
            if feedback_entry['email'] not in metrics['active_users']:
                metrics['active_users'].append(feedback_entry['email'])
        else:
            metrics['active_users'].add(feedback_entry['email'])
            metrics['active_users'] = list(metrics['active_users'])
    
    # Horodatage
    metrics['timestamps'].append(feedback_entry['timestamp'])
    
    # Analyse des sentiments simplifiée
    sentiment_score = analyze_sentiment(feedback_entry['message'])
    metrics['sentiment_score'] = ((metrics['sentiment_score'] * (metrics['feedback_count'] - 1)) + sentiment_score) / metrics['feedback_count']
    
    # Enregistrer les métriques
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2, default=lambda x: list(x) if isinstance(x, set) else x)

def analyze_sentiment(text):
    """
    Analyse de sentiment très simplifiée
    
    Returns:
        float: Score de sentiment entre -1.0 (négatif) et 1.0 (positif)
    """
    # Liste de mots positifs et négatifs pour une analyse simple
    positive_words = [
        'bien', 'bon', 'super', 'excellent', 'génial', 'parfait', 'bravo', 'merci',
        'aime', 'utile', 'pratique', 'efficace', 'facile', 'intuitif', 'simple'
    ]
    
    negative_words = [
        'mauvais', 'bug', 'erreur', 'problème', 'difficile', 'compliqué', 'lent',
        'inutile', 'confus', 'confusion', 'déçu', 'frustrant', 'impossible',
        'plantage', 'plante'
    ]
    
    # Convertir le texte en minuscules
    text_lower = text.lower()
    
    # Compter les mots positifs et négatifs
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    # Calculer le score normalisé
    total = positive_count + negative_count
    if total == 0:
        return 0.0
    
    return (positive_count - negative_count) / total

def send_feedback_notification(feedback_data):
    """
    Exemple de fonction pour envoyer une notification par email
    
    Args:
        feedback_data (dict): Données du feedback à notifier
    """
    # Cette fonction est un placeholder et doit être implémentée avec un service d'envoi d'emails
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    sender = os.getenv('NOTIFICATION_EMAIL_SENDER')
    recipients = os.getenv('NOTIFICATION_EMAIL_RECIPIENTS', '').split(',')
    password = os.getenv('NOTIFICATION_EMAIL_PASSWORD')
    
    if not sender or not recipients or not password:
        logger.warning("Configuration email incomplète, notification non envoyée")
        return
    
    # Créer le corps du message
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = ', '.join(recipients)
    message['Subject'] = f"[NovaEvo] Nouveau feedback: {feedback_data['type']}"
    
    body = f"""
    Nouveau feedback reçu:
    
    Type: {feedback_data['type']}
    Horodatage: {feedback_data['timestamp']}
    Email: {feedback_data['email']}
    Source: {feedback_data['source']}
    
    Message:
    {feedback_data['message']}
    
    ---
    Ce message est généré automatiquement. Ne pas répondre directement.
    """
    
    message.attach(MIMEText(body, 'plain'))
    
    # Envoyer l'email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipients, message.as_string())
    
    logger.info(f"Notification de feedback envoyée à {len(recipients)} destinataires")

# Fonction principale
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
