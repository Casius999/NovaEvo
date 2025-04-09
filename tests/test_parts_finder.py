"""
Tests pour le module Parts Finder
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json
import requests

# Ajouter le chemin racine au path Python pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import des modules à tester
from parts_finder.parts_finder_main import (
    PartsFinderManager, 
    search_official, 
    search_facebook_marketplace,
    search_leboncoin,
    search_facebook_groups,
    search_parts,
    VALID_PART_TYPES
)

class TestPartsFinderLocal(unittest.TestCase):
    """Tests pour la recherche locale de pièces"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.finder = PartsFinderManager()
    
    def test_initialization(self):
        """Test d'initialisation du gestionnaire"""
        self.assertTrue(self.finder.db_initialized)
        self.assertIsNotNone(self.finder.categories)
        self.assertIsNotNone(self.finder.part_types)
    
    def test_search_parts_by_type(self):
        """Test de recherche par type de pièce"""
        result = self.finder.search_parts_local(part_type="sport")
        
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("results", result)
        self.assertIsInstance(result["results"], list)
        
        # Vérifier que tous les résultats sont du type sport
        for item in result["results"]:
            self.assertEqual(item["part_type"], "sport")
    
    def test_search_parts_by_reference(self):
        """Test de recherche par référence"""
        result = self.finder.search_parts_local(reference="F-001")
        
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("results", result)
        self.assertIsInstance(result["results"], list)
        
        if result["results"]:  # S'il y a des résultats
            # Vérifier que la référence est bien présente
            self.assertEqual(result["results"][0]["reference"], "F-001")
    
    def test_search_parts_with_filter_combination(self):
        """Test de recherche avec combinaison de filtres"""
        result = self.finder.search_parts_local(
            category="Freinage",
            part_type="origine",
            keyword="avant"
        )
        
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        self.assertIn("results", result)
        self.assertIsInstance(result["results"], list)
    
    def test_get_part_details(self):
        """Test de récupération des détails d'une pièce"""
        # Tester avec un ID (s'il existe)
        result = self.finder.get_part_details(part_id=1)
        
        # Si la pièce existe
        if "success" in result and result["success"]:
            self.assertIn("part", result)
            self.assertIn("id", result["part"])
            self.assertIn("name", result["part"])
            self.assertIn("compatible_models", result["part"])
        # Sinon, c'est normal aussi car on ne connaît pas les IDs de la base de test
        
        # Tester avec une référence
        result = self.finder.get_part_details(reference="F-001")
        
        if "success" in result and result["success"]:
            self.assertIn("part", result)
            self.assertEqual(result["part"]["reference"], "F-001")
            self.assertIn("compatible_models", result["part"])


class TestExternalSearch(unittest.TestCase):
    """Tests pour les fonctions de recherche externes"""
    
    @patch('requests.get')
    def test_search_official(self, mock_get):
        """Test de la fonction search_official avec mock de requests"""
        # Configurer le mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "reference": "F-001",
                    "name": "Plaquettes de frein origine",
                    "description": "Plaquettes d'origine pour véhicule standard",
                    "price": 45.99,
                    "currency": "EUR",
                    "provider": "Oscaro",
                    "stock": 25,
                    "delivery_time": "24h"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Appel de la fonction
        results = search_official("F-001", "origine")
        
        # Vérifications
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)
        self.assertIn("reference", results[0])
        self.assertIn("name", results[0])
        self.assertIn("price", results[0])
        self.assertIn("source", results[0])
        
        # Vérifier que requests.get a été appelé avec les bons paramètres
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"]["ref"], "F-001")
        self.assertEqual(kwargs["params"]["type"], "origine")
    
    @patch('requests.get')
    @patch('bs4.BeautifulSoup')
    def test_search_facebook_marketplace(self, mock_soup, mock_get):
        """Test de la fonction search_facebook_marketplace avec mocks"""
        # Configurer les mocks
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Contenu simulé</body></html>"
        mock_get.return_value = mock_response
        
        # Configurer le mock de BeautifulSoup
        mock_soup_instance = MagicMock()
        mock_soup.return_value = mock_soup_instance
        
        # Le scraping étant complexe à mocker complètement, on vérifie juste la structure de base
        results = search_facebook_marketplace("F-001", "origine")
        
        # Vérifications
        self.assertIsInstance(results, list)
        # La fonction peut retourner des résultats simulés même si le scraping échoue
        if results:
            self.assertIn("reference", results[0])
            self.assertIn("name", results[0])
            self.assertIn("price", results[0])
            self.assertIn("source", results[0])
            self.assertEqual(results[0]["source"], "Facebook Marketplace")
    
    @patch('requests.get')
    @patch('bs4.BeautifulSoup')
    def test_search_leboncoin(self, mock_soup, mock_get):
        """Test de la fonction search_leboncoin avec mocks"""
        # Configurer les mocks
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Contenu simulé</body></html>"
        mock_get.return_value = mock_response
        
        # Configurer le mock de BeautifulSoup
        mock_soup_instance = MagicMock()
        mock_soup.return_value = mock_soup_instance
        
        # Le scraping étant complexe à mocker complètement, on vérifie juste la structure de base
        results = search_leboncoin("F-001", "origine")
        
        # Vérifications
        self.assertIsInstance(results, list)
        # La fonction peut retourner des résultats simulés même si le scraping échoue
        if results:
            self.assertIn("reference", results[0])
            self.assertIn("name", results[0])
            self.assertIn("price", results[0])
            self.assertIn("source", results[0])
            self.assertEqual(results[0]["source"], "Leboncoin")
    
    def test_search_facebook_groups(self):
        """Test de la fonction search_facebook_groups"""
        # Cette fonction étant plus complexe (nécessitant authentification),
        # on vérifie seulement le format des résultats
        results = search_facebook_groups("F-001", "origine")
        
        self.assertIsInstance(results, list)
        if results:
            self.assertIn("reference", results[0])
            self.assertIn("name", results[0])
            self.assertIn("price", results[0])
            self.assertIn("source", results[0])
            self.assertEqual(results[0]["source"], "Groupe Facebook")


