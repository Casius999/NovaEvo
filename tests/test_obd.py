"""
Tests unitaires pour le module OBD-II
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les modules à tester
from obd2.obd_main import OBDManager


class TestOBDModule(unittest.TestCase):
    """Tests pour le module OBD-II"""

    def setUp(self):
        """Configuration des tests"""
        self.obd_manager = OBDManager()

    def test_obd_manager_init(self):
        """Test de l'initialisation de OBDManager"""
        self.assertIsNotNone(self.obd_manager)
        self.assertFalse(self.obd_manager.connected)
        self.assertIsNone(self.obd_manager.connection)

    @patch('obd.OBD')
    def test_connect_success(self, mock_obd):
        """Test de connexion réussie"""
        # Configurer le mock pour simuler une connexion réussie
        mock_connection = MagicMock()
        mock_connection.status.return_value = 3  # OBDStatus.CAR_CONNECTED
        mock_obd.return_value = mock_connection

        # Tester la connexion
        result = self.obd_manager.connect()

        # Vérifications
        self.assertTrue(result)
        self.assertTrue(self.obd_manager.connected)
        mock_obd.assert_called_once()

    @patch('obd.OBD')
    def test_connect_failure(self, mock_obd):
        """Test de connexion échouée"""
        # Configurer le mock pour simuler une connexion échouée
        mock_connection = MagicMock()
        mock_connection.status.return_value = 0  # OBDStatus.NOT_CONNECTED
        mock_obd.return_value = mock_connection

        # Tester la connexion
        result = self.obd_manager.connect()

        # Vérifications
        self.assertFalse(result)
        self.assertFalse(self.obd_manager.connected)
        mock_obd.assert_called_once()

    @patch('obd.OBD')
    def test_get_rpm(self, mock_obd):
        """Test de récupération du RPM"""
        # Configurer le mock
        mock_connection = MagicMock()
        mock_connection.status.return_value = 3  # OBDStatus.CAR_CONNECTED
        
        # Mock de la réponse pour la commande RPM
        mock_response = MagicMock()
        mock_response.is_null.return_value = False
        mock_response.value.magnitude = 1500
        mock_response.value.units = "rpm"
        mock_connection.query.return_value = mock_response
        
        mock_obd.return_value = mock_connection

        # Connecter et tester
        self.obd_manager.connect()
        result = self.obd_manager.get_rpm()

        # Vérifications
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertEqual(result["value"], 1500)
        self.assertEqual(result["unit"], "rpm")

    @patch('obd.OBD')
    def test_get_speed(self, mock_obd):
        """Test de récupération de la vitesse"""
        # Configurer le mock
        mock_connection = MagicMock()
        mock_connection.status.return_value = 3  # OBDStatus.CAR_CONNECTED
        
        # Mock de la réponse pour la commande SPEED
        mock_response = MagicMock()
        mock_response.is_null.return_value = False
        mock_response.value.magnitude = 60
        mock_response.value.units = "kph"
        mock_connection.query.return_value = mock_response
        
        mock_obd.return_value = mock_connection

        # Connecter et tester
        self.obd_manager.connect()
        result = self.obd_manager.get_speed()

        # Vérifications
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertEqual(result["value"], 60)
        self.assertEqual(result["unit"], "kph")

    @patch('obd.OBD')
    def test_get_dtc_codes_none(self, mock_obd):
        """Test de récupération des codes d'erreur (aucun code)"""
        # Configurer le mock
        mock_connection = MagicMock()
        mock_connection.status.return_value = 3  # OBDStatus.CAR_CONNECTED
        
        # Mock de la réponse pour la commande GET_DTC
        mock_response = MagicMock()
        mock_response.is_null.return_value = False
        mock_response.value = []  # Aucun code d'erreur
        mock_connection.query.return_value = mock_response
        
        mock_obd.return_value = mock_connection

        # Connecter et tester
        self.obd_manager.connect()
        result = self.obd_manager.get_dtc_codes()

        # Vérifications
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 0)
        self.assertEqual(len(result["codes"]), 0)

    @patch('obd.OBD')
    def test_get_dtc_codes_with_codes(self, mock_obd):
        """Test de récupération des codes d'erreur (avec codes)"""
        # Configurer le mock
        mock_connection = MagicMock()
        mock_connection.status.return_value = 3  # OBDStatus.CAR_CONNECTED
        
        # Mock de la réponse pour la commande GET_DTC
        mock_response = MagicMock()
        mock_response.is_null.return_value = False
        mock_response.value = [
            ("P0123", "Throttle Position Sensor Circuit High Input"),
            ("P0456", "EVAP System Leak Detected (Small Leak)")
        ]
        mock_connection.query.return_value = mock_response
        
        mock_obd.return_value = mock_connection

        # Connecter et tester
        self.obd_manager.connect()
        result = self.obd_manager.get_dtc_codes()

        # Vérifications
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["codes"]), 2)
        self.assertEqual(result["codes"][0]["code"], "P0123")

    def test_disconnect(self):
        """Test de la déconnexion"""
        # Créer un mock pour la connexion
        self.obd_manager.connection = MagicMock()
        self.obd_manager.connected = True
        
        # Déconnecter
        self.obd_manager.disconnect()
        
        # Vérifications
        self.assertFalse(self.obd_manager.connected)
        self.assertIsNone(self.obd_manager.connection)
        self.obd_manager.connection.close.assert_called_once()

    def test_get_vehicle_data_function(self):
        """
        Test de la fonction get_vehicle_data() définie dans app.py
        
        Cette fonction devrait retourner un dictionnaire contenant 
        les clés RPM, Speed et DTC.
        """
        # Import de la fonction depuis app.py
        from app import get_vehicle_data
        
        # Patch du OBDManager pour éviter la connexion réelle
        with patch('app.obd_manager') as mock_obd_manager:
            # Configurer les retours des méthodes
            mock_obd_manager.connect.return_value = True
            mock_obd_manager.get_rpm.return_value = {"success": True, "value": 1200}
            mock_obd_manager.get_speed.return_value = {"success": True, "value": 45}
            mock_obd_manager.get_dtc_codes.return_value = {"success": True, "codes": [], "count": 0}
            
            # Appeler la fonction
            result = get_vehicle_data()
            
            # Vérifications
            self.assertIsInstance(result, dict)
            self.assertIn("RPM", result)
            self.assertIn("Speed", result)
            self.assertIn("DTC", result)
            
            # Vérifier que la fonction a bien appelé disconnect
            mock_obd_manager.disconnect.assert_called_once()


if __name__ == '__main__':
    unittest.main()
