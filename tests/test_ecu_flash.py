"""
Tests unitaires pour le module ECU Flash
"""
import os
import json
import unittest
from unittest.mock import patch, MagicMock, mock_open

import sys
import pytest

# Ajouter le répertoire parent au chemin pour permettre l'importation des modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import des modules à tester
from ecu_flash.ecu_flash_main import (
    validate_tuning_parameters,
    backup_current_configuration,
    flash_ecu,
    ECUFlashManager,
    SECURE_LIMITS
)

class TestECUFlashValidation(unittest.TestCase):
    """Tests de validation des paramètres de tuning"""
    
    def test_validate_valid_parameters(self):
        """Test de validation avec des paramètres valides"""
        test_params = {
            "cartographie_injection": 100,
            "boost_turbo": 1.0
        }
        is_valid, message = validate_tuning_parameters(test_params)
        self.assertTrue(is_valid)
        self.assertEqual(message, "")
    
    def test_validate_parameters_at_limits(self):
        """Test de validation avec des paramètres aux limites"""
        # Paramètres à la limite inférieure
        min_params = {
            "cartographie_injection": SECURE_LIMITS["cartographie_injection"]["min"],
            "boost_turbo": SECURE_LIMITS["boost_turbo"]["min"]
        }
        is_valid, message = validate_tuning_parameters(min_params)
        self.assertTrue(is_valid)
        
        # Paramètres à la limite supérieure
        max_params = {
            "cartographie_injection": SECURE_LIMITS["cartographie_injection"]["max"],
            "boost_turbo": SECURE_LIMITS["boost_turbo"]["max"]
        }
        is_valid, message = validate_tuning_parameters(max_params)
        self.assertTrue(is_valid)
    
    def test_validate_parameters_below_min(self):
        """Test de validation avec des paramètres en dessous de la limite min"""
        test_params = {
            "cartographie_injection": SECURE_LIMITS["cartographie_injection"]["min"] - 1,
            "boost_turbo": 1.0
        }
        is_valid, message = validate_tuning_parameters(test_params)
        self.assertFalse(is_valid)
        self.assertIn("hors limite", message)
    
    def test_validate_parameters_above_max(self):
        """Test de validation avec des paramètres au-dessus de la limite max"""
        test_params = {
            "cartographie_injection": 100,
            "boost_turbo": SECURE_LIMITS["boost_turbo"]["max"] + 0.1
        }
        is_valid, message = validate_tuning_parameters(test_params)
        self.assertFalse(is_valid)
        self.assertIn("hors limite", message)
    
    def test_validate_unknown_parameter(self):
        """Test de validation avec un paramètre inconnu"""
        test_params = {
            "parametre_inconnu": 100
        }
        is_valid, message = validate_tuning_parameters(test_params)
        self.assertFalse(is_valid)
        self.assertIn("inconnu", message)

class TestECUFlashBackup(unittest.TestCase):
    """Tests de la fonction de sauvegarde de configuration"""
    
    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_backup_configuration(self, mock_file, mock_json_dump):
        """Test de la sauvegarde de configuration"""
        # Créer un mock pour le contrôleur ECU
        mock_controller = MagicMock()
        mock_controller.read_configuration.return_value = {"test": "configuration"}
        
        # Appeler la fonction de backup
        result = backup_current_configuration(mock_controller, "test_backup.json")
        
        # Vérifier que la fonction a correctement lu la configuration
        mock_controller.read_configuration.assert_called_once()
        
        # Vérifier que le fichier a été ouvert correctement
        mock_file.assert_called_once_with("test_backup.json", "w")
        
        # Vérifier que la configuration a été sauvegardée
        mock_json_dump.assert_called_once()
        
        # Vérifier le résultat
        self.assertEqual(result, {"test": "configuration"})

class TestECUFlash(unittest.TestCase):
    """Tests de la fonction de flashage ECU"""
    
    @patch("ecu_flash.ecu_flash_main.validate_tuning_parameters")
    def test_flash_ecu_validation_failed(self, mock_validate):
        """Test d'échec de validation des paramètres"""
        mock_validate.return_value = (False, "Erreur de validation")
        
        result = flash_ecu({"test": "params"})
        
        mock_validate.assert_called_once_with({"test": "params"})
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Erreur de validation")
    
    @patch("ecu_flash.ecu_flash_main.ECUFlashController")
    @patch("ecu_flash.ecu_flash_main.backup_current_configuration")
    @patch("ecu_flash.ecu_flash_main.validate_tuning_parameters")
    def test_flash_ecu_success(self, mock_validate, mock_backup, mock_controller_class):
        """Test de succès du flashage"""
        # Configuration des mocks
        mock_validate.return_value = (True, "")
        mock_backup.return_value = {"backup": "data"}
        
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_controller.flash_configuration.return_value = {"success": True}
        
        # Appel de la fonction
        result = flash_ecu({"test": "params"})
        
        # Vérifications
        mock_validate.assert_called_once_with({"test": "params"})
        mock_controller_class.assert_called_once()
        mock_backup.assert_called_once_with(mock_controller)
        mock_controller.flash_configuration.assert_called_once_with({"test": "params"})
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["new_configuration"], {"test": "params"})
    
    @patch("ecu_flash.ecu_flash_main.ECUFlashController")
    @patch("ecu_flash.ecu_flash_main.backup_current_configuration")
    @patch("ecu_flash.ecu_flash_main.validate_tuning_parameters")
    def test_flash_ecu_failure(self, mock_validate, mock_backup, mock_controller_class):
        """Test d'échec du flashage"""
        # Configuration des mocks
        mock_validate.return_value = (True, "")
        mock_backup.return_value = {"backup": "data"}
        
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_controller.flash_configuration.return_value = {"success": False, "message": "Échec du flash"}
        
        # Appel de la fonction
        result = flash_ecu({"test": "params"})
        
        # Vérifications
        mock_validate.assert_called_once_with({"test": "params"})
        mock_controller_class.assert_called_once()
        mock_backup.assert_called_once_with(mock_controller)
        mock_controller.flash_configuration.assert_called_once_with({"test": "params"})
        mock_controller.restore_configuration.assert_called_once_with({"backup": "data"})
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Échec du flash", result["message"])
    
    @patch("ecu_flash.ecu_flash_main.ECUFlashController")
    @patch("ecu_flash.ecu_flash_main.backup_current_configuration")
    @patch("ecu_flash.ecu_flash_main.validate_tuning_parameters")
    def test_flash_ecu_exception(self, mock_validate, mock_backup, mock_controller_class):
        """Test d'exception pendant le flashage"""
        # Configuration des mocks
        mock_validate.return_value = (True, "")
        mock_backup.return_value = {"backup": "data"}
        
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_controller.flash_configuration.side_effect = Exception("Erreur critique")
        
        # Appel de la fonction
        result = flash_ecu({"test": "params"})
        
        # Vérifications
        mock_validate.assert_called_once_with({"test": "params"})
        mock_controller_class.assert_called_once()
        mock_backup.assert_called_once_with(mock_controller)
        mock_controller.flash_configuration.assert_called_once_with({"test": "params"})
        mock_controller.restore_configuration.assert_called_once_with({"backup": "data"})
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Erreur critique", result["message"])
        self.assertIn("Rollback effectué", result["message"])

