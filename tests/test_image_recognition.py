"""
Tests unitaires pour le module de reconnaissance d'image
"""
import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les modules à tester
from image_recognition.image_recognition_main import ImageRecognitionEngine, detect_labels


class TestImageRecognitionModule(unittest.TestCase):
    """Tests pour le module de reconnaissance d'image"""

    def setUp(self):
        """Configuration des tests"""
        # Créer un dossier pour les images de test s'il n'existe pas
        self.test_images_dir = os.path.join(os.path.dirname(__file__), 'test_images')
        os.makedirs(self.test_images_dir, exist_ok=True)
        
        # Créer une image de test simple pour les tests
        self.sample_image_path = os.path.join(self.test_images_dir, 'test_sample.jpg')
        if not os.path.exists(self.sample_image_path):
            # Créer une image vide avec OpenCV pour les tests
            try:
                import cv2
                import numpy as np
                # Créer une image noire 100x100
                img = np.zeros((100, 100, 3), np.uint8)
                # Dessiner un cercle blanc au centre (simuler une pièce)
                cv2.circle(img, (50, 50), 30, (255, 255, 255), -1)
                # Sauvegarder l'image
                cv2.imwrite(self.sample_image_path, img)
            except ImportError:
                # Si OpenCV n'est pas disponible, créer un fichier vide
                with open(self.sample_image_path, 'wb') as f:
                    f.write(b'')
        
        # Patcher les appels à Google Cloud Vision pour éviter les appels réels à l'API
        self.vision_client_patcher = patch('google.cloud.vision.ImageAnnotatorClient')
        self.mock_vision_client = self.vision_client_patcher.start()
        
        # Configurer le mock pour simuler une réponse
        mock_response = MagicMock()
        mock_label = MagicMock()
        mock_label.description = "car part"
        mock_label.score = 0.95
        mock_response.label_annotations = [mock_label]
        
        self.mock_vision_client.return_value.label_detection.return_value = mock_response
        
        # Initialiser l'engine avec le mock
        self.engine = ImageRecognitionEngine()
        self.engine.vision_client = self.mock_vision_client.return_value
        self.engine.vision_api_available = True

    def tearDown(self):
        """Nettoyage après les tests"""
        self.vision_client_patcher.stop()

    def test_engine_initialization(self):
        """Test de l'initialisation du moteur de reconnaissance d'image"""
        self.assertIsNotNone(self.engine)
        self.assertTrue(self.engine.initialized)
        
    def test_detect_labels_class_method(self):
        """Test de la méthode detect_labels de la classe ImageRecognitionEngine"""
        # Appeler la méthode detect_labels de la classe
        result = self.engine.detect_labels(self.sample_image_path)
        
        # Vérifications
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("labels", result)
        self.assertIsInstance(result["labels"], dict)
        self.assertGreater(len(result["labels"]), 0)
        
        # Vérifier que l'API a été appelée
        self.engine.vision_client.label_detection.assert_called_once()

    def test_detect_labels_standalone_function(self):
        """Test de la fonction autonome detect_labels"""
        # Patcher la fonction pour utiliser notre mock
        with patch('image_recognition.image_recognition_main.vision.ImageAnnotatorClient') as mock_client:
            # Configurer le mock
            mock_response = MagicMock()
            mock_label = MagicMock()
            mock_label.description = "engine"
            mock_label.score = 0.8
            mock_response.label_annotations = [mock_label]
            
            mock_client.return_value.label_detection.return_value = mock_response
            
            # Appeler la fonction detect_labels
            result = detect_labels(self.sample_image_path)
            
            # Vérifications
            self.assertIsInstance(result, dict)
            self.assertIn("success", result)
            self.assertTrue(result["success"])
            self.assertIn("labels", result)
            self.assertIsInstance(result["labels"], dict)
            self.assertGreater(len(result["labels"]), 0)
            
            # Vérifier que l'API a été appelée
            mock_client.return_value.label_detection.assert_called_once()

    def test_detect_labels_returns_dict(self):
        """
        Test que la fonction detect_labels retourne un dictionnaire
        contenant des clés 'labels' lorsqu'une image valide est analysée
        """
        # Appeler la fonction detect_labels avec notre image de test
        with patch('image_recognition.image_recognition_main.vision.ImageAnnotatorClient') as mock_client:
            # Configurer le mock
            mock_response = MagicMock()
            mock_label1 = MagicMock()
            mock_label1.description = "car"
            mock_label1.score = 0.9
            
            mock_label2 = MagicMock()
            mock_label2.description = "vehicle"
            mock_label2.score = 0.85
            
            mock_response.label_annotations = [mock_label1, mock_label2]
            
            mock_client.return_value.label_detection.return_value = mock_response
            
            # Appeler la fonction
            result = detect_labels(self.sample_image_path)
            
            # Vérifications
            self.assertIsInstance(result, dict)
            self.assertIn("labels", result)
            self.assertIsInstance(result["labels"], dict)
            self.assertGreater(len(result["labels"]), 0)
            
            # Vérifier que les labels attendus sont présents
            self.assertIn("car", result["labels"])
            self.assertIn("vehicle", result["labels"])
            
            # Vérifier les scores
            self.assertAlmostEqual(result["labels"]["car"], 0.9)
            self.assertAlmostEqual(result["labels"]["vehicle"], 0.85)

    def test_anomaly_detection(self):
        """Test de la détection d'anomalies dans les labels"""
        # Simuler la détection d'une anomalie
        with patch('image_recognition.image_recognition_main.vision.ImageAnnotatorClient') as mock_client:
            # Configurer le mock pour retourner des labels d'anomalies
            mock_response = MagicMock()
            
            mock_label1 = MagicMock()
            mock_label1.description = "car"
            mock_label1.score = 0.9
            
            mock_label2 = MagicMock()
            mock_label2.description = "rust damage"
            mock_label2.score = 0.8
            
            mock_label3 = MagicMock()
            mock_label3.description = "broken headlight"
            mock_label3.score = 0.7
            
            mock_response.label_annotations = [mock_label1, mock_label2, mock_label3]
            
            mock_client.return_value.label_detection.return_value = mock_response
            
            # Appeler la fonction
            result = detect_labels(self.sample_image_path)
            
            # Vérifications
            self.assertIn("anomalies_detected", result)
            self.assertTrue(result["anomalies_detected"])
            self.assertIn("anomalies", result)
            self.assertIsInstance(result["anomalies"], list)
            self.assertGreater(len(result["anomalies"]), 0)
            
            # Vérifier que les types d'anomalies sont bien détectés
            anomaly_types = [anomaly["type"] for anomaly in result["anomalies"]]
            self.assertTrue(any("damage" in anomaly_type for anomaly_type in anomaly_types))
            self.assertTrue(any("broken" in anomaly_type for anomaly_type in anomaly_types))

    def test_car_relatedness_detection(self):
        """Test de la détection de relation avec l'automobile"""
        # Simuler la détection de labels liés à l'automobile
        with patch('image_recognition.image_recognition_main.vision.ImageAnnotatorClient') as mock_client:
            # Configurer le mock pour retourner des labels liés à l'automobile
            mock_response = MagicMock()
            
            mock_label1 = MagicMock()
            mock_label1.description = "car"
            mock_label1.score = 0.9
            
            mock_label2 = MagicMock()
            mock_label2.description = "wheel"
            mock_label2.score = 0.85
            
            mock_label3 = MagicMock()
            mock_label3.description = "sky"  # Non lié à l'auto
            mock_label3.score = 0.7
            
            mock_response.label_annotations = [mock_label1, mock_label2, mock_label3]
            
            mock_client.return_value.label_detection.return_value = mock_response
            
            # Appeler la fonction
            result = detect_labels(self.sample_image_path)
            
            # Vérifications
            self.assertIn("car_related", result)
            self.assertTrue(result["car_related"])

    def test_error_handling(self):
        """Test de la gestion des erreurs"""
        # Simuler une erreur lors de l'appel à l'API
        with patch('image_recognition.image_recognition_main.vision.ImageAnnotatorClient') as mock_client:
            # Configurer le mock pour lever une exception
            mock_client.return_value.label_detection.side_effect = Exception("API Error")
            
            # Appeler la fonction
            result = detect_labels(self.sample_image_path)
            
            # Vérifications
            self.assertIn("error", result)
            self.assertIn("API Error", result["error"])


if __name__ == '__main__':
    unittest.main()
