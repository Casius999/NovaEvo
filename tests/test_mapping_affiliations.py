import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import du module à tester
from mapping_affiliations.mapping_affiliations_main import search_mapping_offers, search_official_api, search_facebook_marketplace_mapping, search_leboncoin_mapping, get_demo_data, generate_affiliate_link

class TestMappingAffiliations(unittest.TestCase):
    
    @patch('mapping_affiliations.mapping_affiliations_main.search_official_api')
    @patch('mapping_affiliations.mapping_affiliations_main.search_facebook_marketplace_mapping')
    @patch('mapping_affiliations.mapping_affiliations_main.search_leboncoin_mapping')
    def test_search_mapping_offers(self, mock_leboncoin, mock_facebook, mock_official_api):
        """Test de la recherche globale de cartographies"""
        # Configuration des mocks
        mock_official_api.return_value = [
            {
                'preparateur': 'TunerPro',
                'description': 'Stage 1 pour Golf 7 GTI',
                'price': '249.90€',
                'category': 'sport',
                'source': 'API Partenaire',
                'affiliate_link': 'https://tunerpro.com/cart/golf7?ref=assistant-auto'
            }
        ]
        
        mock_facebook.return_value = [
            {
                'preparateur': 'BoostMyRide',
                'description': 'Reprog Golf 7 Stage 2',
                'price': '299.90€',
                'category': 'sport',
                'source': 'Facebook Marketplace',
                'affiliate_link': 'https://marketplace.facebook.com/item/123?ref=assistant-auto'
            }
        ]
        
        mock_leboncoin.return_value = []
        
        # Exécution de la fonction à tester
        results = search_mapping_offers(query="cartographie golf 7 gti", category="sport")
        
        # Vérifications
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['preparateur'], 'TunerPro')
        self.assertEqual(results[1]['preparateur'], 'BoostMyRide')
        mock_official_api.assert_called_once_with("cartographie golf 7 gti", "sport")
        mock_facebook.assert_called_once_with("cartographie golf 7 gti", "sport")
        mock_leboncoin.assert_called_once_with("cartographie golf 7 gti", "sport")
    
    @patch('mapping_affiliations.mapping_affiliations_main.requests.get')
    def test_search_official_api(self, mock_get):
        """Test de recherche via l'API officielle de partenaires"""
        # Configuration du mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "preparateur": "TunerPro",
                    "description": "Stage 1 pour Golf 7 GTI",
                    "price": 249.90,
                    "category": "sport",
                    "url": "https://tunerpro.com/cart/golf7"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Exécution de la fonction à tester
        with patch('mapping_affiliations.mapping_affiliations_main.generate_affiliate_link') as mock_generate:
            mock_generate.return_value = "https://tunerpro.com/cart/golf7?ref=assistant-auto"
            results = search_official_api("cartographie golf 7 gti", "sport")
        
        # Vérifications
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['preparateur'], 'TunerPro')
        self.assertEqual(results[0]['price'], '249.90€')
        self.assertEqual(results[0]['affiliate_link'], 'https://tunerpro.com/cart/golf7?ref=assistant-auto')
    
    def test_generate_affiliate_link(self):
        """Test de génération d'un lien d'affiliation"""
        # URLs de test
        url1 = "https://example.com/product/123"
        url2 = "https://example.com/product/123?param=value"
        
        # Exécution de la fonction à tester
        result1 = generate_affiliate_link(url1)
        result2 = generate_affiliate_link(url2)
        
        # Vérifications
        self.assertEqual(result1, "https://example.com/product/123?ref=assistant-auto-ultime")
        self.assertEqual(result2, "https://example.com/product/123?param=value&ref=assistant-auto-ultime")
    
    def test_get_demo_data(self):
        """Test de génération des données de démonstration"""
        # Exécution de la fonction à tester
        results = get_demo_data("cartographie golf 7 gti", "sport")
        
        # Vérifications
        self.assertTrue(len(results) > 0)
        for result in results:
            self.assertIn('preparateur', result)
            self.assertIn('description', result)
            self.assertIn('price', result)
            self.assertIn('category', result)
            self.assertIn('source', result)
            self.assertIn('affiliate_link', result)
            # Vérifier que la catégorie correspond bien à celle demandée
            if 'category' in result:
                self.assertEqual(result['category'], 'sport')

if __name__ == '__main__':
    unittest.main()