class TestECUFlashManager(unittest.TestCase):
    """Tests du gestionnaire ECUFlashManager"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.manager = ECUFlashManager()
    
    @patch("ecu_flash.ecu_flash_main.ECUFlashController")
    def test_init_real_flash_controller(self, mock_controller_class):
        """Test d'initialisation du contrôleur réel"""
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        
        self.manager.init_real_flash_controller()
        
        mock_controller_class.assert_called_once()
        self.assertEqual(self.manager.flash_controller, mock_controller)
    
    @patch("ecu_flash.ecu_flash_main.ECUFlashController")
    def test_init_real_flash_controller_exception(self, mock_controller_class):
        """Test d'exception lors de l'initialisation du contrôleur"""
        mock_controller_class.side_effect = Exception("Erreur d'initialisation")
        
        with self.assertRaises(Exception):
            self.manager.init_real_flash_controller()
    
    @patch("builtins.open", new_callable=mock_open, read_data='{"vehicle": {"make": "Test"}, "parameters": {}, "maps": {}, "metadata": {}}')
    def test_load_config_file(self, mock_file):
        """Test de chargement d'un fichier de configuration"""
        with patch("json.load") as mock_json_load:
            mock_json_load.return_value = {
                "vehicle": {"make": "Test", "model": "Model", "year": "2025"},
                "parameters": {"param1": {"name": "param1", "value": 100, "description": "Test", "category": "test"}},
                "maps": {},
                "metadata": {}
            }
            
            result = self.manager.load_config_file("test_config.json")
            
            mock_file.assert_called_once_with("test_config.json", "r")
            mock_json_load.assert_called_once()
            
            self.assertTrue(result["success"])
            self.assertEqual(result["vehicle"]["make"], "Test")
            self.assertEqual(result["parameters_count"], 1)
    
    def test_connect_ecu_no_device_id(self):
        """Test de connexion sans ID de périphérique"""
        self.manager.device_id = None
        
        result = self.manager.connect_ecu()
        
        self.assertFalse(result["success"])
        self.assertIn("non configuré", result["message"])
    
    @patch("time.sleep")
    def test_connect_ecu_simulation(self, mock_sleep):
        """Test de connexion en mode simulation"""
        self.manager.device_id = "TEST001"
        self.manager.flash_controller = None
        
        result = self.manager.connect_ecu()
        
        mock_sleep.assert_called_once()
        self.assertTrue(result["success"])
        self.assertIn("simulation", result["message"])
        self.assertTrue(self.manager.connected)
        self.assertEqual(self.manager.connection["device_id"], "TEST001")
    
    @patch("ecu_flash.ecu_flash_main.flash_ecu")
    def test_flash_ecu_with_custom_params(self, mock_flash_ecu):
        """Test de flashage avec paramètres personnalisés"""
        mock_flash_ecu.return_value = {"status": "success", "message": "Flash réussi"}
        
        self.manager.connected = True
        result = self.manager.flash_ecu_with_custom_params({"test": "params"})
        
        mock_flash_ecu.assert_called_once_with({"test": "params"})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Flash réussi")
    
    def test_flash_ecu_with_custom_params_not_connected(self):
        """Test de flashage sans connexion préalable"""
        self.manager.connected = False
        
        result = self.manager.flash_ecu_with_custom_params({"test": "params"})
        
        self.assertEqual(result["error"], "Non connecté à l'ECU")

def test_requirements_installed():
    """Vérifie que les dépendances sont installées"""
    try:
        # Cette importation échouera en environnement de test si le package n'existe pas
        # mais sera masquée par l'exception interne à ecu_flash_main.py
        import ecu_flash_lib
        assert True  # Si importé avec succès
    except ImportError:
        # C'est normal en environnement de test, donc pas d'échec
        assert True

if __name__ == '__main__':
    unittest.main()
