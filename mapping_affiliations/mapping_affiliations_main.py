"""
Module d'affiliation pour la vente de cartographies clé en main

Ce module interroge des API partenaires et/ou effectue du scraping sur des plateformes telles que 
Facebook Marketplace, Leboncoin et des groupes Facebook spécialisés, afin d'afficher des offres affiliées.
"""
import os
import requests
import json
import random
import time
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote_plus

# Configuration
API_KEY = os.getenv("MAPPING_API_KEY", "demo_key_123456")
API_URL = os.getenv("MAPPING_API_URL", "https://api.tuners.example.com/mappings")

# Catégories valides
VALID_CATEGORIES = ["origine", "sport", "competition", None]

def search_official_mapping(query: str, category: str = None) -> list:
    """
    Recherche des cartographies via l'API des partenaires officiels
    
    Args:
        query: Terme de recherche (ex: "cartographie bmw 320d e90")
        category: Catégorie de cartographie (origine, sport, competition)
        
    Returns:
        list: Liste des cartographies trouvées
    """
    # Validation des paramètres
    if category and category not in VALID_CATEGORIES:
        return [{"error": f"Catégorie invalide. Catégories valides: {', '.join(filter(None, VALID_CATEGORIES))}"}]
    
    # Construction de la requête API
    params = {
        "query": query,
        "api_key": API_KEY,
        "currency": "EUR"
    }
    
    if category:
        params["category"] = category
    
    # Faire la requête à l'API partenaire
    try:
        # En mode démonstration, on simule une réponse API
        if API_KEY == "demo_key_123456":
            return get_demo_data(query, category, "official")
        
        # Si on a une vraie clé API
        response = requests.get(API_URL, params=params, timeout=15)
        
        if response.status_code == 200:
            # Traiter et standardiser la réponse
            data = response.json()
            
            # Standardiser le format pour l'intégration
            standardized_results = []
            for item in data.get("results", []):
                standardized_results.append({
                    "preparateur": item.get("tuner_name", "Non spécifié"),
                    "description": item.get("description", ""),
                    "price": f"{item.get('price', 0):.2f}€",
                    "affiliate_link": item.get("affiliate_url", "#"),
                    "category": item.get("category", category or "Non spécifié"),
                    "source": "API Partenaire Officiel",
                    "rating": item.get("rating", None),
                    "discount": item.get("discount", None),
                    "compatibility": item.get("compatibility", [])
                })
            
            return standardized_results
        else:
            return [{"error": f"L'API a retourné le code {response.status_code}"}]
            
    except Exception as e:
        return [{"error": f"Exception lors de l'appel à l'API: {str(e)}"}]

def search_facebook_marketplace_mapping(query: str, category: str = None) -> list:
    """
    Recherche des cartographies sur Facebook Marketplace via scraping
    
    Args:
        query: Terme de recherche
        category: Catégorie de cartographie (optionnel)
        
    Returns:
        list: Liste des cartographies trouvées
    """
    # Validation des paramètres
    if category and category not in VALID_CATEGORIES:
        return [{"error": f"Catégorie invalide. Catégories valides: {', '.join(filter(None, VALID_CATEGORIES))}"}]
    
    # Construction de l'URL de recherche
    search_term = f"{query} {category if category else 'cartographie'}"
    search_url = f"https://www.facebook.com/marketplace/search/?query={quote_plus(search_term)}"
    
    # Headers pour simuler un navigateur
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    try:
        # En mode démonstration, on simule une réponse de scraping
        return get_demo_data(query, category, "facebook")
        
        # Note: le code ci-dessous est un exemple de scraping réel qui serait implémenté,
        # mais il est commenté car Facebook a des mesures anti-scraping avancées
        # et cela nécessiterait une solution plus robuste comme Selenium
        
        """
        response = requests.get(search_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return [{"error": f"Erreur lors de la récupération des données: code {response.status_code}"}]
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        results = []
        
        # Recherche des éléments de listings (dépend de la structure de la page)
        listing_items = soup.find_all("div", class_="item-inner")
        
        for item in listing_items:
            # Extraire les informations
            title_elem = item.find("span", class_="title")
            price_elem = item.find("span", class_="price")
            location_elem = item.find("span", class_="location")
            link_elem = item.find("a", class_="item-link")
            
            if title_elem and price_elem and link_elem:
                # Construire l'URL avec le référent d'affiliation
                base_url = link_elem.get("href", "")
                if base_url:
                    if "?" in base_url:
                        affiliate_url = f"{base_url}&ref=assistant_auto_ultime"
                    else:
                        affiliate_url = f"{base_url}?ref=assistant_auto_ultime"
                else:
                    affiliate_url = "#"
                
                result = {
                    "preparateur": "Vendeur Facebook",
                    "description": title_elem.text.strip(),
                    "price": price_elem.text.strip(),
                    "affiliate_link": affiliate_url,
                    "category": category or "Non spécifié",
                    "source": "Facebook Marketplace",
                    "location": location_elem.text.strip() if location_elem else "Non spécifié"
                }
                
                results.append(result)
        
        return results
        """
        
    except Exception as e:
        return [{"error": f"Erreur lors du scraping Facebook Marketplace: {str(e)}"}]

