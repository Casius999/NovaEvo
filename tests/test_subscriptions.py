import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import du module à tester
from subscriptions.subscriptions_main import process_subscription, webhook_handler, get_subscription_status

class TestSubscriptions(unittest.TestCase):
    
    @patch('subscriptions.subscriptions_main.stripe')
    @patch('subscriptions.subscriptions_main.User')
    def test_process_subscription(self, mock_user, mock_stripe):
        """Test du processus de création d'abonnement"""
        # Configuration des mocks
        mock_stripe.Customer.create.return_value = MagicMock(id='cus_test123')
        mock_stripe.Subscription.create.return_value = MagicMock(
            id='sub_test123',
            status='active'
        )
        mock_user_instance = MagicMock()
        mock_user.return_value = mock_user_instance
        
        # Données de test
        user_data = {
            "email": "test@example.com",
            "password": "securepassword123",
            "name": "Test User",
            "plan_id": "price_basic"
        }
        
        # Exécution de la fonction à tester
        result = process_subscription(user_data)
        
        # Vérifications
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['subscription_id'], 'sub_test123')
        mock_stripe.Customer.create.assert_called_once_with(
            email=user_data['email'],
            name=user_data['name']
        )
        mock_stripe.Subscription.create.assert_called_once()
        mock_user_instance.save.assert_called_once()
    
    @patch('subscriptions.subscriptions_main.stripe')
    def test_webhook_handler_subscription_created(self, mock_stripe):
        """Test du gestionnaire de webhook pour un événement de création d'abonnement"""
        # Configuration des mocks
        mock_stripe.Webhook.construct_event.return_value = {
            'type': 'customer.subscription.created',
            'data': {
                'object': {
                    'id': 'sub_test123',
                    'customer': 'cus_test123',
                    'status': 'active'
                }
            }
        }
        
        # Simuler une charge utile de webhook et une signature
        payload = json.dumps({}).encode('utf-8')
        sig_header = 'dummy_signature'
        
        # Exécution de la fonction à tester
        with patch('subscriptions.subscriptions_main.update_user_subscription') as mock_update:
            result = webhook_handler(payload, sig_header)
        
        # Vérifications
        self.assertEqual(result['status'], 'success')
        mock_update.assert_called_once_with('cus_test123', 'sub_test123', 'active')
    
    @patch('subscriptions.subscriptions_main.User')
    def test_get_subscription_status(self, mock_user):
        """Test de la récupération du statut d'abonnement"""
        # Configuration des mocks
        mock_user.query.filter_by.return_value.first.return_value = MagicMock(
            subscription_id='sub_test123',
            subscription_status='active'
        )
        
        # Exécution de la fonction à tester
        status = get_subscription_status('test@example.com')
        
        # Vérifications
        self.assertEqual(status, 'active')
        mock_user.query.filter_by.assert_called_once_with(email='test@example.com')

if __name__ == '__main__':
    unittest.main()