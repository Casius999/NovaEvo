"""
Module OCR - Reconnaissance Optique de Caractères
Ce module utilise Google Cloud Vision API pour extraire du texte à partir d'images
"""
import os
import io
import re
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import vision
from google.cloud.vision_v1 import types

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ocr')

# Charger les variables d'environnement
load_dotenv()

class OCRProcessor:
    """Classe pour traiter les images avec OCR"""
    
    def __init__(self):
        """Initialisation du client Google Cloud Vision"""
        # Vérifier si les identifiants sont configurés
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            try:
                self.client = vision.ImageAnnotatorClient()
                logger.info("Client Google Cloud Vision initialisé avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du client Vision: {str(e)}")
                self.client = None
        else:
            logger.warning("AVERTISSEMENT: Identifiants Google Cloud Vision non configurés!")
            self.client = None
            
        # Dictionnaire de correspondance pour les marques de véhicule (pour une meilleure détection)
        self.car_brands = {
            "RENAULT": "Renault",
            "PEUGEOT": "Peugeot",
            "CITROEN": "Citroën", 
            "CITROEN": "Citroën",
            "BMW": "BMW",
            "MERCEDES": "Mercedes-Benz", 
            "MERCEDES BENZ": "Mercedes-Benz",
            "AUDI": "Audi",
            "VOLKSWAGEN": "Volkswagen", 
            "VW": "Volkswagen",
            "TOYOTA": "Toyota",
            "HONDA": "Honda",
            "FORD": "Ford",
            "FIAT": "Fiat",
            "OPEL": "Opel",
            "CHEVROLET": "Chevrolet",
            "NISSAN": "Nissan",
            "SEAT": "Seat",
            "SKODA": "Škoda",
            "HYUNDAI": "Hyundai",
            "KIA": "Kia",
            "MAZDA": "Mazda",
            "VOLVO": "Volvo",
            "MINI": "Mini",
            "SUZUKI": "Suzuki",
            "DACIA": "Dacia",
            "ALFA ROMEO": "Alfa Romeo",
            "JEEP": "Jeep",
            "LANCIA": "Lancia",
            "PORSCHE": "Porsche",
            "LEXUS": "Lexus",
            "JAGUAR": "Jaguar",
            "LAND ROVER": "Land Rover",
            "SMART": "Smart",
            "TESLA": "Tesla",
            "DS": "DS Automobiles"
        }
            
    def process_image(self, image_path=None, image_content=None):
        """
        Traite une image pour en extraire le texte
        Args:
            image_path (str, optional): Chemin vers le fichier image local
            image_content (bytes, optional): Contenu de l'image en bytes
        Returns:
            dict: Résultat de l'OCR avec le texte extrait
        """
        if not self.client:
            logger.error("Client Google Cloud Vision non configuré")
            return {"error": "Client Google Cloud Vision non configuré. Vérifiez votre configuration API."}
        
        try:
            # Préparer l'image
            if image_path:
                logger.info(f"Traitement d'image à partir du chemin: {image_path}")
                with io.open(image_path, 'rb') as image_file:
                    content = image_file.read()
            elif image_content:
                logger.info("Traitement d'image à partir du contenu binaire")
                content = image_content
            else:
                logger.error("Aucune image fournie pour le traitement OCR")
                return {"error": "Aucune image fournie"}
            
            image = types.Image(content=content)
            
            # Effectuer la détection de texte
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            # Vérifier si l'API a détecté des textes
            if not texts:
                logger.warning("Aucun texte détecté dans l'image")
                return {
                    "success": True,
                    "message": "Aucun texte détecté dans l'image"
                }
            
            # Extraire le texte complet (premier élément) et tous les blocs de texte
            full_text = texts[0].description
            logger.info(f"Texte extrait avec succès: {len(full_text)} caractères")
            
            text_blocks = [
                {
                    "text": text.description,
                    "bounding_poly": [[vertex.x, vertex.y] for vertex in text.bounding_poly.vertices]
                }
                for text in texts[1:]  # Ignorer le premier qui contient tout le texte
            ]
            
            return {
                "success": True,
                "full_text": full_text,
                "text_blocks": text_blocks
            }
                
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse OCR: {str(e)}")
            return {
                "error": f"Erreur lors de l'analyse OCR: {str(e)}"
            }
    
    def extract_vehicle_info(self, ocr_result):
        """
        Extraire les informations du véhicule à partir du résultat OCR
        Spécifiquement adapté pour les cartes grises françaises
        
        Args:
            ocr_result (dict): Résultat OCR de process_image()
            
        Returns:
            dict: Informations extraites du véhicule
        """
        if "error" in ocr_result:
            logger.error(f"Impossible d'extraire des informations: {ocr_result['error']}")
            return ocr_result
            
        full_text = ocr_result.get("full_text", "")
        logger.info("Extraction des informations du véhicule...")
        
        # Structure pour stocker les informations du véhicule
        vehicle_info = {
            "registration": None,
            "make": None,
            "model": None,
            "vin": None,
            "first_registration_date": None,
            "owner": None,
            "type_variant_version": None,
            "power": None
        }
        
        # Extraire les blocs de texte en lignes
        lines = full_text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        
        # Expression régulière pour l'immatriculation (format français: AA-123-BB ou AB-123-CD)
        reg_pattern = r'[A-Z]{2}-\d{3}-[A-Z]{2}'
        for line in cleaned_lines:
            reg_match = re.search(reg_pattern, line)
            if reg_match:
                vehicle_info["registration"] = reg_match.group(0)
                logger.info(f"Immatriculation détectée: {vehicle_info['registration']}")
                break
        
        # Détecter le VIN (numéro de châssis) - 17 caractères alphanumériques
        vin_pattern = r'[A-HJ-NPR-Z0-9]{17}'
        for line in cleaned_lines:
            vin_match = re.search(vin_pattern, line)
            if vin_match:
                candidate = vin_match.group(0)
                # Vérifier que c'est bien un VIN (pas de I, O, Q)
                if not any(c in "IOQ" for c in candidate):
                    vehicle_info["vin"] = candidate
                    logger.info(f"VIN détecté: {vehicle_info['vin']}")
                    break
        
        # Recherche de marque et modèle
        for line in cleaned_lines:
            upper_line = line.upper()
            # Chercher des correspondances avec les marques connues
            for brand_key in self.car_brands:
                if brand_key in upper_line:
                    vehicle_info["make"] = self.car_brands[brand_key]
                    logger.info(f"Marque détectée: {vehicle_info['make']}")
                    
                    # Essayer d'extraire le modèle (ce qui suit la marque)
                    brand_index = upper_line.find(brand_key)
                    if brand_index >= 0 and len(upper_line) > brand_index + len(brand_key) + 1:
                        remainder = upper_line[brand_index + len(brand_key):].strip()
                        # Si le reste contient des lettres, c'est probablement le modèle
                        if re.search(r'[A-Za-z]', remainder):
                            vehicle_info["model"] = remainder.strip('.,;: ')
                            logger.info(f"Modèle détecté: {vehicle_info['model']}")
                    break
            
            # Si on a trouvé la marque, on sort de la boucle
            if vehicle_info["make"]:
                break
        
        # Recherche de date de 1ère immatriculation (formats: JJ/MM/AAAA ou JJ.MM.AAAA)
        date_patterns = [
            r'(\d{2})[/](\d{2})[/](\d{4})',  # JJ/MM/AAAA
            r'(\d{2})[.](\d{2})[.](\d{4})',  # JJ.MM.AAAA
            r'(\d{2})[-](\d{2})[-](\d{4})'   # JJ-MM-AAAA
        ]
        
        for line in cleaned_lines:
            for pattern in date_patterns:
                date_match = re.search(pattern, line)
                if date_match:
                    day, month, year = date_match.groups()
                    try:
                        # Vérifier que la date est valide
                        date_obj = datetime(int(year), int(month), int(day))
                        if 1900 <= date_obj.year <= datetime.now().year:
                            vehicle_info["first_registration_date"] = f"{day}/{month}/{year}"
                            logger.info(f"Date de 1ère immatriculation: {vehicle_info['first_registration_date']}")
                            break
                    except ValueError:
                        # Date invalide, continuer la recherche
                        pass
            
            # Si on a trouvé la date, on sort de la boucle
            if vehicle_info["first_registration_date"]:
                break
        
        # Recherche de puissance (ex: 5CV, 110CH, etc.)
        power_pattern = r'(\d+)\s*(?:CV|CH|KW)'
        for line in cleaned_lines:
            power_match = re.search(power_pattern, line, re.IGNORECASE)
            if power_match:
                power_value = power_match.group(1)
                power_unit = power_match.group(0)[len(power_value):].strip()
                vehicle_info["power"] = f"{power_value} {power_unit}"
                logger.info(f"Puissance détectée: {vehicle_info['power']}")
                break
        
        # Recherche de propriétaire (généralement un nom en majuscules)
        # Cette logique est simplifiée et pourrait nécessiter des ajustements
        owner_candidates = []
        for line in cleaned_lines:
            # Si la ligne est principalement en majuscules et contient au moins un espace
            if line.isupper() and ' ' in line and len(line) > 5:
                # Éviter les lignes qui contiennent probablement des informations techniques
                if not any(keyword in line for keyword in ['CARTE', 'CERTIFICAT', 'IMMATRICULATION', 'TYPE', 'MARQUE', 'MODELE']):
                    owner_candidates.append(line)
        
        if owner_candidates:
            # Prendre le candidat le plus long comme nom du propriétaire
            vehicle_info["owner"] = max(owner_candidates, key=len)
            logger.info(f"Propriétaire potentiel détecté: {vehicle_info['owner']}")
        
        # Vérifier la qualité des informations extraites
        info_quality = sum(1 for value in vehicle_info.values() if value is not None)
        info_percentage = (info_quality / len(vehicle_info)) * 100
        logger.info(f"Qualité de l'extraction: {info_percentage:.2f}% ({info_quality}/{len(vehicle_info)} champs)")
        
        # Préparer la réponse avec une indication de confiance
        confidence_level = "haute" if info_percentage > 70 else "moyenne" if info_percentage > 40 else "basse"
        
        return {
            "success": True,
            "vehicle_info": vehicle_info,
            "raw_text": full_text,
            "confidence": confidence_level,
            "extraction_quality": f"{info_percentage:.2f}%"
        }

    def validate_registration(self, registration):
        """
        Valide le format d'une plaque d'immatriculation française
        
        Args:
            registration (str): Plaque d'immatriculation à valider
            
        Returns:
            bool: True si le format est valide, False sinon
        """
        if not registration:
            return False
            
        # Format standard français (SIV): AA-123-BB
        pattern = r'^[A-Z]{2}-\d{3}-[A-Z]{2}$'
        return bool(re.match(pattern, registration))

    def fallback_to_tesseract(self, image_path):
        """
        Méthode de repli vers Tesseract OCR si Google Cloud Vision n'est pas configuré
        
        Args:
            image_path (str): Chemin vers l'image
            
        Returns:
            dict: Résultat de l'OCR avec le texte extrait
        """
        try:
            import pytesseract
            from PIL import Image
            
            logger.info("Utilisation de Tesseract OCR comme fallback")
            img = Image.open(image_path)
            
            # Prétraitement de l'image pour améliorer la reconnaissance
            # Tesseract fonctionne mieux avec des images en noir et blanc à fort contraste
            
            # Extraire le texte avec Tesseract
            extracted_text = pytesseract.image_to_string(img, lang='fra')
            
            if extracted_text:
                return {
                    "success": True,
                    "full_text": extracted_text,
                    "text_blocks": [],
                    "note": "Texte extrait avec Tesseract OCR (solution de repli)"
                }
            else:
                return {"error": "Aucun texte détecté avec Tesseract OCR"}
                
        except ImportError:
            logger.error("Impossible de fallback vers Tesseract OCR: module pytesseract non installé")
            return {"error": "Tesseract OCR non disponible"}
        except Exception as e:
            logger.error(f"Erreur lors de l'utilisation de Tesseract OCR: {str(e)}")
            return {"error": f"Erreur avec Tesseract: {str(e)}"}

