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
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta

# Configuration du logger
logger = logging.getLogger('novaevo.context_sync')

class ContextModule:
    """
    Représentation d'un module contextuel externe
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
        
    def sync(self, force: bool = False) -> bool:
        """
        Synchronise les données avec le serveur
        
        Args:
            force (bool): Forcer la synchronisation même si une version récente est disponible
            
        Returns:
            bool: True si la synchronisation a réussi, False sinon
        """
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f"Bearer {self.api_key}"
                
            # Ajouter l'en-tête If-None-Match si nous avons une version
            if self.data_version and not force:
                headers['If-None-Match'] = self.data_version
                
            # Récupérer les données du serveur
            response = requests.get(
                f"{self.server_url}/api/data",
                headers=headers,
                timeout=30
            )
            
            # Traiter la réponse selon le code
            if response.status_code == 200:
                self.data = response.json()
                self.last_sync = datetime.now()
                self.status = 'active'
                self.error_count = 0
                
                # Stocker la version des données
                if 'ETag' in response.headers:
                    self.data_version = response.headers['ETag']
                    
                # Sauvegarder les données en cache
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
                
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation du module {self.id}: {str(e)}")
            self.error_count += 1
            
            if self.error_count >= self.max_errors:
                self.status = 'error'
                
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
        Sauvegarde les données dans un fichier cache
        """
        try:
            cache_dir = os.path.join('data', 'cache', 'context')
            os.makedirs(cache_dir, exist_ok=True)
            
            cache_file = os.path.join(cache_dir, f"{self.id}.json")
            
            cache_data = {
                'data': self.data,
                'version': self.data_version,
                'timestamp': datetime.now().isoformat(),
                'server_url': self.server_url
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
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
                
            self.data = cache_data['data']
            self.data_version = cache_data.get('version')
            self.last_sync = timestamp
            
            logger.info(f"Données chargées depuis le cache pour {self.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du cache pour {self.id}: {str(e)}")
            return False


class ContextSyncManager:
    """
    Gestionnaire de synchronisation des modules contextuels
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
            
        # Récupérer l'ancien état pour comparaison
        old_data_hash = self._hash_data(self.modules[module_id].data)
        
        # Synchroniser le module
        result = self.modules[module_id].sync(force)
        
        if result:
            # Vérifier si les données ont changé
            new_data_hash = self._hash_data(self.modules[module_id].data)
            
            if old_data_hash != new_data_hash:
                logger.info(f"Données modifiées pour le module {module_id}")
                
                # Notifier les listeners
                for listener in self.listeners:
                    try:
                        listener(module_id, self.modules[module_id].data)
                    except Exception as e:
                        logger.error(f"Erreur lors de la notification d'un listener: {str(e)}")
        
        return result
        
    def sync_all_modules(self) -> Dict[str, bool]:
        """
        Synchronise tous les modules enregistrés
        
        Returns:
            dict: Résultats de synchronisation par module
        """
        results = {}
        for module_id in self.modules:
            results[module_id] = self.sync_module(module_id)
            
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

# Instance singleton pour l'utilisation dans l'application
context_manager = ContextSyncManager()
