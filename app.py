"""
Assistant Auto Ultime - Application Principale
"""
import os
import json
import logging
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

# Créer le dossier d'upload si nécessaire
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuration du logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_file = os.getenv('LOG_FILE', 'logs/auto_assistant.log')

# Créer le dossier de logs si nécessaire
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Configuration du logger
logger = logging.getLogger('assistant_auto')
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

# Nouveaux modules (Étape 10)
from subscriptions.subscriptions_main import process_subscription, app as subscriptions_app, webhook_handler

# Initialiser les gestionnaires des modules
ocr_processor = OCRProcessor()
obd_manager = OBDManager()
nlp_assistant = AutoAssistantNLP()
image_recognition_engine = ImageRecognitionEngine()
ecu_flash_manager = ECUFlashManager()
parts_finder_manager = PartsFinderManager()

# Routes principales

@app.route('/')
def index():
    """Route principale - Page d'accueil"""
    return jsonify({
        'status': 'success',
        'message': 'API Assistant Auto Ultime opérationnelle',
        'modules': [
            '/ocr', '/obd2', '/nlp', '/image_recognition', 
            '/ecu_flash', '/parts_finder', '/subscriptions', '/mapping_affiliations',
            '/feedback'  # Nouvel endpoint pour l'étape 11
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
        logger.error(f"Erreur NLP: {str(e)}")
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
        result = flash_ecu(tuning_parameters)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur ECU flash: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors du flash ECU: {str(e)}'
        }), 500

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
    
    return jsonify({
        'status': 'success',
        'parameters': SECURE_LIMITS
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
    
    # Lancer la recherche multi-sources
    try:
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
        
        return jsonify({
            'status': 'success',
            'count': len(offers),
            'reference': reference,
            'type': type_piece,
            'offers': offers
        })
        
    except Exception as e:
        logger.error(f"Erreur recherche pièces: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la recherche de pièces: {str(e)}'
        }), 500

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

# Nouveaux endpoints pour le module d'abonnements (Étape 10)

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

# Endpoints pour le module Mapping Affiliations (Étape 10)

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
    
    # Import et utilisation du module mapping_affiliations
    try:
        from mapping_affiliations.mapping_affiliations_main import search_mapping_offers
        offers = search_mapping_offers(query, category)
        return jsonify({"offers": offers})
    except ImportError:
        # Si le module n'est pas encore disponible, retourner un exemple de données
        example_offers = [
            {
                "preparateur": "TuningBox France",
                "description": "Cartographie Stage 1 pour moteurs TSI 2.0L",
                "price": "249.90€",
                "affiliate_link": "https://tuningbox-france.com/cart/stage1-tsi?ref=assistant-auto",
                "category": category or "sport",
                "source": "API Partenaire"
            },
            {
                "preparateur": "DigiTech Performance",
                "description": "Reprogrammation origine pour économie de carburant",
                "price": "189.00€",
                "affiliate_link": "https://digitech-perf.fr/eco?ref=auto-assistant",
                "category": category or "origine",
                "source": "Facebook Marketplace"
            }
        ]
        return jsonify({"offers": example_offers})
    except Exception as e:
        logger.error(f"Erreur recherche cartographies: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la recherche de cartographies: {str(e)}'
        }), 500

# Nouvel endpoint pour la collecte de feedback (Étape 11)

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
    message['Subject'] = f"[Assistant Auto] Nouveau feedback: {feedback_data['type']}"
    
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