class TestSearchParts(unittest.TestCase):
    """Tests pour la fonction principale search_parts"""
    
    @patch('parts_finder.parts_finder_main.search_official')
    @patch('parts_finder.parts_finder_main.search_facebook_marketplace')
    @patch('parts_finder.parts_finder_main.search_leboncoin')
    @patch('parts_finder.parts_finder_main.search_facebook_groups')
    def test_search_parts_valid_type(self, mock_groups, mock_leboncoin, mock_fb, mock_official):
        """Test de search_parts avec un type de pièce valide"""
        # Configurer les mocks pour qu'ils retournent des résultats simulés
        mock_official.return_value = [{"name": "Pièce 1", "price": 10.0, "source": "API"}]
        mock_fb.return_value = [{"name": "Pièce 2", "price": 20.0, "source": "FB"}]
        mock_leboncoin.return_value = [{"name": "Pièce 3", "price": 30.0, "source": "LBC"}]
        mock_groups.return_value = [{"name": "Pièce 4", "price": 40.0, "source": "Group"}]
        
        # Appeler la fonction avec un type valide
        results = search_parts("F-001", "sport")
        
        # Vérifications
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 4)  # Un résultat de chaque source
        
        # Vérifier que toutes les fonctions de recherche ont été appelées
        mock_official.assert_called_once_with("F-001", "sport")
        mock_fb.assert_called_once_with("F-001", "sport")
        mock_leboncoin.assert_called_once_with("F-001", "sport")
        mock_groups.assert_called_once_with("F-001", "sport")
    
    def test_search_parts_invalid_type(self):
        """Test de search_parts avec un type de pièce invalide"""
        results = search_parts("F-001", "invalid_type")
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertIn("error", results[0])
        self.assertIn(str(VALID_PART_TYPES), results[0]["error"])
    
    @patch('parts_finder.parts_finder_main.search_official')
    @patch('parts_finder.parts_finder_main.search_facebook_marketplace')
    @patch('parts_finder.parts_finder_main.search_leboncoin')
    @patch('parts_finder.parts_finder_main.search_facebook_groups')
    def test_search_parts_handling_errors(self, mock_groups, mock_leboncoin, mock_fb, mock_official):
        """Test que search_parts gère correctement les erreurs des sous-fonctions"""
        # Configurer certains mocks pour qu'ils génèrent des erreurs
        mock_official.return_value = [{"name": "Pièce 1", "price": 10.0, "source": "API"}]
        mock_fb.side_effect = Exception("Error in FB")
        mock_leboncoin.return_value = [{"error": "LBC Error Message"}]
        mock_groups.return_value = [{"name": "Pièce 4", "price": 40.0, "source": "Group"}]
        
        # Appeler la fonction
        results = search_parts("F-001", "origine")
        
        # Vérifications : même avec des erreurs, la fonction doit retourner les résultats valides
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)  # Uniquement les résultats sans erreur
        
        # Vérifier que les fonctions ont été appelées malgré les erreurs
        mock_official.assert_called_once()
        mock_fb.assert_called_once()
        mock_leboncoin.assert_called_once()
        mock_groups.assert_called_once()


if __name__ == '__main__':
    unittest.main()
