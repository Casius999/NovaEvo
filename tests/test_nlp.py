"""
Tests unitaires pour le module NLP
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les modules à tester
from nlp.nlp_main import AutoAssistantNLP
from app import process_command


class TestNLPModule(unittest.TestCase):
    """Tests pour le module NLP"""

    def setUp(self):
        """Configuration des tests"""
        # Patcher les appels à OpenAI pour éviter d'utiliser l'API réelle pendant les tests
        self.openai_patcher = patch('openai.chat.completions.create')
        self.mock_openai = self.openai_patcher.start()
        
        # Configurer le mock pour retourner une réponse simulée
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Ceci est une réponse simulée de l'API OpenAI."
        self.mock_openai.return_value = mock_response
        
        # Créer une instance de l'assistant NLP avec une clé API factice
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            self.nlp_assistant = AutoAssistantNLP()
        
        # S'assurer que l'assistant est initialisé
        self.nlp_assistant.initialized = True
    
    def tearDown(self):
        """Nettoyage après les tests"""
        self.openai_patcher.stop()
    
    def test_nlp_assistant_initialization(self):
        """Test de l'initialisation de AutoAssistantNLP"""
        self.assertIsNotNone(self.nlp_assistant)
        self.assertTrue(self.nlp_assistant.initialized)
        self.assertEqual(self.nlp_assistant.model, 'gpt-4-turbo-preview')  # Valeur par défaut
    
    def test_error_code_interpretation(self):
        """Test de l'interprétation d'un code d'erreur"""
        # Tester un code d'erreur présent dans la base de connaissances
        result = self.nlp_assistant.interpret_command("Que signifie le code P0300?")
        
        self.assertIsInstance(result, dict)
        self.assertIn("intent", result)
        self.assertEqual(result["intent"], "recherche_code_erreur")
        self.assertIn("code", result["entities"])
        self.assertEqual(result["entities"]["code"], "P0300")
        
        # Vérifier qu'une description est retournée
        self.assertIn("description", result)
        self.assertIsInstance(result["description"], str)
        self.assertTrue(len(result["description"]) > 0)
    
    def test_maintenance_query_interpretation(self):
        """Test de l'interprétation d'une requête d'entretien"""
        result = self.nlp_assistant.interpret_command("Quand dois-je faire ma vidange?")
        
        self.assertIsInstance(result, dict)
        self.assertIn("category", result)
        self.assertEqual(result["category"], "entretien")
        self.assertIn("description", result)
        self.assertIsInstance(result["description"], str)
        self.assertTrue(len(result["description"]) > 0)
    
    def test_interpret_command_api_call(self):
        """Test de l'appel à l'API pour les requêtes complexes"""
        query = "Comment améliorer les performances de ma voiture?"
        
        # Configurer le mock pour simuler une réponse JSON
        self.mock_openai.return_value.choices[0].message.content = '{"category": "performance", "intent": "amélioration", "suggested_action": "Consulter un spécialiste"}'
        
        # Tester l'interprétation
        result = self.nlp_assistant.interpret_command(query)
        
        # Vérifier que l'API a été appelée
        self.mock_openai.assert_called_once()
        
        # Vérifier que le résultat est correct
        self.assertIsInstance(result, dict)
        self.assertIn("category", result)
        self.assertEqual(result["category"], "performance")
        self.assertIn("intent", result)
        self.assertEqual(result["intent"], "amélioration")
    
    def test_process_command_function(self):
        """
        Test de la fonction process_command définie dans app.py
        qui utilise le module NLP
        """
        # Simuler l'interprétation de la commande
        with patch('app.nlp_assistant.interpret_command') as mock_interpret:
            # Configurer le mock pour simuler différents types de réponses
            mock_interpret.return_value = {
                "category": "diagnostic", 
                "intent": "information",
                "description": "Explication simulée",
                "suggested_action": "Action recommandée"
            }
            
            # Tester la fonction
            result = process_command("Comment diagnostiquer un problème de démarrage?")
            
            # Vérifier que l'interprétation a été appelée
            mock_interpret.assert_called_once_with("Comment diagnostiquer un problème de démarrage?")
            
            # Vérifier que la réponse est une chaîne non vide
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
            
            # Vérifier que la réponse contient la description de l'interprétation
            self.assertEqual(result, "Explication simulée")
    
    def test_process_command_with_error(self):
        """Test de la gestion des erreurs dans process_command"""
        # Simuler une erreur d'interprétation
        with patch('app.nlp_assistant.interpret_command') as mock_interpret:
            mock_interpret.return_value = {"error": "Erreur simulée"}
            
            # Tester la fonction
            result = process_command("Requête problématique")
            
            # Vérifier que la réponse indique l'erreur
            self.assertIn("Je n'ai pas pu traiter votre demande", result)
            self.assertIn("Erreur simulée", result)
    
    def test_process_command_with_openai(self):
        """Test de l'utilisation d'OpenAI dans process_command"""
        # Simuler une interprétation sans description directe
        with patch('app.nlp_assistant.interpret_command') as mock_interpret:
            mock_interpret.return_value = {
                "category": "performance",
                "intent": "conseil",
                "entities": {"voiture": "Peugeot 308"}
            }
            
            # Simuler la réponse d'OpenAI
            with patch('openai.chat.completions.create') as mock_openai_completion:
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "Voici mes conseils pour améliorer votre Peugeot 308."
                mock_openai_completion.return_value = mock_response
                
                # Tester la fonction
                result = process_command("Comment améliorer les performances de ma Peugeot 308?")
                
                # Vérifier que OpenAI a été appelé
                mock_openai_completion.assert_called_once()
                
                # Vérifier la réponse
                self.assertEqual(result, "Voici mes conseils pour améliorer votre Peugeot 308.")


if __name__ == '__main__':
    unittest.main()
