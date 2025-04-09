"""
Tests unitaires pour le module OCR
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ocr.ocr_main import OCRProcessor, extraire_infos_carte_grise

class TestOCR(unittest.TestCase):
    """Tests pour le module OCR"""

    def setUp(self):
        """Initialisation avant chaque test"""
        # Créer un mock pour éviter d'utiliser l'API Google Cloud Vision
        self.patcher = patch('ocr.ocr_main.vision.ImageAnnotatorClient')
        self.mock_client = self.patcher.start()
        
        # Initialiser le processeur OCR avec notre mock
        self.ocr = OCRProcessor()
        self.ocr.client = MagicMock()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        self.patcher.stop()
    
    def test_process_image_no_image(self):
        """Test du traitement sans image"""
        result = self.ocr.process_image()
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Aucune image fournie")
    
    def test_process_image_success(self):
        """Test du traitement d'image avec succès"""
        # Configurer le mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_text = MagicMock()
        mock_text.description = "CARTE GRISE\nRENAULT CLIO\nAA-123-BB"
        mock_text.bounding_poly.vertices = [MagicMock(x=0, y=0), MagicMock(x=10, y=0), 
                                           MagicMock(x=10, y=10), MagicMock(x=0, y=10)]
        mock_response.text_annotations = [mock_text]
        
        self.ocr.client.text_detection.return_value = mock_response
        
        # Tester la méthode
        result = self.ocr.process_image(image_content=b"fake_image_content")
        
        # Vérifier que la méthode a été appelée
        self.ocr.client.text_detection.assert_called_once()
        
        # Vérifier le résultat
        self.assertTrue(result["success"])
        self.assertEqual(result["full_text"], "CARTE GRISE\nRENAULT CLIO\nAA-123-BB")
    
    def test_extract_vehicle_info(self):
        """Test d'extraction des informations du véhicule"""
        # Données de test
        ocr_result = {
            "success": True,
            "full_text": "CERTIFICAT D'IMMATRICULATION\nRENAULT CLIO\nAA-123-BB\nVF123456789012345\n01/01/2020\nDUPONT JEAN\n"
        }
        
        # Appeler la méthode
        result = self.ocr.extract_vehicle_info(ocr_result)
        
        # Vérifier le résultat
        self.assertTrue(result["success"])
        self.assertEqual(result["vehicle_info"]["registration"], "AA-123-BB")
        self.assertEqual(result["vehicle_info"]["make"], "Renault")
        self.assertEqual(result["vehicle_info"]["vin"], "VF123456789012345")
        self.assertEqual(result["vehicle_info"]["first_registration_date"], "01/01/2020")
    
    def test_extract_vehicle_info_advanced(self):
        """Test d'extraction avancée des informations du véhicule"""
        # Données de test plus complètes
        ocr_result = {
            "success": True,
            "full_text": """RÉPUBLIQUE FRANÇAISE
            CERTIFICAT D'IMMATRICULATION
            CARTE GRISE
            
            Numéro d'immatriculation: AB-123-CD
            Date première immatriculation: 15/03/2018
            
            PEUGEOT 308 GTI
            Type: M10FGUTVP5000
            Puissance: 200 KW / 272 CH
            
            VIN: VF30ABCDEF12345
            
            MARTIN SOPHIE MARIE
            123 RUE DE PARIS
            75001 PARIS
            
            Couleur: GRIS
            Catégorie: M1
            """
        }
        
        # Appeler la méthode
        result = self.ocr.extract_vehicle_info(ocr_result)
        
        # Vérifier le résultat
        self.assertTrue(result["success"])
        self.assertEqual(result["vehicle_info"]["registration"], "AB-123-CD")
        self.assertEqual(result["vehicle_info"]["make"], "Peugeot")
        self.assertEqual(result["vehicle_info"]["model"], "308 GTI")
        self.assertEqual(result["vehicle_info"]["vin"], "VF30ABCDEF12345")
        self.assertEqual(result["vehicle_info"]["first_registration_date"], "15/03/2018")
        self.assertEqual(result["vehicle_info"]["owner"], "MARTIN SOPHIE MARIE")
        self.assertEqual(result["vehicle_info"]["power"], "200 KW")
    
    def test_validate_registration(self):
        """Test de validation du format de plaque d'immatriculation"""
        # Formats valides
        self.assertTrue(self.ocr.validate_registration("AB-123-CD"))
        self.assertTrue(self.ocr.validate_registration("AA-123-BB"))
        self.assertTrue(self.ocr.validate_registration("ZZ-999-ZZ"))
        
        # Formats invalides
        self.assertFalse(self.ocr.validate_registration("AB123CD"))  # sans tirets
        self.assertFalse(self.ocr.validate_registration("AB-123-C"))  # trop court
        self.assertFalse(self.ocr.validate_registration("123-AB-CD"))  # mauvais format
        self.assertFalse(self.ocr.validate_registration(""))  # vide
        self.assertFalse(self.ocr.validate_registration(None))  # None
    
    @patch('ocr.ocr_main.OCRProcessor.process_image')
    def test_extraire_infos_carte_grise(self, mock_process_image):
        """Test de la fonction de haut niveau extraire_infos_carte_grise"""
        # Configurer le mock pour simuler une réponse réussie
        mock_process_image.return_value = {
            "success": True,
            "full_text": "RENAULT CLIO\nAA-123-BB\nVF123456789012345"
        }
        
        # Appeler la fonction
        result = extraire_infos_carte_grise("fake_image_path.jpg")
        
        # Vérifier que le mock a été appelé correctement
        mock_process_image.assert_called_once_with(image_path="fake_image_path.jpg")
        
        # Vérifier le résultat
        self.assertTrue(result["success"])
        self.assertEqual(result["vehicle_info"]["registration"], "AA-123-BB")
        self.assertEqual(result["vehicle_info"]["make"], "Renault")
        self.assertEqual(result["vehicle_info"]["vin"], "VF123456789012345")
    
    @patch('ocr.ocr_main.OCRProcessor.process_image')
    @patch('ocr.ocr_main.OCRProcessor.fallback_to_tesseract')
    def test_fallback_to_tesseract(self, mock_fallback, mock_process_image):
        """Test du fallback vers Tesseract si Google Cloud Vision échoue"""
        # Configurer les mocks
        mock_process_image.return_value = {"error": "Client Google Cloud Vision non configuré"}
        mock_fallback.return_value = {
            "success": True,
            "full_text": "RENAULT CLIO\nAA-123-BB\nVF123456789012345",
            "note": "Texte extrait avec Tesseract OCR (solution de repli)"
        }
        
        # Appeler la fonction
        result = extraire_infos_carte_grise("fake_image_path.jpg")
        
        # Vérifier que les mocks ont été appelés correctement
        mock_process_image.assert_called_once_with(image_path="fake_image_path.jpg")
        mock_fallback.assert_called_once_with("fake_image_path.jpg")
        
        # Vérifier le résultat
        self.assertTrue(result["success"])
        self.assertEqual(result["vehicle_info"]["registration"], "AA-123-BB")
        self.assertEqual(result["vehicle_info"]["make"], "Renault")
        self.assertEqual(result["vehicle_info"]["vin"], "VF123456789012345")
        self.assertIn("note", result)  # Le résultat devrait inclure la note du fallback

if __name__ == '__main__':
    unittest.main()
