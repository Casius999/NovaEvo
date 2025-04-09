"""
Module OCR - Reconnaissance Optique de Caractères
Ce module utilise Google Cloud Vision API pour extraire du texte à partir d'images
"""
import os
import io
import json
from dotenv import load_dotenv
from google.cloud import vision
from google.cloud.vision_v1 import types

# Charger les variables d'environnement
load_dotenv()

class OCRProcessor:
    """Classe pour traiter les images avec OCR"""
    
    def __init__(self):
        """Initialisation du client Google Cloud Vision"""
        # Vérifier si les identifiants sont configurés
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            self.client = vision.ImageAnnotatorClient()
        else:
            print("AVERTISSEMENT: Identifiants Google Cloud Vision non configurés!")
            self.client = None
    
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
            return {"error": "Client Google Cloud Vision non configuré"}
        
        try:
            # Préparer l'image
            if image_path:
                with io.open(image_path, 'rb') as image_file:
                    content = image_file.read()
            elif image_content:
                content = image_content
            else:
                return {"error": "Aucune image fournie"}
            
            image = types.Image(content=content)
            
            # Effectuer la détection de texte
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            # Extraire le texte complet (premier élément) et tous les blocs de texte
            if texts:
                full_text = texts[0].description
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
            else:
                return {
                    "success": True,
                    "message": "Aucun texte détecté dans l'image"
                }
                
        except Exception as e:
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
            return ocr_result
            
        full_text = ocr_result.get("full_text", "")
        
        # Exemple simple d'extraction (à améliorer avec des regex plus précis)
        vehicle_info = {
            "registration": None,
            "make": None,
            "model": None,
            "vin": None,
            "first_registration_date": None,
            "owner": None
        }
        
        # Recherche d'informations (très basique, à améliorer)
        lines = full_text.split('\n')
        for line in lines:
            line = line.strip()
            # Immatriculation (format AA-123-BB ou similaire)
            if '-' in line and len(line) <= 10 and line[0].isalpha():
                vehicle_info["registration"] = line
            
            # Numéro VIN (17 caractères)
            if len(line) == 17 and line.isalnum():
                vehicle_info["vin"] = line
                
            # Recherche de mots clés pour la marque
            for brand in ["RENAULT", "PEUGEOT", "CITROEN", "BMW", "MERCEDES", "AUDI", "TOYOTA"]:
                if brand in line.upper():
                    vehicle_info["make"] = brand.title()
                    # Essayer d'extraire le modèle (ce qui suit la marque)
                    parts = line.upper().split(brand)
                    if len(parts) > 1 and parts[1].strip():
                        vehicle_info["model"] = parts[1].strip()
                    break
        
        return {
            "success": True,
            "vehicle_info": vehicle_info,
            "raw_text": full_text
        }

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