def extraire_infos_carte_grise(image_path):
    """
    Fonction de haut niveau pour extraire les informations d'une carte grise
    Cette fonction est conçue pour être appelée directement depuis le module app.py
    
    Args:
        image_path (str): Chemin vers l'image de la carte grise
        
    Returns:
        dict: Informations extraites du véhicule
    """
    ocr = OCRProcessor()
    result = ocr.process_image(image_path=image_path)
    
    # Si Google Cloud Vision n'est pas configuré ou échoue, essayer Tesseract
    if "error" in result and "Google Cloud Vision" in result["error"]:
        result = ocr.fallback_to_tesseract(image_path)
    
    if "error" not in result:
        return ocr.extract_vehicle_info(result)
    else:
        return result

# Exemple d'utilisation
def main():
    """Fonction principale pour tester le module OCR"""
    ocr = OCRProcessor()
    
    # Exemple de test avec une image locale (si disponible)
    test_image = "test_images/carte_grise_sample.jpg"
    if os.path.exists(test_image):
        print(f"Traitement de l'image de test: {test_image}")
        result = ocr.process_image(image_path=test_image)
        
        if "error" not in result:
            vehicle_info = ocr.extract_vehicle_info(result)
            print(json.dumps(vehicle_info, indent=2, ensure_ascii=False))
        else:
            print(f"Erreur: {result['error']}")
    else:
        print(f"Image de test non trouvée: {test_image}")
        print("Créez un dossier 'test_images' avec des exemples pour tester.")

if __name__ == "__main__":
    main()