def search_leboncoin_mapping(query: str, category: str = None) -> list:
    """
    Recherche des cartographies sur Leboncoin via scraping
    
    Args:
        query: Terme de recherche
        category: Catégorie de cartographie (optionnel)
        
    Returns:
        list: Liste des cartographies trouvées
    """
    # Validation des paramètres
    if category and category not in VALID_CATEGORIES:
        return [{"error": f"Catégorie invalide. Catégories valides: {', '.join(filter(None, VALID_CATEGORIES))}"}]
    
    # En mode démonstration, on simule une réponse
    return get_demo_data(query, category, "leboncoin")

def search_facebook_groups_mapping(query: str, category: str = None) -> list:
    """
    Recherche des cartographies dans les groupes Facebook via scraping
    
    Args:
        query: Terme de recherche
        category: Catégorie de cartographie (optionnel)
        
    Returns:
        list: Liste des cartographies trouvées
    """
    # Validation des paramètres
    if category and category not in VALID_CATEGORIES:
        return [{"error": f"Catégorie invalide. Catégories valides: {', '.join(filter(None, VALID_CATEGORIES))}"}]
    
    # En mode démonstration, on simule une réponse
    return get_demo_data(query, category, "facebook_groups")

def get_demo_data(query: str, category: str, source: str) -> list:
    """
    Génère des données de démonstration pour les différentes sources
    
    Args:
        query: Terme de recherche
        category: Catégorie de cartographie
        source: Source de données (official, facebook, leboncoin, facebook_groups)
        
    Returns:
        list: Liste des cartographies simulées
    """
    # Extraire les mots-clés significatifs pour personnaliser les résultats
    keywords = query.lower().split()
    
    # Vérifier si un modèle de voiture est mentionné
    car_models = {
        "golf": "Volkswagen Golf",
        "bmw": "BMW",
        "mercedes": "Mercedes",
        "audi": "Audi",
        "renault": "Renault",
        "peugeot": "Peugeot",
        "citroen": "Citroën",
        "ford": "Ford",
        "308": "Peugeot 308",
        "megane": "Renault Megane",
        "clio": "Renault Clio",
        "a3": "Audi A3",
        "a4": "Audi A4",
        "a5": "Audi A5",
        "leon": "Seat Leon",
        "focus": "Ford Focus",
        "serie": "BMW Série",
        "classe": "Mercedes Classe"
    }
    
    car_model = None
    for keyword in keywords:
        if keyword in car_models:
            car_model = car_models[keyword]
            break
    
    # Définir la catégorie de tuning (origine, sport, competition)
    if not category:
        for keyword in keywords:
            if keyword in VALID_CATEGORIES and keyword is not None:
                category = keyword
                break
        if not category:
            category = random.choice(["origine", "sport", "competition"])
    
    # Générer des résultats en fonction de la source
    if source == "official":
        return generate_official_results(query, category, car_model)
    elif source == "facebook":
        return generate_facebook_results(query, category, car_model)
    elif source == "leboncoin":
        return generate_leboncoin_results(query, category, car_model)
    elif source == "facebook_groups":
        return generate_facebook_groups_results(query, category, car_model)
    else:
        return [{"error": "Source non reconnue"}]

