"""
NovaEvo - Gestionnaire de Synchronisation Contextuelle

Ce module gère la synchronisation des données contextuelles avec des serveurs dédiés.
Il fournit des mécanismes pour la récupération, la mise en cache et l'invalidation
de données tierces afin d'enrichir l'expérience utilisateur.
"""

import os
import json
import time
import hashlib
import logging
import threading
import requests
import ssl
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from urllib.parse import urlparse

# Configuration du logger
logger = logging.getLogger('novaevo.context_sync')

class ContextModule:
    """
    Représentation d'un module contextuel externe avec sécurité et validation des données renforcées
    """
    
    def __init__(self, module_id: str, server_url: str, api_key: Optional[str] = None):
        """
        Initialise un module contextuel
        
        Args:
            module_id (str): Identifiant unique du module
            server_url (str): URL du serveur dédié
            api_key (str, optional): Clé API pour l'authentification
        """
        self.id = module_id
        self.server_url = server_url
        self.api_key = api_key
        self.data = {}
        self.last_sync = None
        self.status = 'registered'
        self.error_count = 0
        self.max_errors = 5
        self.data_version = None
        self.last_verified = None
        self.verification_hash = None
        self.ssl_context = self._create_ssl_context()
        self.server_certificate = None
        # Établir un plan de sauvegarde des données en cas d'indisponibilité temporaire
        self.fallback_data = {}
        # Vérifier l'URL du serveur pour la sécurité
        self._validate_server_url(server_url)
        
    def sync(self, force: bool = False) -> bool:
        """
        Synchronise les données avec le serveur de manière sécurisée
        
        Args:
            force (bool): Forcer la synchronisation même si une version récente est disponible
            
        Returns:
            bool: True si la synchronisation a réussi, False sinon
        """
        try:
            # Vérifier l'intégrité des données avant de synchroniser
            if not force and self.data and self.verification_hash:
                self.verify_data_integrity()
                
            headers = {}
            if self.api_key:
                headers['Authorization'] = f"Bearer {self.api_key}"
                
            # Ajouter l'en-tête If-None-Match si nous avons une version
            if self.data_version and not force:
                headers['If-None-Match'] = self.data_version
                
            # Ajouter des en-têtes de sécurité
            headers['X-Request-ID'] = f"{self.id}-{int(time.time())}"
            headers['User-Agent'] = 'NovaEvo-ContextSync/1.0'
                
            # Récupérer les données du serveur avec vérification SSL
            response = requests.get(
                f"{self.server_url}/api/data",
                headers=headers,
                timeout=30,
                verify=True  # Vérification SSL
            )
            
            # Traiter la réponse selon le code
            if response.status_code == 200:
                response_data = response.json()
                
                # Vérifier que les données sont valides
                if not isinstance(response_data, dict):
                    logger.error(f"Format de données invalide pour {self.id}: attendu dict, reçu {type(response_data)}")
                    self.error_count += 1
                    return False
                    
                self.data = response_data
                self.last_sync = datetime.now()
                self.status = 'active'
                self.error_count = 0
                
                # Stocker la version des données
                if 'ETag' in response.headers:
                    self.data_version = response.headers['ETag']
                
                # Enregistrer l'empreinte digitale du serveur pour vérification ultérieure
                if hasattr(response, 'raw') and hasattr(response.raw, 'connection') and hasattr(response.raw.connection, 'sock'):
                    sock = response.raw.connection.sock
                    if hasattr(sock, 'getpeercert'):
                        self.server_certificate = sock.getpeercert()
                    
                # Sauvegarder les données en cache (crée aussi le hash d'intégrité)
                self._save_to_cache()
                
                logger.info(f"Module {self.id} synchronisé avec succès")
                return True
                
            elif response.status_code == 304:
                # Pas de modification depuis la dernière synchronisation
                self.last_sync = datetime.now()
                self.status = 'active'
                self.error_count = 0
                
                logger.info(f"Module {self.id} déjà à jour (304 Not Modified)")
                return True
                
            else:
                logger.warning(f"Échec de synchronisation du module {self.id}: {response.status_code}")
                self.error_count += 1
                
                if self.error_count >= self.max_errors:
                    self.status = 'error'
                    # Utiliser les données de fallback si disponibles
                    if self.fallback_data and not self.data:
                        logger.info(f"Utilisation des données de secours pour {self.id}")
                        self.data = self.fallback_data.copy()
                
                return False
                
        except ssl.SSLError as ssl_err:
            logger.error(f"Erreur SSL lors de la synchronisation du module {self.id}: {str(ssl_err)}")
            self.error_count += 1
            self.status = 'error' if self.error_count >= self.max_errors else 'ssl_error'
            return False
                
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Erreur réseau lors de la synchronisation du module {self.id}: {str(req_err)}")
            self.error_count += 1
            
            if self.error_count >= self.max_errors:
                self.status = 'error'
                # Utiliser les données de fallback si disponibles
                if self.fallback_data and not self.data:
                    logger.info(f"Utilisation des données de secours pour {self.id}")
                    self.data = self.fallback_data.copy()
                
            return False
            
        except json.JSONDecodeError as json_err:
            logger.error(f"Erreur de décodage JSON pour {self.id}: {str(json_err)}")
            self.error_count += 1
            self.status = 'error' if self.error_count >= self.max_errors else 'format_error'
            return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation du module {self.id}: {str(e)}")
            self.error_count += 1
            
            if self.error_count >= self.max_errors:
                self.status = 'error'
                # Utiliser les données de fallback si disponibles
                if self.fallback_data and not self.data:
                    logger.info(f"Utilisation des données de secours pour {self.id}")
                    self.data = self.fallback_data.copy()
                
            return False
            
    def get_data(self, path: Optional[str] = None) -> Any:
        """
        Récupère les données contextuelles
        
        Args:
            path (str, optional): Chemin d'accès spécifique dans les données (format dot notation)
            
        Returns:
            any: Données contextuelles demandées
        """
        # Si les données sont vides, essayer de les charger depuis le cache
        if not self.data:
            self._load_from_cache()
            
        if path:
            # Naviguer dans la structure de données selon le chemin
            data = self.data
            for key in path.split('.'):
                if isinstance(data, dict) and key in data:
                    data = data[key]
                else:
                    return None
            return data
        else:
            return self.data
            
    def _save_to_cache(self) -> None:
        """
        Sauvegarde les données dans un fichier cache avec vérification d'intégrité
        """
        try:
            cache_dir = os.path.join('data', 'cache', 'context')
            os.makedirs(cache_dir, exist_ok=True)
            
            cache_file = os.path.join(cache_dir, f"{self.id}.json")
            
            # Créer un hash pour l'intégrité des données
            data_str = json.dumps(self.data, sort_keys=True)
            data_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
            
            cache_data = {
                'data': self.data,
                'version': self.data_version,
                'timestamp': datetime.now().isoformat(),
                'server_url': self.server_url,
                'hash': data_hash
            }
            
            # Créer un fichier temporaire d'abord pour éviter la corruption
            temp_file = f"{cache_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            # Remplacer le fichier de cache actuel par le nouveau
            os.replace(temp_file, cache_file)
            
            # Mettre à jour les données de secours
            self.fallback_data = self.data.copy()
            self.verification_hash = data_hash
                
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du cache pour {self.id}: {str(e)}")
            
    def _load_from_cache(self) -> bool:
        """
        Charge les données depuis le fichier cache
        
        Returns:
            bool: True si les données ont été chargées avec succès, False sinon
        """
        try:
            cache_file = os.path.join('data', 'cache', 'context', f"{self.id}.json")
            
            if not os.path.exists(cache_file):
                return False
                
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Vérifier que les données ne sont pas trop anciennes (max 24h)
            timestamp = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - timestamp > timedelta(hours=24):
                logger.warning(f"Données de cache trop anciennes pour {self.id}")
                return False
                
            # Vérifier l'intégrité des données par le hash
            if 'hash' in cache_data:
                data_str = json.dumps(cache_data['data'], sort_keys=True)
                computed_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
                if computed_hash != cache_data['hash']:
                    logger.warning(f"Intégrité des données compromise pour {self.id}, hash invalide")
                    return False
                    
            self.data = cache_data['data']
            self.data_version = cache_data.get('version')
            self.last_sync = timestamp
            
            # Sauvegarder comme données de secours
            self.fallback_data = self.data.copy()
            
            logger.info(f"Données chargées depuis le cache pour {self.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du cache pour {self.id}: {str(e)}")
            return False
            
    def _create_ssl_context(self) -> ssl.SSLContext:
        """
        Crée un contexte SSL sécurisé pour les communications avec le serveur
        
        Returns:
            ssl.SSLContext: Contexte SSL configuré
        """
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        return context
        
    def _validate_server_url(self, url: str) -> bool:
        """
        Vérifie que l'URL du serveur est sécurisée (HTTPS) et valide
        
        Args:
            url (str): URL à valider
            
        Returns:
            bool: True si l'URL est valide et sécurisée
        """
        try:
            parsed = urlparse(url)
            if parsed.scheme != 'https':
                logger.warning(f"L'URL du serveur {self.id} n'utilise pas HTTPS: {url}")
                return False
                
            # Vérifier que le domaine est valide
            if not parsed.netloc or '.' not in parsed.netloc:
                logger.warning(f"L'URL du serveur {self.id} a un domaine invalide: {url}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la validation de l'URL pour {self.id}: {str(e)}")
            return False
            
    def verify_data_integrity(self) -> bool:
        """
        Vérifie l'intégrité des données actuelles
        
        Returns:
            bool: True si les données sont intègres
        """
        if not self.data or not self.verification_hash:
            return False
            
        data_str = json.dumps(self.data, sort_keys=True)
        current_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
        
        if current_hash != self.verification_hash:
            logger.warning(f"Intégrité des données compromise pour {self.id}")
            if self.fallback_data:
                logger.info(f"Restauration des données de secours pour {self.id}")
                self.data = self.fallback_data.copy()
            return False
            
        return True


