"""
NovaEvo - Vérification de Sécurité pour Modules Contextuels

Ce module fournit des fonctions pour vérifier l'authenticité et la sécurité
des sources de données contextuelles et des communications avec les serveurs externes.
"""

import os
import json
import hmac
import hashlib
import logging
import requests
import ssl
import socket
import threading
import time
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

# Configuration du logger
logger = logging.getLogger('novaevo.security')

class SecurityChecker:
    """
    Vérificateur de sécurité pour les communications avec les serveurs externes
    """
    
    def __init__(self):
        """
        Initialise le vérificateur de sécurité
        """
        self.trusted_servers = {}
        self.public_keys = {}
        self.certificates = {}
        self.server_fingerprints = {}
        self.blacklist = set()
        self.check_interval = int(os.getenv('SECURITY_CHECK_INTERVAL', '86400'))  # 24h par défaut
        self.running = False
        self.check_thread = None
        
        # Charger les serveurs de confiance
        self._load_trusted_servers()
        
    def verify_server(self, server_url: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Vérifie la sécurité d'un serveur
        
        Args:
            server_url (str): URL du serveur à vérifier
            api_key (str, optional): Clé API pour l'authentification
            
        Returns:
            Dict[str, Any]: Résultat de la vérification
        """
        result = {
            'server_url': server_url,
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'overall_status': 'unknown'
        }
        
        try:
            # Extraire le domaine de l'URL
            domain = server_url.split('/')[2]
            
            # Vérifier si le serveur est dans la liste noire
            if server_url in self.blacklist or domain in self.blacklist:
                result['checks']['blacklist'] = {
                    'status': 'failed',
                    'message': 'Serveur dans la liste noire'
                }
                result['overall_status'] = 'failed'
                return result
                
            # Vérifier le certificat TLS
            result['checks']['tls'] = self._check_tls_certificate(domain)
            
            # Vérifier l'empreinte du serveur
            result['checks']['fingerprint'] = self._check_server_fingerprint(server_url)
            
            # Vérifier l'API de sécurité du serveur
            result['checks']['security_api'] = self._check_security_api(server_url, api_key)
            
            # Vérifier la disponibilité et le temps de réponse
            result['checks']['availability'] = self._check_availability(server_url)
            
            # Déterminer le statut global
            failed_checks = [check for check, data in result['checks'].items() if data['status'] == 'failed']
            
            if failed_checks:
                result['overall_status'] = 'failed'
            else:
                warning_checks = [check for check, data in result['checks'].items() if data['status'] == 'warning']
                if warning_checks:
                    result['overall_status'] = 'warning'
                else:
                    result['overall_status'] = 'passed'
                    
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du serveur {server_url}: {str(e)}")
            result['checks']['error'] = {
                'status': 'failed',
                'message': f"Erreur lors de la vérification: {str(e)}"
            }
            result['overall_status'] = 'failed'
            return result
            
    def register_trusted_server(self, server_url: str, fingerprint: str, 
                               public_key: Optional[str] = None) -> bool:
        """
        Enregistre un serveur de confiance
        
        Args:
            server_url (str): URL du serveur
            fingerprint (str): Empreinte du serveur
            public_key (str, optional): Clé publique du serveur
            
        Returns:
            bool: True si l'enregistrement a réussi, False sinon
        """
        try:
            # Extraire le domaine de l'URL
            domain = server_url.split('/')[2]
            
            # Enregistrer le serveur
            self.trusted_servers[server_url] = {
                'domain': domain,
                'fingerprint': fingerprint,
                'public_key': public_key,
                'last_verified': datetime.now().isoformat(),
                'status': 'trusted'
            }
            
            # Enregistrer l'empreinte
            self.server_fingerprints[server_url] = fingerprint
            
            # Enregistrer la clé publique
            if public_key:
                self.public_keys[server_url] = public_key
                
            # Sauvegarder les serveurs de confiance
            self._save_trusted_servers()
            
            logger.info(f"Serveur de confiance enregistré: {server_url}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du serveur de confiance {server_url}: {str(e)}")
            return False
            
    def unregister_trusted_server(self, server_url: str) -> bool:
        """
        Supprime un serveur de confiance
        
        Args:
            server_url (str): URL du serveur
            
        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        try:
            # Supprimer le serveur
            if server_url in self.trusted_servers:
                del self.trusted_servers[server_url]
                
            # Supprimer l'empreinte
            if server_url in self.server_fingerprints:
                del self.server_fingerprints[server_url]
                
            # Supprimer la clé publique
            if server_url in self.public_keys:
                del self.public_keys[server_url]
                
            # Sauvegarder les serveurs de confiance
            self._save_trusted_servers()
            
            logger.info(f"Serveur de confiance supprimé: {server_url}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du serveur de confiance {server_url}: {str(e)}")
            return False
            
    def blacklist_server(self, server_url: str, reason: str) -> bool:
        """
        Ajoute un serveur à la liste noire
        
        Args:
            server_url (str): URL du serveur
            reason (str): Raison du blacklistage
            
        Returns:
            bool: True si l'ajout a réussi, False sinon
        """
        try:
            # Ajouter le serveur à la liste noire
            self.blacklist.add(server_url)
            
            # Extraire le domaine et l'ajouter également
            domain = server_url.split('/')[2]
            self.blacklist.add(domain)
            
            # Sauvegarder la liste noire
            self._save_blacklist()
            
            # Journaliser l'événement
            logger.warning(f"Serveur blacklisté: {server_url} - Raison: {reason}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du blacklistage du serveur {server_url}: {str(e)}")
            return False
            
    def verify_data_signature(self, data: Dict[str, Any], signature: str, 
                             server_url: str) -> bool:
        """
        Vérifie la signature des données
        
        Args:
            data (Dict[str, Any]): Données à vérifier
            signature (str): Signature à vérifier
            server_url (str): URL du serveur source
            
        Returns:
            bool: True si la signature est valide, False sinon
        """
        try:
            # Vérifier si nous avons la clé publique du serveur
            if server_url not in self.public_keys:
                logger.warning(f"Pas de clé publique pour le serveur {server_url}")
                return False
                
            # Sérialiser les données
            data_str = json.dumps(data, sort_keys=True)
            
            # Récupérer la clé publique
            public_key_pem = self.public_keys[server_url]
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
            
            # Vérifier la signature
            try:
                public_key.verify(
                    bytes.fromhex(signature),
                    data_str.encode('utf-8'),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True
            except InvalidSignature:
                logger.warning(f"Signature invalide pour les données du serveur {server_url}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la signature des données: {str(e)}")
            return False
            
    def verify_hmac(self, data: Dict[str, Any], hmac_signature: str, 
                   server_url: str, api_key: str) -> bool:
        """
        Vérifie la signature HMAC des données
        
        Args:
            data (Dict[str, Any]): Données à vérifier
            hmac_signature (str): Signature HMAC à vérifier
            server_url (str): URL du serveur source
            api_key (str): Clé API pour le HMAC
            
        Returns:
            bool: True si la signature est valide, False sinon
        """
        try:
            # Sérialiser les données
            data_str = json.dumps(data, sort_keys=True)
            
            # Calculer le HMAC
            h = hmac.new(api_key.encode('utf-8'), data_str.encode('utf-8'), hashlib.sha256)
            calculated_signature = h.hexdigest()
            
            # Vérifier la signature
            return hmac.compare_digest(calculated_signature, hmac_signature)
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du HMAC: {str(e)}")
            return False
            
    def start_periodic_checks(self) -> None:
        """
        Démarre les vérifications périodiques des serveurs
        """
        if self.running:
            logger.warning("Les vérifications périodiques sont déjà en cours")
            return
            
        self.running = True
        
        def check_worker():
            """Fonction de vérification périodique"""
            while self.running:
                try:
                    self._check_all_servers()
                except Exception as e:
                    logger.error(f"Erreur lors de la vérification périodique: {str(e)}")
                    
                time.sleep(self.check_interval)
                
        self.check_thread = threading.Thread(target=check_worker, daemon=True)
        self.check_thread.start()
        
        logger.info(f"Vérifications périodiques démarrées (intervalle: {self.check_interval}s)")
        
    def stop_periodic_checks(self) -> None:
        """
        Arrête les vérifications périodiques des serveurs
        """
        self.running = False
        if self.check_thread:
            # Pas besoin de join() car le thread est daemon
            self.check_thread = None
            
        logger.info("Vérifications périodiques arrêtées")
        
    def _check_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """
        Vérifie tous les serveurs de confiance
        
        Returns:
            Dict[str, Dict[str, Any]]: Résultats des vérifications
        """
        results = {}
        
        for server_url in list(self.trusted_servers.keys()):
            # Vérifier le serveur
            result = self.verify_server(server_url)
            
            # Mettre à jour le statut
            self.trusted_servers[server_url]['last_verified'] = datetime.now().isoformat()
            self.trusted_servers[server_url]['status'] = result['overall_status']
            
            # Si le serveur a échoué à la vérification, le blacklister
            if result['overall_status'] == 'failed':
                reason = "Échec de la vérification périodique"
                self.blacklist_server(server_url, reason)
                self.unregister_trusted_server(server_url)
                
            results[server_url] = result
            
        # Sauvegarder les serveurs de confiance
        self._save_trusted_servers()
        
        return results
        
    def _check_tls_certificate(self, domain: str) -> Dict[str, Any]:
        """
        Vérifie le certificat TLS d'un domaine
        
        Args:
            domain (str): Domaine à vérifier
            
        Returns:
            Dict[str, Any]: Résultat de la vérification
        """
        try:
            context = ssl.create_default_context()
            conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
            conn.settimeout(5.0)
            conn.connect((domain, 443))
            cert = conn.getpeercert()
            
            # Vérifier la date d'expiration
            expire_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
            days_left = (expire_date - datetime.now()).days
            
            if days_left <= 0:
                return {
                    'status': 'failed',
                    'message': f"Certificat expiré depuis {-days_left} jours"
                }
            elif days_left <= 30:
                return {
                    'status': 'warning',
                    'message': f"Certificat expire dans {days_left} jours"
                }
            else:
                return {
                    'status': 'passed',
                    'message': f"Certificat valide, expire dans {days_left} jours"
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du certificat TLS pour {domain}: {str(e)}")
            return {
                'status': 'failed',
                'message': f"Erreur: {str(e)}"
            }
            
    def _check_server_fingerprint(self, server_url: str) -> Dict[str, Any]:
        """
        Vérifie l'empreinte d'un serveur
        
        Args:
            server_url (str): URL du serveur à vérifier
            
        Returns:
            Dict[str, Any]: Résultat de la vérification
        """
        try:
            # Vérifier si nous avons une empreinte enregistrée
            if server_url not in self.server_fingerprints:
                return {
                    'status': 'warning',
                    'message': "Pas d'empreinte enregistrée"
                }
                
            # Récupérer l'empreinte du serveur
            response = requests.get(f"{server_url}/api/fingerprint", timeout=5)
            
            if response.status_code != 200:
                return {
                    'status': 'warning',
                    'message': f"Impossible de récupérer l'empreinte: {response.status_code}"
                }
                
            current_fingerprint = response.text.strip()
            expected_fingerprint = self.server_fingerprints[server_url]
            
            # Vérifier l'empreinte
            if current_fingerprint == expected_fingerprint:
                return {
                    'status': 'passed',
                    'message': "Empreinte valide"
                }
            else:
                logger.warning(f"Empreinte invalide pour {server_url}: attendu {expected_fingerprint}, reçu {current_fingerprint}")
                return {
                    'status': 'failed',
                    'message': "Empreinte invalide"
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'empreinte pour {server_url}: {str(e)}")
            return {
                'status': 'failed',
                'message': f"Erreur: {str(e)}"
            }
            
    def _check_security_api(self, server_url: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Vérifie l'API de sécurité d'un serveur
        
        Args:
            server_url (str): URL du serveur à vérifier
            api_key (str, optional): Clé API pour l'authentification
            
        Returns:
            Dict[str, Any]: Résultat de la vérification
        """
        try:
            headers = {}
            if api_key:
                headers['Authorization'] = f"Bearer {api_key}"
                
            # Appeler l'API de sécurité
            response = requests.get(f"{server_url}/api/security-check", headers=headers, timeout=5)
            
            if response.status_code != 200:
                return {
                    'status': 'warning',
                    'message': f"API de sécurité non disponible: {response.status_code}"
                }
                
            result = response.json()
            
            # Vérifier la version de l'API
            if 'api_version' in result:
                if result['api_version'] < 1.0:
                    return {
                        'status': 'warning',
                        'message': f"Version d'API obsolète: {result['api_version']}"
                    }
                    
            # Vérifier les tests de sécurité
            if 'security_tests' in result:
                failed_tests = [test for test in result['security_tests'] if test['status'] == 'failed']
                if failed_tests:
                    return {
                        'status': 'warning',
                        'message': f"{len(failed_tests)} tests de sécurité échoués"
                    }
                    
            return {
                'status': 'passed',
                'message': "API de sécurité validée"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'API de sécurité pour {server_url}: {str(e)}")
            return {
                'status': 'warning',
                'message': f"Erreur: {str(e)}"
            }
            
    def _check_availability(self, server_url: str) -> Dict[str, Any]:
        """
        Vérifie la disponibilité d'un serveur
        
        Args:
            server_url (str): URL du serveur à vérifier
            
        Returns:
            Dict[str, Any]: Résultat de la vérification
        """
        try:
            start_time = time.time()
            response = requests.get(f"{server_url}/api/health", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                return {
                    'status': 'failed',
                    'message': f"Serveur non disponible: {response.status_code}"
                }
                
            # Vérifier le temps de réponse
            if response_time > 1.0:
                return {
                    'status': 'warning',
                    'message': f"Temps de réponse élevé: {response_time:.2f}s"
                }
                
            return {
                'status': 'passed',
                'message': f"Serveur disponible, temps de réponse: {response_time:.2f}s"
            }
            
        except requests.exceptions.Timeout:
            return {
                'status': 'failed',
                'message': "Délai d'attente dépassé"
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'failed',
                'message': "Erreur de connexion"
            }
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la disponibilité pour {server_url}: {str(e)}")
            return {
                'status': 'failed',
                'message': f"Erreur: {str(e)}"
            }
            
    def _load_trusted_servers(self) -> None:
        """
        Charge les serveurs de confiance depuis un fichier
        """
        try:
            file_path = os.path.join('data', 'security', 'trusted_servers.json')
            
            if not os.path.exists(file_path):
                logger.info("Fichier des serveurs de confiance non trouvé, création d'un nouveau fichier")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                self.trusted_servers = {}
                self._save_trusted_servers()
                return
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.trusted_servers = data.get('servers', {})
            
            # Extraire les empreintes et les clés publiques
            for server_url, server_data in self.trusted_servers.items():
                if 'fingerprint' in server_data:
                    self.server_fingerprints[server_url] = server_data['fingerprint']
                if 'public_key' in server_data and server_data['public_key']:
                    self.public_keys[server_url] = server_data['public_key']
                    
            logger.info(f"Serveurs de confiance chargés: {len(self.trusted_servers)}")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des serveurs de confiance: {str(e)}")
            self.trusted_servers = {}
            
    def _save_trusted_servers(self) -> None:
        """
        Sauvegarde les serveurs de confiance dans un fichier
        """
        try:
            file_path = os.path.join('data', 'security', 'trusted_servers.json')
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            data = {
                'servers': self.trusted_servers,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Serveurs de confiance sauvegardés: {len(self.trusted_servers)}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des serveurs de confiance: {str(e)}")
            
    def _load_blacklist(self) -> None:
        """
        Charge la liste noire depuis un fichier
        """
        try:
            file_path = os.path.join('data', 'security', 'blacklist.json')
            
            if not os.path.exists(file_path):
                logger.info("Fichier de liste noire non trouvé, création d'un nouveau fichier")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                self.blacklist = set()
                self._save_blacklist()
                return
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.blacklist = set(data.get('servers', []))
            
            logger.info(f"Liste noire chargée: {len(self.blacklist)} serveurs")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la liste noire: {str(e)}")
            self.blacklist = set()
            
    def _save_blacklist(self) -> None:
        """
        Sauvegarde la liste noire dans un fichier
        """
        try:
            file_path = os.path.join('data', 'security', 'blacklist.json')
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            data = {
                'servers': list(self.blacklist),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Liste noire sauvegardée: {len(self.blacklist)} serveurs")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la liste noire: {str(e)}")

# Instance singleton pour l'utilisation dans l'application
security_checker = SecurityChecker()