def generate_official_results(query: str, category: str, car_model: str) -> list:
    """
    Génère des résultats démo pour les API officielles
    """
    # Création de préparateurs fictifs
    preparateurs = {
        "origine": ["EcoTuning", "OPTImap", "GreenTuners", "EconoPerf", "FuelSaver Pro"],
        "sport": ["SportTuning", "Stage1Performance", "PowerLab", "TuningBox", "MaxPower"],
        "competition": ["RaceTech", "CompetitionTuners", "TrackForce", "UltimateRace", "Pro-Competition"]
    }
    
    # Descriptions en fonction de la catégorie
    descriptions = {
        "origine": [
            "Cartographie optimisée économie de carburant",
            "Reprogrammation d'origine améliorée",
            "Cartographie ECO pour réduction de consommation",
            "Optimisation couple-consommation",
            "Reprogrammation écologique homologuée"
        ],
        "sport": [
            "Stage 1 optimisation moteur performance",
            "Cartographie sportive équilibrée",
            "Reprogrammation Stage 1 avec gains de puissance",
            "Optimisation sportive couple/puissance",
            "Stage 1+ avec gains jusqu'à 30%"
        ],
        "competition": [
            "Stage 3 competition track day",
            "Reprogrammation circuit compétition",
            "Cartographie racing professionnelle",
            "Programme haute performance non homologué",
            "Cartographie compétition maximale"
        ]
    }
    
    # Prix en fonction de la catégorie
    price_ranges = {
        "origine": (149, 299),
        "sport": (299, 499),
        "competition": (599, 999)
    }
    
    # Génération des résultats
    results = []
    num_results = random.randint(3, 6)
    
    for i in range(num_results):
        preparateur = random.choice(preparateurs[category])
        description_base = random.choice(descriptions[category])
        
        # Personnaliser la description avec le modèle de voiture si disponible
        if car_model:
            description = f"{description_base} pour {car_model}"
        else:
            description = description_base
            
        # Générer un prix aléatoire dans la fourchette de prix
        price_min, price_max = price_ranges[category]
        price = random.randint(price_min, price_max)
        
        # Ajouter des informations supplémentaires selon la source
        result = {
            "preparateur": preparateur,
            "description": description,
            "price": f"{price}.00€",
            "affiliate_link": f"https://example.com/cartographies/{preparateur.lower().replace(' ', '-')}/ref=assistant-auto-ultime",
            "category": category,
            "source": "API Partenaire Officiel",
            "rating": round(3.5 + random.random() * 1.5, 1),  # Note entre 3.5 et 5.0
            "compatibility": [car_model] if car_model else ["Tous modèles compatibles"],
            "gains": {
                "puissance": f"+{random.randint(10, 30)}%",
                "couple": f"+{random.randint(15, 35)}%",
                "consommation": f"{'-' if category == 'origine' else '+'}{random.randint(5, 15)}%"
            }
        }
        
        results.append(result)
    
    return results

def generate_facebook_results(query: str, category: str, car_model: str) -> list:
    """
    Génère des résultats démo pour Facebook Marketplace
    """
    results = []
    num_results = random.randint(2, 4)
    
    for i in range(num_results):
        if car_model:
            description = f"Cartographie {category} pour {car_model} - gains garantis"
        else:
            description = f"Cartographie moteur {category} toutes marques - optimisation garantie"
        
        # Prix selon catégorie
        if category == "origine":
            price = random.randint(120, 250)
        elif category == "sport":
            price = random.randint(250, 450)
        else:  # competition
            price = random.randint(450, 850)
        
        # Ajouter des informations
        result = {
            "preparateur": "Vendeur Facebook",
            "description": description,
            "price": f"{price}.00€",
            "affiliate_link": f"https://facebook.com/marketplace/item/{random.randint(1000000, 9999999)}?ref=assistant-auto-ultime",
            "category": category,
            "source": "Facebook Marketplace",
            "location": random.choice(["Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux", "Lille"]),
            "date_publication": (datetime.now().replace(microsecond=0) - \
                               datetime.timedelta(days=random.randint(1, 30))).isoformat()
        }
        
        results.append(result)
    
    return results

def generate_leboncoin_results(query: str, category: str, car_model: str) -> list:
    """
    Génère des résultats démo pour Leboncoin
    """
    results = []
    num_results = random.randint(2, 5)
    
    for i in range(num_results):
        if car_model:
            description = f"[PRO] Reprogrammation {category} {car_model} - Service rapide"
        else:
            description = f"[PRO] Service de reprogrammation {category} toutes marques"
        
        # Prix selon catégorie
        if category == "origine":
            price = random.randint(130, 280)
        elif category == "sport":
            price = random.randint(270, 470)
        else:  # competition
            price = random.randint(470, 900)
        
        # Ajouter des informations
        result = {
            "preparateur": "Préparateur Automobile",
            "description": description,
            "price": f"{price}.00€",
            "affiliate_link": f"https://www.leboncoin.fr/services/{random.randint(1000000, 9999999)}?ref=assistant-auto-ultime",
            "category": category,
            "source": "Leboncoin",
            "pro": True,
            "location": random.choice(["Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux", "Lille"]),
            "urgent": random.choice([True, False]),
            "date_publication": (datetime.now().replace(microsecond=0) - \
                                datetime.timedelta(days=random.randint(1, 15))).isoformat()
        }
        
        results.append(result)
    
    return results

