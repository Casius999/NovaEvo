"""
Tests unitaires pour le module OCR
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ocr import OCRProcessor

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
            "full_text": "CARTE GRISE\nRENAULT CLIO\nAA-123-BB\nVF123456789012345"
        }
        
        # Appeler la méthode
        result = self.ocr.extract_vehicle_info(ocr_result)
        
        # Vérifier le résultat
        self.assertTrue(result["success"])
        self.assertEqual(result["vehicle_info"]["registration"], "AA-123-BB")
        self.assertEqual(result["vehicle_info"]["make"], "Renault")
        self.assertEqual(result["vehicle_info"]["vin"], "VF123456789012345")

if __name__ == '__main__':
    unittest.main()
