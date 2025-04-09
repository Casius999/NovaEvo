"""
Module Parts Finder - Recherche de pièces détachées
Ce module permet de rechercher des pièces détachées dans une base de données locale
"""
import os
import json
import sqlite3
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement
load_dotenv()

class PartsFinderManager:
    """Gestionnaire de recherche de pièces détachées"""
    
    def __init__(self):
        """Initialisation du gestionnaire de pièces"""
        self.db_path = os.getenv('DB_PATH', 'sqlite:///assistant_auto.db')
        self.connection = None
        self.db_initialized = False
        
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
                print(f"Base de données SQLite initialisée: {db_file}")
                
            except Exception as e:
                print(f"Erreur d'initialisation de la base SQLite: {str(e)}")
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
        print("Utilisation d'une base de données en mémoire pour les tests")
        
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
    
    def search_parts(self, manufacturer=None, model=None, category=None, part_type=None, keyword=None):
        """
        Recherche des pièces selon différents critères
        
        Args:
            manufacturer (str, optional): Nom du constructeur
            model (str, optional): Nom du modèle
            category (str, optional): Catégorie de pièce
            part_type (str, optional): Type de pièce (origine, sport, etc.)
            keyword (str, optional): Mot-clé de recherche dans le nom ou la description
            
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
                        "stock": row["stock"]
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
                        "stock": part["stock"]
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
                    "keyword": keyword
                }
            }
            
        except Exception as e:
            return {"error": f"Erreur lors de la recherche: {str(e)}"}
    
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
                        "compatible_models": compatible_models
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
                        "compatible_models": compatible_models
                    }
                }
                
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des détails: {str(e)}"}

# Exemple d'utilisation
def main():
    """Fonction principale pour tester le module Parts Finder"""
    finder = PartsFinderManager()
    
    # Tester la recherche de pièces
    print("Test de recherche de pièces sportives:")
    sport_parts = finder.search_parts(part_type="sport")
    print(json.dumps(sport_parts, indent=2, ensure_ascii=False))
    
    # Tester la recherche par catégorie
    print("\nTest de recherche de pièces de freinage:")
    brake_parts = finder.search_parts(category="Frein")
    print(json.dumps(brake_parts, indent=2, ensure_ascii=False))
    
    # Tester la recherche par modèle
    print("\nTest de recherche pour Golf:")
    golf_parts = finder.search_parts(model="Golf")
    print(json.dumps(golf_parts, indent=2, ensure_ascii=False))
    
    # Tester l'obtention des détails d'une pièce
    if sport_parts["success"] and sport_parts["count"] > 0:
        part_id = sport_parts["results"][0]["id"]
        print(f"\nTest de récupération des détails de la pièce ID={part_id}:")
        part_details = finder.get_part_details(part_id=part_id)
        print(json.dumps(part_details, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