def generate_facebook_groups_results(query: str, category: str, car_model: str) -> list:
    """
    Génère des résultats démo pour les groupes Facebook
    """
    groups = [
        "Échange de cartographies auto",
        "Passionnés reprogrammation moteur",
        f"Club {car_model}" if car_model else "Tuning et reprogrammation France",
        "Forum cartographie performance"
    ]
    
    results = []
    num_results = random.randint(1, 3)
    
    for i in range(num_results):
        group = random.choice(groups)
        
        if car_model:
            description = f"[DISPO] Cartographie sur mesure {category} pour {car_model}"
        else:
            description = f"Propose cartographies {category} personnalisées - toutes marques"
        
        # Prix selon catégorie
        if category == "origine":
            price = random.randint(100, 200)
        elif category == "sport":
            price = random.randint(200, 400)
        else:  # competition
            price = random.randint(400, 800)
        
        # Ajouter des informations
        result = {
            "preparateur": f"Membre du groupe '{group}'",
            "description": description,
            "price": f"{price}.00€",
            "affiliate_link": f"https://facebook.com/groups/{group.lower().replace(' ', '-')}/posts/{random.randint(1000000, 9999999)}?ref=assistant-auto-ultime",
            "category": category,
            "source": "Groupe Facebook",
            "group_name": group,
            "date_publication": (datetime.now().replace(microsecond=0) - \
                               datetime.timedelta(days=random.randint(1, 10))).isoformat()
        }
        
        results.append(result)
    
    return results

def search_mapping_offers(query: str, category: str = None) -> list:
    """
    Fonction principale d'agrégation pour la recherche de cartographies affiliées
    
    Args:
        query: Terme de recherche (ex: "cartographie bmw 320d")
        category: Catégorie (origine, sport, competition)
        
    Returns:
        list: Liste des offres de cartographies trouvées
    """
    # Valider la catégorie
    if category and category not in VALID_CATEGORIES:
        return [{"error": f"Catégorie invalide. Catégories valides: {', '.join(filter(None, VALID_CATEGORIES))}"}]
    
    results = []
    
    # Recherche via API officielle des cartographies
    official_results = search_official_mapping(query, category)
    if official_results and not (len(official_results) == 1 and "error" in official_results[0]):
        results.extend(official_results)
    
    # Recherche sur Facebook Marketplace
    facebook_results = search_facebook_marketplace_mapping(query, category)
    if facebook_results and not (len(facebook_results) == 1 and "error" in facebook_results[0]):
        results.extend(facebook_results)
    
    # Recherche sur Leboncoin
    leboncoin_results = search_leboncoin_mapping(query, category)
    if leboncoin_results and not (len(leboncoin_results) == 1 and "error" in leboncoin_results[0]):
        results.extend(leboncoin_results)
    
    # Recherche dans les groupes Facebook
    facebook_groups_results = search_facebook_groups_mapping(query, category)
    if facebook_groups_results and not (len(facebook_groups_results) == 1 and "error" in facebook_groups_results[0]):
        results.extend(facebook_groups_results)
    
    # Si aucun résultat n'a été trouvé
    if not results:
        return [{"error": "Aucune cartographie trouvée correspondant à votre recherche."}]
    
    return results

# Si le script est exécuté directement, effectuer un test
if __name__ == "__main__":
    test_query = "cartographie golf 7 gti"
    test_category = "sport"
    
    print(f"Test de recherche pour '{test_query}' dans la catégorie '{test_category}'...")
    results = search_mapping_offers(test_query, test_category)
    
    print(f"Nombre de résultats: {len(results)}")
    print("Premiers résultats:")
    for i, result in enumerate(results[:3]):
        print(f"\n--- Résultat {i+1} ---")
        for key, value in result.items():
            print(f"{key}: {value}")
