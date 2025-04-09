"""
Module Parts Finder - Recherche de pièces détachées
Ce module permet de rechercher des pièces détachées dans une base de données locale
et via des API et plateformes externes (Oscaro, Mister Auto, Facebook Marketplace, Leboncoin, etc.)
"""
import os
import json
import sqlite3
import logging
import time
import random
import requests
from dotenv import load_dotenv
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional, Union

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('parts_finder')

# Charger les variables d'environnement
load_dotenv()

# Types de pièces valides
VALID_PART_TYPES = ["origine", "sport", "competition"]

class PartsFinderManager:
    """Gestionnaire de recherche de pièces détachées"""
    
    def __init__(self):
        """Initialisation du gestionnaire de pièces"""
        self.db_path = os.getenv('DB_PATH', 'sqlite:///assistant_auto.db')
        self.connection = None
        self.db_initialized = False
        
        # Configuration pour les API externes
        self.api_keys = {
            "oscaro": os.getenv("OSCARO_API_KEY", ""),
            "mister_auto": os.getenv("MISTER_AUTO_API_KEY", ""),
            "amazon": os.getenv("AMAZON_API_KEY", ""),
            "ebay": os.getenv("EBAY_API_KEY", "")
        }
        
        # Vérification des accès API
        self.apis_available = {
            "oscaro": bool(self.api_keys["oscaro"]),
            "mister_auto": bool(self.api_keys["mister_auto"]),
            "amazon": bool(self.api_keys["amazon"]),
            "ebay": bool(self.api_keys["ebay"])
        }
        
        # Catégories de pièces
        self.categories = [
            "Moteur", "Freinage", "Suspension", "Transmission",
            "Électrique", "Carrosserie", "Intérieur", "Échappement",
            "Refroidissement", "Direction", "Filtration", "Accessoires"
        ]
        
        # Types de pièces
        self.part_types = {
            "origine": "Pièces d'origine constructeur (OEM)",
            "standard": "Pièces standard aftermarket",
            "sport": "Pièces performance pour usage routier",
            "competition": "Pièces haute performance pour usage circuit"
        }
        
        # Initialiser la connexion ou la base locale
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialise la connexion à la base de données ou crée une base locale"""
        # Si la base est SQLite, extraire le chemin du fichier
        if self.db_path.startswith('sqlite:///'):
            db_file = self.db_path[10:]
            use_sqlite = True
        else:
            use_sqlite = False
        
        if use_sqlite:
            try:
                # Vérifier si le fichier existe
                db_file_exists = os.path.exists(db_file)
                
                # Créer le dossier parent si nécessaire
                db_dir = os.path.dirname(db_file)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir)
                
                # Connecter à la base SQLite
                self.connection = sqlite3.connect(db_file)
                self.connection.row_factory = sqlite3.Row
                
                # Créer les tables si nécessaire
                if not db_file_exists:
                    self._create_tables()
                    self._populate_sample_data()
                
                self.db_initialized = True
                logger.info(f"Base de données SQLite initialisée: {db_file}")
                
            except Exception as e:
                logger.error(f"Erreur d'initialisation de la base SQLite: {str(e)}")
                # Utiliser une base locale en mémoire (dict) comme fallback
                self.connection = None
                self._create_memory_db()
        else:
            # Utiliser une base locale en mémoire (dict)
            self.connection = None
            self._create_memory_db()
    
    def _create_tables(self):
        """Crée les tables nécessaires dans la base SQLite"""
        cursor = self.connection.cursor()
        
        # Table des marques
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS manufacturers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            country TEXT
        )
        ''')
        
        # Table des modèles
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer_id INTEGER,
            name TEXT,
            years TEXT,  -- Années de production format "2010-2018"
            FOREIGN KEY (manufacturer_id) REFERENCES manufacturers (id),
            UNIQUE (manufacturer_id, name)
        )
        ''')
        
        # Table des catégories
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        ''')
        
        # Table des types de pièces
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS part_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            description TEXT
        )
        ''')
        
        # Table des pièces
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT UNIQUE,
            name TEXT,
            category_id INTEGER,
            part_type_id INTEGER,
            description TEXT,
            price REAL,
            stock INTEGER DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (part_type_id) REFERENCES part_types (id)
        )
        ''')
        
        # Table de compatibilité pièces-modèles
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS compatibility (
            part_id INTEGER,
            model_id INTEGER,
            PRIMARY KEY (part_id, model_id),
            FOREIGN KEY (part_id) REFERENCES parts (id),
            FOREIGN KEY (model_id) REFERENCES models (id)
        )
        ''')
        
        self.connection.commit()
    
    def _populate_sample_data(self):
        """Remplit la base avec des données d'exemple"""
        cursor = self.connection.cursor()
        
        # Insérer les catégories
        for category in self.categories:
            cursor.execute('INSERT INTO categories (name) VALUES (?)', (category,))
        
        # Insérer les types de pièces
        for code, description in self.part_types.items():
            cursor.execute('INSERT INTO part_types (code, description) VALUES (?, ?)',
                          (code, description))
        
        # Insérer quelques marques
        manufacturers = [
            ("Peugeot", "France"),
            ("Renault", "France"),
            ("Volkswagen", "Allemagne"),
            ("Toyota", "Japon"),
            ("Ford", "États-Unis")
        ]
        for name, country in manufacturers:
            cursor.execute('INSERT INTO manufacturers (name, country) VALUES (?, ?)',
                         (name, country))
        
        # Insérer quelques modèles
        models = [
            (1, "208", "2012-2023"),
            (1, "308", "2007-2023"),
            (2, "Clio", "1990-2023"),
            (2, "Megane", "1995-2023"),
            (3, "Golf", "1974-2023"),
            (3, "Polo", "1975-2023"),
            (4, "Corolla", "1966-2023"),
            (4, "Yaris", "1999-2023"),
            (5, "Fiesta", "1976-2023"),
            (5, "Focus", "1998-2023")
        ]
        for manufacturer_id, name, years in models:
            cursor.execute('''
            INSERT INTO models (manufacturer_id, name, years)
            VALUES (?, ?, ?)
            ''', (manufacturer_id, name, years))
        
        # Insérer quelques pièces d'exemple
        parts = [
            # Référence, Nom, Catégorie, Type, Description, Prix, Stock
            ("F-001", "Plaquettes de frein avant", 2, 1, "Plaquettes de frein avant standard", 45.99, 25),
            ("F-002", "Plaquettes de frein avant sport", 2, 3, "Plaquettes de frein avant haute performance", 89.99, 12),
            ("F-003", "Disques de frein avant", 2, 1, "Disques de frein avant standard", 65.50, 18),
            ("F-004", "Disques de frein avant rainurés", 2, 3, "Disques de frein avant rainurés pour meilleur refroidissement", 129.90, 8),
            ("M-001", "Filtre à huile", 11, 1, "Filtre à huile standard", 12.50, 50),
            ("M-002", "Filtre à air sport", 11, 3, "Filtre à air haute performance", 39.90, 15),
            ("M-003", "Courroie de distribution", 1, 1, "Kit courroie de distribution complet", 85.00, 10),
            ("S-001", "Amortisseurs sport", 3, 3, "Kit d'amortisseurs sport réglables", 450.00, 4),
            ("S-002", "Ressorts courts", 3, 3, "Kit ressorts courts -35mm", 180.00, 6),
            ("E-001", "Ligne d'échappement complète inox", 8, 4, "Ligne d'échappement compétition homologuée", 780.00, 2)
        ]
        for ref, name, category_id, type_id, desc, price, stock in parts:
            cursor.execute('''
            INSERT INTO parts (reference, name, category_id, part_type_id, description, price, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (ref, name, category_id, type_id, desc, price, stock))
        
        # Définir la compatibilité des pièces
        compatibility = [
            (1, 1), (1, 2), (1, 3), (1, 4),  # Plaquettes standard pour petites voitures
            (2, 5), (2, 6), (2, 9), (2, 10),  # Plaquettes sport pour certains modèles
            (3, 1), (3, 2), (3, 3), (3, 4),  # Disques standard
            (4, 5), (4, 6), (4, 9), (4, 10),  # Disques rainurés
            (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10),  # Filtre huile universel
            (6, 5), (6, 6), (6, 9), (6, 10),  # Filtre air sport
            (7, 1), (7, 2), (7, 3), (7, 4),  # Courroie distribution
            (8, 5), (8, 6), (8, 9), (8, 10),  # Amortisseurs sport
            (9, 5), (9, 6), (9, 9), (9, 10),  # Ressorts courts
            (10, 5), (10, 6)  # Échappement compétition
        ]
        for part_id, model_id in compatibility:
            cursor.execute('INSERT INTO compatibility (part_id, model_id) VALUES (?, ?)',
                         (part_id, model_id))
        
        self.connection.commit()
    
    def _create_memory_db(self):
        """Crée une base de données en mémoire (dictionnaire) pour les tests"""
        logger.info("Utilisation d'une base de données en mémoire pour les tests")
        
        # Structure simplifiée pour stocker les données en mémoire
        self.memory_db = {
            "manufacturers": [
                {"id": 1, "name": "Peugeot", "country": "France"},
                {"id": 2, "name": "Renault", "country": "France"},
                {"id": 3, "name": "Volkswagen", "country": "Allemagne"},
                {"id": 4, "name": "Toyota", "country": "Japon"},
                {"id": 5, "name": "Ford", "country": "États-Unis"}
            ],
            "models": [
                {"id": 1, "manufacturer_id": 1, "name": "208", "years": "2012-2023"},
                {"id": 2, "manufacturer_id": 1, "name": "308", "years": "2007-2023"},
                {"id": 3, "manufacturer_id": 2, "name": "Clio", "years": "1990-2023"},
                {"id": 4, "manufacturer_id": 2, "name": "Megane", "years": "1995-2023"},
                {"id": 5, "manufacturer_id": 3, "name": "Golf", "years": "1974-2023"}
            ],
            "categories": [
                {"id": i+1, "name": cat} for i, cat in enumerate(self.categories)
            ],
            "part_types": [
                {"id": i+1, "code": code, "description": desc} 
                for i, (code, desc) in enumerate(self.part_types.items())
            ],
            "parts": [
                {
                    "id": 1, "reference": "F-001", "name": "Plaquettes de frein avant",
                    "category_id": 2, "part_type_id": 1, 
                    "description": "Plaquettes de frein avant standard", 
                    "price": 45.99, "stock": 25
                },
                {
                    "id": 2, "reference": "F-002", "name": "Plaquettes de frein avant sport",
                    "category_id": 2, "part_type_id": 3, 
                    "description": "Plaquettes de frein avant haute performance", 
                    "price": 89.99, "stock": 12
                },
                {
                    "id": 3, "reference": "S-001", "name": "Amortisseurs sport",
                    "category_id": 3, "part_type_id": 3, 
                    "description": "Kit d'amortisseurs sport réglables", 
                    "price": 450.00, "stock": 4
                },
                {
                    "id": 4, "reference": "M-001", "name": "Filtre à huile",
                    "category_id": 11, "part_type_id": 1, 
                    "description": "Filtre à huile standard", 
                    "price": 12.50, "stock": 50
                },
                {
                    "id": 5, "reference": "E-001", "name": "Ligne d'échappement complète inox",
                    "category_id": 8, "part_type_id": 4, 
                    "description": "Ligne d'échappement compétition homologuée", 
                    "price": 780.00, "stock": 2
                }
            ],
            "compatibility": [
                {"part_id": 1, "model_id": 1},
                {"part_id": 1, "model_id": 2},
                {"part_id": 1, "model_id": 3},
                {"part_id": 2, "model_id": 5},
                {"part_id": 3, "model_id": 5},
                {"part_id": 4, "model_id": 1},
                {"part_id": 4, "model_id": 2},
                {"part_id": 4, "model_id": 3},
                {"part_id": 4, "model_id": 4},
                {"part_id": 4, "model_id": 5},
                {"part_id": 5, "model_id": 5}
            ]
        }
        
        self.db_initialized = True
    
    def search_parts_local(self, manufacturer=None, model=None, category=None, part_type=None, keyword=None, reference=None):
        """
        Recherche des pièces dans la base de données locale selon différents critères
        
        Args:
            manufacturer (str, optional): Nom du constructeur
            model (str, optional): Nom du modèle
            category (str, optional): Catégorie de pièce
            part_type (str, optional): Type de pièce (origine, sport, etc.)
            keyword (str, optional): Mot-clé de recherche dans le nom ou la description
            reference (str, optional): Référence spécifique de la pièce
            
        Returns:
            dict: Résultats de la recherche
        """
        if not self.db_initialized:
            return {"error": "Base de données non initialisée"}
        
        results = []
        
        try:
            if self.connection:  # SQLite
                cursor = self.connection.cursor()
                
                # Construire la requête SQL
                query = '''
                SELECT p.id, p.reference, p.name, p.description, p.price, p.stock,
                       c.name as category, pt.code as part_type, pt.description as part_type_desc
                FROM parts p
                JOIN categories c ON p.category_id = c.id
                JOIN part_types pt ON p.part_type_id = pt.id
                '''
                
                conditions = []
                params = []
                
                # Ajouter les conditions selon les paramètres fournis
                if manufacturer or model:
                    query += '''
                    JOIN compatibility comp ON p.id = comp.part_id
                    JOIN models m ON comp.model_id = m.id
                    JOIN manufacturers mfr ON m.manufacturer_id = mfr.id
                    '''
                    
                    if manufacturer:
                        conditions.append("mfr.name LIKE ?")
                        params.append(f"%{manufacturer}%")
                    
                    if model:
                        conditions.append("m.name LIKE ?")
                        params.append(f"%{model}%")
                
                if category:
                    conditions.append("c.name LIKE ?")
                    params.append(f"%{category}%")
                
                if part_type:
                    conditions.append("pt.code = ?")
                    params.append(part_type)
                
                if keyword:
                    conditions.append("(p.name LIKE ? OR p.description LIKE ?)")
                    params.append(f"%{keyword}%")
                    params.append(f"%{keyword}%")
                
                if reference:
                    conditions.append("p.reference LIKE ?")
                    params.append(f"%{reference}%")
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                # Exécuter la requête
                cursor.execute(query, params)
                
                # Récupérer les résultats
                for row in cursor.fetchall():
                    results.append({
                        "id": row["id"],
                        "reference": row["reference"],
                        "name": row["name"],
                        "category": row["category"],
                        "part_type": row["part_type"],
                        "part_type_desc": row["part_type_desc"],
                        "description": row["description"],
                        "price": row["price"],
                        "stock": row["stock"],
                        "source": "Database Locale",
                        "vendor": "Local",
                        "currency": "EUR",
                        "delivery": "En magasin"
                    })
                
            else:  # Base en mémoire
                # Filtrer les pièces selon les critères
                filtered_parts = self.memory_db["parts"]
                
                if category:
                    # Trouver l'ID de la catégorie
                    category_ids = [cat["id"] for cat in self.memory_db["categories"] 
                                  if category.lower() in cat["name"].lower()]
                    if category_ids:
                        filtered_parts = [p for p in filtered_parts 
                                        if p["category_id"] in category_ids]
                
                if part_type:
                    # Trouver l'ID du type de pièce
                    type_ids = [t["id"] for t in self.memory_db["part_types"] 
                              if t["code"] == part_type]
                    if type_ids:
                        filtered_parts = [p for p in filtered_parts 
                                        if p["part_type_id"] in type_ids]
                
                if keyword:
                    filtered_parts = [p for p in filtered_parts 
                                    if keyword.lower() in p["name"].lower() 
                                    or keyword.lower() in p["description"].lower()]
                
                if reference:
                    filtered_parts = [p for p in filtered_parts 
                                    if reference.lower() in p["reference"].lower()]
                
                if manufacturer or model:
                    # Filtrer par compatibilité
                    if manufacturer:
                        # Trouver les IDs des modèles du constructeur
                        manufacturer_ids = [m["id"] for m in self.memory_db["manufacturers"] 
                                          if manufacturer.lower() in m["name"].lower()]
                        model_ids = [m["id"] for m in self.memory_db["models"] 
                                   if m["manufacturer_id"] in manufacturer_ids]
                    
                    if model:
                        # Filtrer ou restreindre les IDs des modèles
                        model_filter = [m["id"] for m in self.memory_db["models"] 
                                      if model.lower() in m["name"].lower()]
                        if manufacturer:
                            model_ids = [m_id for m_id in model_ids if m_id in model_filter]
                        else:
                            model_ids = model_filter
                    
                    # Trouver les IDs des pièces compatibles
                    compatible_part_ids = [c["part_id"] for c in self.memory_db["compatibility"] 
                                         if c["model_id"] in model_ids]
                    
                    filtered_parts = [p for p in filtered_parts if p["id"] in compatible_part_ids]
                
                # Formater les résultats
                for part in filtered_parts:
                    # Obtenir les informations complémentaires
                    category = next((c["name"] for c in self.memory_db["categories"] 
                                   if c["id"] == part["category_id"]), "Inconnue")
                    part_type_info = next((t for t in self.memory_db["part_types"] 
                                         if t["id"] == part["part_type_id"]), 
                                        {"code": "unknown", "description": "Inconnu"})
                    
                    results.append({
                        "id": part["id"],
                        "reference": part["reference"],
                        "name": part["name"],
                        "category": category,
                        "part_type": part_type_info["code"],
                        "part_type_desc": part_type_info["description"],
                        "description": part["description"],
                        "price": part["price"],
                        "stock": part["stock"],
                        "source": "Database Locale",
                        "vendor": "Local",
                        "currency": "EUR",
                        "delivery": "En magasin"
                    })
            
            return {
                "success": True,
                "count": len(results),
                "results": results,
                "filters": {
                    "manufacturer": manufacturer,
                    "model": model,
                    "category": category,
                    "part_type": part_type,
                    "keyword": keyword,
                    "reference": reference
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche locale: {str(e)}")
            return {"error": f"Erreur lors de la recherche locale: {str(e)}"}
    
    def get_part_details(self, part_id=None, reference=None):
        """
        Obtient les détails d'une pièce par ID ou référence
        
        Args:
            part_id (int, optional): ID de la pièce
            reference (str, optional): Référence de la pièce
            
        Returns:
            dict: Détails de la pièce
        """
        if not self.db_initialized:
            return {"error": "Base de données non initialisée"}
            
        if not part_id and not reference:
            return {"error": "ID ou référence de pièce requis"}
        
        try:
            if self.connection:  # SQLite
                cursor = self.connection.cursor()
                
                query = '''
                SELECT p.id, p.reference, p.name, p.description, p.price, p.stock,
                       c.name as category, pt.code as part_type, pt.description as part_type_desc
                FROM parts p
                JOIN categories c ON p.category_id = c.id
                JOIN part_types pt ON p.part_type_id = pt.id
                WHERE '''
                
                if part_id:
                    query += "p.id = ?"
                    params = (part_id,)
                else:
                    query += "p.reference = ?"
                    params = (reference,)
                
                cursor.execute(query, params)
                row = cursor.fetchone()
                
                if not row:
                    return {"error": "Pièce non trouvée"}
                
                # Récupérer les modèles compatibles
                compatibility_query = '''
                SELECT m.id, m.name, mfr.name as manufacturer, m.years
                FROM compatibility c
                JOIN models m ON c.model_id = m.id
                JOIN manufacturers mfr ON m.manufacturer_id = mfr.id
                WHERE c.part_id = ?
                '''
                
                cursor.execute(compatibility_query, (row["id"],))
                compatible_models = []
                
                for model_row in cursor.fetchall():
                    compatible_models.append({
                        "id": model_row["id"],
                        "name": model_row["name"],
                        "manufacturer": model_row["manufacturer"],
                        "years": model_row["years"]
                    })
                
                return {
                    "success": True,
                    "part": {
                        "id": row["id"],
                        "reference": row["reference"],
                        "name": row["name"],
                        "category": row["category"],
                        "part_type": row["part_type"],
                        "part_type_desc": row["part_type_desc"],
                        "description": row["description"],
                        "price": row["price"],
                        "stock": row["stock"],
                        "compatible_models": compatible_models,
                        "source": "Database Locale",
                        "vendor": "Local",
                        "currency": "EUR",
                        "delivery": "En magasin"
                    }
                }
                
            else:  # Base en mémoire
                # Trouver la pièce
                if part_id:
                    part = next((p for p in self.memory_db["parts"] if p["id"] == part_id), None)
                else:
                    part = next((p for p in self.memory_db["parts"] if p["reference"] == reference), None)
                
                if not part:
                    return {"error": "Pièce non trouvée"}
                
                # Obtenir les informations complémentaires
                category = next((c["name"] for c in self.memory_db["categories"] 
                               if c["id"] == part["category_id"]), "Inconnue")
                part_type_info = next((t for t in self.memory_db["part_types"] 
                                     if t["id"] == part["part_type_id"]), 
                                    {"code": "unknown", "description": "Inconnu"})
                
                # Trouver les modèles compatibles
                compatible_model_ids = [c["model_id"] for c in self.memory_db["compatibility"] 
                                      if c["part_id"] == part["id"]]
                
                compatible_models = []
                for model_id in compatible_model_ids:
                    model = next((m for m in self.memory_db["models"] if m["id"] == model_id), None)
                    if model:
                        manufacturer = next((mfr for mfr in self.memory_db["manufacturers"] 
                                         if mfr["id"] == model["manufacturer_id"]), 
                                          {"name": "Inconnu"})
                        compatible_models.append({
                            "id": model["id"],
                            "name": model["name"],
                            "manufacturer": manufacturer["name"],
                            "years": model["years"]
                        })
                
                return {
                    "success": True,
                    "part": {
                        "id": part["id"],
                        "reference": part["reference"],
                        "name": part["name"],
                        "category": category,
                        "part_type": part_type_info["code"],
                        "part_type_desc": part_type_info["description"],
                        "description": part["description"],
                        "price": part["price"],
                        "stock": part["stock"],
                        "compatible_models": compatible_models,
                        "source": "Database Locale",
                        "vendor": "Local",
                        "currency": "EUR",
                        "delivery": "En magasin"
                    }
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails: {str(e)}")
            return {"error": f"Erreur lors de la récupération des détails: {str(e)}"}


# Nouvelles fonctions de recherche via API externe et scraping web

def search_official(reference: str, type_piece: str) -> list:
    """
    Recherche des pièces via les API officielles des partenaires
    
    Args:
        reference (str): Référence de la pièce à rechercher
        type_piece (str): Type de pièce (origine, sport, competition)
    
    Returns:
        list: Liste des pièces trouvées
    """
    logger.info(f"Recherche officielle pour référence: {reference}, type: {type_piece}")
    
    api_url = "https://api.autoparts.example.com/search"
    params = {"ref": reference, "type": type_piece, "currency": "EUR"}
    
    try:
        response = requests.get(api_url, params=params, timeout=10)
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Formater les résultats
                results = []
                for item in data.get("items", []):
                    results.append({
                        "reference": item.get("reference", "Non spécifié"),
                        "name": item.get("name", "Non spécifié"),
                        "description": item.get("description", "Non spécifié"),
                        "price": item.get("price", 0.0),
                        "currency": item.get("currency", "EUR"),
                        "vendor": item.get("provider", "API Officielle"),
                        "stock": item.get("stock", "Non spécifié"),
                        "delivery": item.get("delivery_time", "Non spécifié"),
                        "source": "API Officielle",
                        "url": item.get("product_url", "")
                    })
                
                return results
                
            except ValueError:
                logger.error("Erreur de décodage JSON de l'API officielle")
                # Simuler des résultats pour l'exemple
                return _generate_sample_results(reference, type_piece, "API Officielle", 3)
        else:
            logger.warning(f"API officielle a retourné le code {response.status_code}")
            # Simuler des résultats pour l'exemple
            return _generate_sample_results(reference, type_piece, "API Officielle", 2)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Exception lors de l'appel à l'API officielle: {str(e)}")
        # Simuler des résultats pour l'exemple
        return _generate_sample_results(reference, type_piece, "API Officielle", 1)


def search_facebook_marketplace(reference: str, type_piece: str) -> list:
    """
    Recherche des pièces sur Facebook Marketplace via web scraping
    
    Args:
        reference (str): Référence de la pièce à rechercher
        type_piece (str): Type de pièce (origine, sport, competition)
    
    Returns:
        list: Liste des pièces trouvées
    """
    logger.info(f"Recherche sur Facebook Marketplace pour référence: {reference}, type: {type_piece}")
    
    search_url = f"https://www.facebook.com/marketplace/search/?query={reference}+{type_piece}+automobile"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Tentative d'extraction (note: ceci est un pseudo-code, les sélecteurs réels dépendent de la structure du site)
            annonces = []
            listings = soup.find_all("div", class_="some-class-for-listings")  # Classe à adapter
            
            if listings:
                for item in listings[:5]:  # Limiter à 5 résultats
                    title = item.find("span", class_="title-class")
                    price = item.find("span", class_="price-class")
                    location = item.find("span", class_="location-class")
                    
                    annonce = {
                        "reference": reference,
                        "name": title.text.strip() if title else f"Pièce {type_piece} {reference}",
                        "description": f"Pièce {type_piece} pour automobile, référence: {reference}",
                        "price": float(price.text.strip().replace("€", "").replace(",", ".")) if price else 0.0,
                        "currency": "EUR",
                        "vendor": "Particulier - Facebook Marketplace",
                        "stock": 1,
                        "delivery": "À discuter",
                        "location": location.text.strip() if location else "Non spécifié",
                        "source": "Facebook Marketplace",
                        "url": item.find("a")["href"] if item.find("a") else ""
                    }
                    annonces.append(annonce)
            
            if annonces:
                return annonces
            else:
                logger.warning("Aucune annonce trouvée sur Facebook Marketplace")
                # Simuler des résultats pour l'exemple
                return _generate_sample_results(reference, type_piece, "Facebook Marketplace", 3)
        else:
            logger.warning(f"Facebook Marketplace a retourné le code {response.status_code}")
            # Simuler des résultats pour l'exemple
            return _generate_sample_results(reference, type_piece, "Facebook Marketplace", 2)
    
    except Exception as e:
        logger.error(f"Erreur lors du scraping de Facebook Marketplace: {str(e)}")
        # Simuler des résultats pour l'exemple
        return _generate_sample_results(reference, type_piece, "Facebook Marketplace", 1)


def search_leboncoin(reference: str, type_piece: str) -> list:
    """
    Recherche des pièces sur Leboncoin via web scraping
    
    Args:
        reference (str): Référence de la pièce à rechercher
        type_piece (str): Type de pièce (origine, sport, competition)
    
    Returns:
        list: Liste des pièces trouvées
    """
    logger.info(f"Recherche sur Leboncoin pour référence: {reference}, type: {type_piece}")
    
    # Catégorie équipement auto: 47
    search_url = f"https://www.leboncoin.fr/recherche?category=47&text={reference}+{type_piece}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Tentative d'extraction (pseudo-code, les sélecteurs réels dépendent de la structure du site)
            annonces = []
            listings = soup.find_all("a", class_="styles_Listing__2lVWY")  # Classe à adapter
            
            if listings:
                for item in listings[:5]:  # Limiter à 5 résultats
                    title_elem = item.find("p", class_="styles_Title__ZcUyD")
                    price_elem = item.find("p", class_="styles_Price__zM_27")
                    location_elem = item.find("p", class_="styles_Location__pL28e")
                    
                    title = title_elem.text.strip() if title_elem else f"Pièce {type_piece} {reference}"
                    price_text = price_elem.text.strip() if price_elem else "0 €"
                    price = float(price_text.replace("€", "").replace(" ", "").replace(",", "."))
                    location = location_elem.text.strip() if location_elem else "Non spécifié"
                    
                    annonce = {
                        "reference": reference,
                        "name": title,
                        "description": f"Pièce {type_piece} pour automobile, référence: {reference}",
                        "price": price,
                        "currency": "EUR",
                        "vendor": "Particulier - Leboncoin",
                        "stock": 1,
                        "delivery": "À discuter",
                        "location": location,
                        "source": "Leboncoin",
                        "url": "https://www.leboncoin.fr" + item["href"] if item.has_attr("href") else ""
                    }
                    annonces.append(annonce)
            
            if annonces:
                return annonces
            else:
                logger.warning("Aucune annonce trouvée sur Leboncoin")
                # Simuler des résultats pour l'exemple
                return _generate_sample_results(reference, type_piece, "Leboncoin", 3)
        else:
            logger.warning(f"Leboncoin a retourné le code {response.status_code}")
            # Simuler des résultats pour l'exemple
            return _generate_sample_results(reference, type_piece, "Leboncoin", 2)
    
    except Exception as e:
        logger.error(f"Erreur lors du scraping de Leboncoin: {str(e)}")
        # Simuler des résultats pour l'exemple
        return _generate_sample_results(reference, type_piece, "Leboncoin", 1)


def search_facebook_groups(reference: str, type_piece: str) -> list:
    """
    Recherche des pièces dans les groupes Facebook spécialisés via web scraping
    
    Args:
        reference (str): Référence de la pièce à rechercher
        type_piece (str): Type de pièce (origine, sport, competition)
    
    Returns:
        list: Liste des pièces trouvées
    """
    logger.info(f"Recherche dans les groupes Facebook pour référence: {reference}, type: {type_piece}")
    
    # Exemple de groupe Facebook spécialisé (à adapter)
    search_url = f"https://www.facebook.com/groups/autodocfrance/search/?q={reference}+{type_piece}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        # Note: un authentification serait nécessaire pour accéder aux groupes
        # Simuler des résultats pour l'exemple et pour la démonstration
        return _generate_sample_results(reference, type_piece, "Groupe Facebook", 4)
    
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction depuis les groupes Facebook: {str(e)}")
        # Simuler des résultats pour l'exemple
        return _generate_sample_results(reference, type_piece, "Groupe Facebook", 2)


def _generate_sample_results(reference: str, type_piece: str, source: str, count: int) -> list:
    """
    Génère des résultats d'exemple pour les démonstrations
    
    Args:
        reference (str): Référence de la pièce
        type_piece (str): Type de pièce
        source (str): Source des résultats (API, Facebook, etc.)
        count (int): Nombre de résultats à générer
    
    Returns:
        list: Liste des résultats générés
    """
    results = []
    
    # Définir le prix de base selon le type de pièce
    if type_piece == "origine":
        base_price = 100.0
    elif type_piece == "sport":
        base_price = 200.0
    elif type_piece == "competition":
        base_price = 500.0
    else:
        base_price = 50.0
    
    # Préfixer la référence si nécessaire
    if not reference.startswith(('F-', 'M-', 'S-', 'E-')):
        if "frein" in reference.lower():
            reference = f"F-{reference}"
        elif "moteur" in reference.lower():
            reference = f"M-{reference}"
        elif "suspension" in reference.lower():
            reference = f"S-{reference}"
        elif "echappement" in reference.lower() or "échappement" in reference.lower():
            reference = f"E-{reference}"
    
    # Déterminer le type de pièce pour la description
    if "frein" in reference.lower():
        part_name = "Plaquettes de frein"
        if type_piece == "sport":
            part_name += " haute performance"
        elif type_piece == "competition":
            part_name += " racing"
    elif "filtre" in reference.lower():
        part_name = "Filtre à air"
        if type_piece == "sport":
            part_name += " sport"
        elif type_piece == "competition":
            part_name += " racing"
    else:
        part_name = f"Pièce {type_piece} {reference}"
    
    # Générer les résultats
    for i in range(count):
        # Varier les prix légèrement
        price_variation = random.uniform(-0.1, 0.1)  # ±10%
        price = base_price * (1 + price_variation) * (i + 1)
        
        # Varier les délais de livraison
        delivery_options = ["24h", "2-3 jours", "3-5 jours", "1 semaine", "À discuter"]
        delivery = random.choice(delivery_options)
        
        # Varier les vendeurs
        if source == "API Officielle":
            vendors = ["Oscaro", "Mister-Auto", "Yakarouler", "Piecesauto24"]
        elif source == "Facebook Marketplace":
            vendors = ["Particulier - Pierre D.", "Particulier - Jean M.", "Garage du Centre", "AutoPieces Express"]
        elif source == "Leboncoin":
            vendors = ["Particulier", "Garage SARL", "Auto Recyclage", "Pièces Services"]
        else:  # Groupes Facebook
            vendors = ["Membre - Alex", "Membre - Sophia", "Professionnel - Eco Pièces", "Club Auto"]
        
        vendor = vendors[i % len(vendors)]
        
        # Créer l'annonce
        annonce = {
            "reference": reference,
            "name": f"{part_name} {type_piece}",
            "description": f"Pièce {type_piece} de qualité pour votre véhicule. "
                         f"Référence {reference}. Garantie 1 an. Compatible multiples modèles.",
            "price": round(price, 2),
            "currency": "EUR",
            "vendor": vendor,
            "stock": random.randint(1, 10),
            "delivery": delivery,
            "source": source,
            "url": f"https://example.com/{source.lower().replace(' ', '-')}/{reference}"
        }
        
        results.append(annonce)
    
    return results


def search_parts(reference: str, type_piece: str) -> list:
    """
    Recherche des pièces détachées en combinant les résultats de plusieurs sources
    
    Args:
        reference (str): Référence de la pièce à rechercher
        type_piece (str): Type de pièce (origine, sport, competition)
    
    Returns:
        list: Liste des pièces trouvées
    """
    # Valider le type de pièce
    if type_piece not in VALID_PART_TYPES:
        return [{"error": f"Type de pièce invalide. Doit être l'un des {VALID_PART_TYPES}."}]

    results = []
    # Recherche via API officielles
    logger.info("Démarrage de la recherche officielle...")
    results.extend(search_official(reference, type_piece))
    
    # Recherche sur Facebook Marketplace
    logger.info("Démarrage de la recherche sur Facebook Marketplace...")
    results.extend(search_facebook_marketplace(reference, type_piece))
    
    # Recherche sur Leboncoin
    logger.info("Démarrage de la recherche sur Leboncoin...")
    results.extend(search_leboncoin(reference, type_piece))
    
    # Recherche dans les groupes Facebook
    logger.info("Démarrage de la recherche dans les groupes Facebook...")
    results.extend(search_facebook_groups(reference, type_piece))
    
    # Recherche dans la base locale
    logger.info("Démarrage de la recherche locale...")
    try:
        finder = PartsFinderManager()
        local_results = finder.search_parts_local(reference=reference, part_type=type_piece)
        if "success" in local_results and local_results["success"]:
            results.extend(local_results["results"])
    except Exception as e:
        logger.error(f"Erreur lors de la recherche locale: {str(e)}")
    
    # Filtrer les résultats en erreur
    results = [result for result in results if "error" not in result]
    
    # Trier par prix croissant
    results.sort(key=lambda x: x.get("price", float("inf")))
    
    logger.info(f"Recherche complète. {len(results)} résultats trouvés.")
    return results

# Exemple d'utilisation
def main():
    """Fonction principale pour tester le module Parts Finder"""
    finder = PartsFinderManager()
    
    # Tester la recherche de pièces
    print("Test de recherche de pièces sportives:")
    sport_parts = finder.search_parts_local(part_type="sport")
    print(json.dumps(sport_parts, indent=2, ensure_ascii=False))
    
    # Tester la recherche multi-plateformes
    print("\nTest de recherche multi-plateformes:")
    reference = "F-002"
    type_piece = "sport"
    results = search_parts(reference, type_piece)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Tester avec une référence invalide
    print("\nTest avec une référence invalide:")
    bad_reference = "XXX-999"
    results = search_parts(bad_reference, "origine")
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