class ContextSyncManager:
    """
    Gestionnaire de synchronisation des modules contextuels avec gestion avancée et métriques
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire de synchronisation
        """
        self.modules = {}
        self.sync_interval = int(os.getenv('SYNC_INTERVAL', '300'))  # En secondes
        self.sync_thread = None
        self.running = False
        self.listeners = []
        self.metrics = {
            'sync_count': 0,
            'success_count': 0,
            'error_count': 0,
            'last_metrics_reset': datetime.now().isoformat(),
            'module_metrics': {}
        }
        self.adaptive_sync = os.getenv('ADAPTIVE_SYNC', 'True').lower() in ('true', '1', 't')
        self.module_priorities = {}
        
    def register_module(self, module_id: str, server_url: str, api_key: Optional[str] = None) -> None:
        """
        Enregistre un nouveau module contextuel
        
        Args:
            module_id (str): Identifiant unique du module
            server_url (str): URL du serveur dédié
            api_key (str, optional): Clé API pour l'authentification
        """
        if module_id in self.modules:
            logger.warning(f"Le module {module_id} est déjà enregistré")
            return
            
        self.modules[module_id] = ContextModule(module_id, server_url, api_key)
        logger.info(f"Module contextuel enregistré: {module_id} -> {server_url}")
        
    def register_listener(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Enregistre un listener pour les mises à jour de données
        
        Args:
            callback (Callable): Fonction à appeler lors d'une mise à jour
                La fonction doit accepter deux paramètres:
                - module_id (str): Identifiant du module mis à jour
                - data (Dict): Nouvelles données
        """
        if callback not in self.listeners:
            self.listeners.append(callback)
            
    def sync_module(self, module_id: str, force: bool = False) -> bool:
        """
        Synchronise un module spécifique
        
        Args:
            module_id (str): Identifiant du module à synchroniser
            force (bool): Forcer la synchronisation même si une version récente est disponible
            
        Returns:
            bool: True si la synchronisation a réussi, False sinon
        """
        if module_id not in self.modules:
            logger.error(f"Module non enregistré: {module_id}")
            return False
            
        # Initialiser les métriques du module si nécessaire
        if module_id not in self.metrics['module_metrics']:
            self.metrics['module_metrics'][module_id] = {
                'sync_count': 0,
                'success_count': 0,
                'error_count': 0,
                'last_change': None
            }
            
        # Récupérer l'ancien état pour comparaison
        old_data_hash = self._hash_data(self.modules[module_id].data)
        
        # Temps de début pour mesurer la performance
        start_time = time.time()
        
        # Synchroniser le module
        result = self.modules[module_id].sync(force)
        
        # Temps d'exécution
        execution_time = time.time() - start_time
        
        # Mettre à jour les métriques du module
        self.metrics['module_metrics'][module_id]['sync_count'] += 1
        if result:
            self.metrics['module_metrics'][module_id]['success_count'] += 1
        else:
            self.metrics['module_metrics'][module_id]['error_count'] += 1
        
        # Enregistrer le temps d'exécution
        if 'execution_times' not in self.metrics['module_metrics'][module_id]:
            self.metrics['module_metrics'][module_id]['execution_times'] = []
            
        self.metrics['module_metrics'][module_id]['execution_times'].append(execution_time)
        # Garder seulement les 10 derniers temps
        self.metrics['module_metrics'][module_id]['execution_times'] = \
            self.metrics['module_metrics'][module_id]['execution_times'][-10:]
        
        # Calculer le temps moyen
        self.metrics['module_metrics'][module_id]['avg_execution_time'] = \
            sum(self.metrics['module_metrics'][module_id]['execution_times']) / \
            len(self.metrics['module_metrics'][module_id]['execution_times'])
        
        if result:
            # Vérifier si les données ont changé
            new_data_hash = self._hash_data(self.modules[module_id].data)
            
            if old_data_hash != new_data_hash:
                logger.info(f"Données modifiées pour le module {module_id}")
                self.metrics['module_metrics'][module_id]['last_change'] = datetime.now().isoformat()
                
                # Adapter la priorité si la synchronisation adaptative est activée
                if self.adaptive_sync:
                    # Augmenter la priorité si les données changent souvent
                    current_priority = self.module_priorities.get(module_id, 5)
                    # Priorité plus haute (valeur plus basse) pour les modules qui changent
                    new_priority = max(0, current_priority - 1) 
                    self.module_priorities[module_id] = new_priority
                    logger.debug(f"Priorité du module {module_id} ajustée à {new_priority} (données modifiées)")
                
                # Notifier les listeners
                for listener in self.listeners:
                    try:
                        listener(module_id, self.modules[module_id].data)
                    except Exception as e:
                        logger.error(f"Erreur lors de la notification d'un listener: {str(e)}")
                        
            elif self.adaptive_sync:
                # Diminuer légèrement la priorité si les données ne changent pas
                current_priority = self.module_priorities.get(module_id, 5)
                # Priorité plus basse (valeur plus haute) pour les modules stables
                new_priority = min(10, current_priority + 0.5)  
                self.module_priorities[module_id] = new_priority
                logger.debug(f"Priorité du module {module_id} ajustée à {new_priority} (données stables)")
        
        return result
        
    def sync_all_modules(self) -> Dict[str, bool]:
        """
        Synchronise tous les modules enregistrés avec gestion des priorités
        
        Returns:
            dict: Résultats de synchronisation par module
        """
        results = {}
        
        # Si synchronisation adaptative, trier les modules par priorité
        if self.adaptive_sync and self.module_priorities:
            # Trier les modules par priorité (valeur plus basse = priorité plus haute)
            sorted_modules = sorted(self.modules.keys(), 
                                 key=lambda mid: self.module_priorities.get(mid, 999))
        else:
            sorted_modules = list(self.modules.keys())
        
        # Synchroniser les modules dans l'ordre de priorité
        for module_id in sorted_modules:
            results[module_id] = self.sync_module(module_id)
            # Petite pause entre les synchronisations pour ne pas surcharger le réseau
            time.sleep(0.5)
            
        # Mettre à jour les métriques globales
        self.metrics['sync_count'] += len(results)
        self.metrics['success_count'] += sum(1 for success in results.values() if success)
        self.metrics['error_count'] += sum(1 for success in results.values() if not success)
            
        return results
        
    def get_context_data(self, module_id: str, path: Optional[str] = None) -> Any:
        """
        Récupère les données contextuelles d'un module
        
        Args:
            module_id (str): Identifiant du module
            path (str, optional): Chemin d'accès spécifique dans les données (format dot notation)
            
        Returns:
            any: Données contextuelles demandées
        """
        if module_id not in self.modules:
            logger.warning(f"Tentative d'accès à un module non enregistré: {module_id}")
            return None
            
        module = self.modules[module_id]
        
        # Vérifier si une synchronisation est nécessaire
        if module.last_sync is None:
            self.sync_module(module_id)
        elif (datetime.now() - module.last_sync).total_seconds() > self.sync_interval:
            # Lancer la synchronisation en arrière-plan si les données sont trop anciennes
            threading.Thread(target=self.sync_module, args=(module_id,)).start()
            
        # Retourner les données demandées
        return module.get_data(path)
        
    def start_background_sync(self) -> None:
        """
        Démarre la synchronisation périodique en arrière-plan
        """
        if self.running:
            logger.warning("La synchronisation en arrière-plan est déjà en cours")
            return
            
        self.running = True
        
        def sync_worker():
            """Fonction de synchronisation périodique"""
            while self.running:
                try:
                    self.sync_all_modules()
                except Exception as e:
                    logger.error(f"Erreur lors de la synchronisation périodique: {str(e)}")
                    
                time.sleep(self.sync_interval)
                
        self.sync_thread = threading.Thread(target=sync_worker, daemon=True)
        self.sync_thread.start()
        
        logger.info(f"Synchronisation en arrière-plan démarrée (intervalle: {self.sync_interval}s)")
        
    def stop_background_sync(self) -> None:
        """
        Arrête la synchronisation périodique en arrière-plan
        """
        self.running = False
        if self.sync_thread:
            # Pas besoin de join() car le thread est daemon
            self.sync_thread = None
            
        logger.info("Synchronisation en arrière-plan arrêtée")
        
    def get_module_status(self, module_id: str) -> Dict[str, Any]:
        """
        Récupère le statut d'un module
        
        Args:
            module_id (str): Identifiant du module
            
        Returns:
            dict: Statut du module
        """
        if module_id not in self.modules:
            return {
                'status': 'not_registered',
                'error': 'Module non enregistré'
            }
            
        module = self.modules[module_id]
        
        return {
            'status': module.status,
            'last_sync': module.last_sync.isoformat() if module.last_sync else None,
            'server_url': module.server_url,
            'error_count': module.error_count,
            'data_version': module.data_version
        }
        
    def get_all_modules_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Récupère le statut de tous les modules
        
        Returns:
            dict: Statut de tous les modules
        """
        result = {}
        for module_id in self.modules:
            result[module_id] = self.get_module_status(module_id)
            
        return result
        
    def _hash_data(self, data: Any) -> str:
        """
        Calcule un hash des données pour détecter les changements
        
        Args:
            data (Any): Données à hacher
            
        Returns:
            str: Hash des données
        """
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()
        
    def set_module_priority(self, module_id: str, priority: int) -> bool:
        """
        Définit la priorité d'un module pour la synchronisation adaptative
        
        Args:
            module_id (str): Identifiant du module
            priority (int): Priorité (0-10, 0 étant la plus haute priorité)
            
        Returns:
            bool: True si la priorité a été définie avec succès
        """
        if module_id not in self.modules:
            logger.warning(f"Impossible de définir la priorité: module {module_id} non enregistré")
            return False
            
        # Valider la priorité
        priority = max(0, min(10, priority))  # Limiter entre 0 et 10
        self.module_priorities[module_id] = priority
        logger.info(f"Priorité du module {module_id} définie à {priority}")
        return True
        
    def get_sync_metrics(self) -> Dict[str, Any]:
        """
        Récupère les métriques de synchronisation
        
        Returns:
            dict: Métriques de synchronisation
        """
        # Calculer le taux de réussite
        total_syncs = self.metrics['sync_count']
        success_rate = (self.metrics['success_count'] / total_syncs) if total_syncs > 0 else 0
        
        # Récupérer les métriques spécifiques à chaque module
        module_metrics = {}
        for module_id, module in self.modules.items():
            if module_id in self.metrics['module_metrics']:
                module_data = self.metrics['module_metrics'][module_id]
                total_module_syncs = module_data.get('sync_count', 0)
                module_success_rate = (module_data.get('success_count', 0) / total_module_syncs) if total_module_syncs > 0 else 0
                
                module_metrics[module_id] = {
                    'status': module.status,
                    'last_sync': module.last_sync.isoformat() if module.last_sync else None,
                    'error_count': module.error_count,
                    'sync_count': total_module_syncs,
                    'success_rate': module_success_rate,
                    'priority': self.module_priorities.get(module_id, 5)  # Priorité par défaut
                }
        
        return {
            'overall': {
                'sync_count': self.metrics['sync_count'],
                'success_count': self.metrics['success_count'],
                'error_count': self.metrics['error_count'],
                'success_rate': success_rate,
                'last_reset': self.metrics['last_metrics_reset']
            },
            'modules': module_metrics
        }
        
    def reset_metrics(self) -> None:
        """
        Réinitialise les métriques de synchronisation
        """
        self.metrics = {
            'sync_count': 0,
            'success_count': 0,
            'error_count': 0,
            'last_metrics_reset': datetime.now().isoformat(),
            'module_metrics': {}
        }
        logger.info("Métriques de synchronisation réinitialisées")

# Instance singleton pour l'utilisation dans l'application
context_manager = ContextSyncManager()
