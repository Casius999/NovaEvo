# Module OCR

## Vue d'ensemble

Le module OCR (Optical Character Recognition) de NovaEvo est un composant clé permettant l'extraction automatisée d'informations à partir de documents automobiles physiques ou photographiés. Ce module transforme des images de documents en données structurées exploitables par l'ensemble de la plateforme, optimisant ainsi la création de profils véhicules et l'analyse contextuelle.

![Architecture module OCR](../images/ocr_module_architecture.png)

*Note: L'image est référencée à titre illustratif. Veuillez vous assurer que cette image existe dans le dépôt.*

## Objectifs et fonctionnalités

### Objectifs principaux

- Extraire avec précision les informations clés des documents automobiles
- Réduire la saisie manuelle et les erreurs associées
- Accélérer les processus d'identification véhicule
- Alimenter les autres modules avec des données structurées et validées
- Faciliter l'archivage numérique des documents importants

### Fonctionnalités clés

| Fonctionnalité | Description | État |
|----------------|-------------|------|
| **Scan Multi-Documents** | Reconnaissance et traitement de différents types de documents automobiles | ✅ Implémenté |
| **Extraction Précise** | Extraction des champs pertinents avec haute précision (>98%) | ✅ Implémenté |
| **Validation Contextuelle** | Vérification de cohérence des données extraites | ✅ Implémenté |
| **Correction Assistée** | Interface permettant de corriger les données mal reconnues | ✅ Implémenté |
| **Format Multi-Sources** | Support des photos, scans et PDF | ✅ Implémenté |
| **Reconnaissance Multi-Langues** | Support pour documents en français, anglais, allemand, etc. | 🟡 Partiel |
| **Détection de Fraude** | Identification des documents potentiellement falsifiés | 🔵 Planifié |

## Types de documents supportés

Le module OCR prend en charge une large gamme de documents automobiles :

### Documents officiels
- Certificat d'immatriculation (carte grise)
- Certificat de conformité (CoC)
- Certificat de cession
- Contrôle technique

### Documents constructeurs
- Carnets d'entretien
- Manuels utilisateur (sections spécifiques)
- Factures concessionnaires
- Bons de garantie

### Documents techniques
- Fiches techniques
- Rapports de diagnostic
- Factures de réparation
- Devis et estimations

## Architecture technique

Le module OCR est construit selon une architecture modulaire qui garantit extensibilité et performance :

```
┌───────────────────────────────────────────────────────────────────────────┐
│                        MODULE OCR NOVAEVO                                 │
└───────────────────────────────────────────────────────────────────────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
    ┌────────────▼─────────┐  ┌────▼────────────┐  ┌─▼──────────────────┐
    │  PRÉ-TRAITEMENT     │  │  RECONNAISSANCE │  │  POST-TRAITEMENT   │
    │                     │  │                 │  │                    │
    │ ┌─────────────────┐ │  │ ┌─────────────┐ │  │ ┌────────────────┐ │
    │ │ Normalisation   │ │  │ │ Moteur OCR  │ │  │ │ Validation     │ │
    │ └─────────────────┘ │  │ └─────────────┘ │  │ └────────────────┘ │
    │ ┌─────────────────┐ │  │ ┌─────────────┐ │  │ ┌────────────────┐ │
    │ │ Correction Image│ │  │ │ Classification│ │  │ │ Structuration │ │
    │ └─────────────────┘ │  │ └─────────────┘ │  │ └────────────────┘ │
    │ ┌─────────────────┐ │  │ ┌─────────────┐ │  │ ┌────────────────┐ │
    │ │ Segmentation    │ │  │ │ Extraction   │ │  │ │ Enrichissement │ │
    │ └─────────────────┘ │  │ └─────────────┘ │  │ └────────────────┘ │
    └─────────────────────┘  └─────────────────┘  └────────────────────┘
                 │                 │                 │
                 └─────────────────┼─────────────────┘
                                   │
           ┌─────────────────────────────────────────────┐
           │         INTERFACE MODULE CONTEXT            │
           └─────────────────────────────────────────────┘
```

### Composants principaux

#### 1. Pré-traitement
- **Normalisation** : Uniformisation de la taille, résolution et format
- **Correction d'image** : Amélioration du contraste, correction géométrique, suppression du bruit
- **Segmentation** : Identification des zones d'intérêt et séparation des éléments textuels

#### 2. Reconnaissance
- **Moteur OCR** : Système hybride combinant réseaux de neurones convolutifs (CNN) et transformers
- **Classification** : Identification du type de document et orientation du traitement
- **Extraction** : Reconnaissance des champs pertinents selon templates

#### 3. Post-traitement
- **Validation** : Vérification des données extraites (cohérence, format)
- **Structuration** : Organisation des données en schéma standard
- **Enrichissement** : Ajout de métadonnées et informations contextuelles

## Technologies utilisées

### Stack principal
- **Traitement d'image** : OpenCV, Pillow
- **OCR Engine** : Modèle custom basé sur Tesseract 5.0 et EasyOCR
- **Deep Learning** : TensorFlow, PyTorch pour modèles spécialisés
- **NLP** : BERT pour analyse contextuelle et correction
- **Validation** : Règles métier spécifiques et validation croisée

### Performances
- **Précision globale** : >98% sur documents de bonne qualité
- **Temps de traitement** : <3 secondes par document standard
- **Taux d'erreur** : <2% sur champs critiques

## Intégration avec autres modules

Le module OCR interagit avec plusieurs autres composants de NovaEvo :

| Module | Type d'interaction | Données échangées |
|--------|---------------------|-------------------|
| **Module Contexte** | Bidirectionnelle | Données véhicule, historique documents |
| **Module OBD2** | Sortante | Identification véhicule pour diagnostic |
| **Module Parts Finder** | Sortante | Spécifications pour recherche compatibilité |
| **Module Planification** | Sortante | Données maintenance pour planification |
| **Module Abonnements** | Entrante | Vérification droits d'accès fonctionnalités premium |

## Processus d'utilisation

### Workflow standard

1. **Acquisition** : L'utilisateur prend en photo ou importe un document
2. **Détection** : Le système identifie automatiquement le type de document
3. **Traitement** : OCR et extraction des champs pertinents
4. **Vérification** : Proposition des données reconnues à l'utilisateur pour validation
5. **Correction** : Interface intuitive pour corriger les éventuelles erreurs
6. **Validation** : Confirmation finale et intégration des données au profil

### Exemple : Scan carte grise

```sequence
Utilisateur->App Mobile: Photographie carte grise
App Mobile->Module OCR: Envoie image
Module OCR->Module OCR: Pré-traitement
Module OCR->Module OCR: Classification document
Module OCR->Module OCR: Extraction champs spécifiques
Module OCR->App Mobile: Retourne données structurées
App Mobile->Utilisateur: Affiche données pour vérification
Utilisateur->App Mobile: Corrige/Valide données
App Mobile->Module Contexte: Enregistre données véhicule
Module Contexte->App Mobile: Confirme enregistrement
App Mobile->Utilisateur: Affiche confirmation et suggestions
```

## Sécurité et conformité

### Protection des données
- Chiffrement des images en transit et au repos
- Suppression automatique des images après traitement
- Anonymisation des données sensibles dans les logs

### Conformité RGPD
- Traitement local des données quand possible
- Conservation minimale des images de documents
- Transparence sur l'utilisation des données extraites
- Droits d'accès et de suppression des données

## Métriques et KPIs

Le module OCR est évalué sur plusieurs métriques clés :

| Métrique | Objectif | Méthode de mesure |
|----------|----------|-------------------|
| **Taux de reconnaissance** | >98% | Précision extraction champs clés |
| **Taux de rejet** | <5% | % documents nécessitant intervention manuelle |
| **Temps de traitement** | <3s | Durée moyenne extraction à validation |
| **Satisfaction utilisateur** | >4.5/5 | Feedback après utilisation |
| **Réduction saisie** | >80% | % champs automatiquement remplis |

## Évolutions futures

Le roadmap d'évolution du module OCR inclut plusieurs améliorations majeures :

### Court terme (6 mois)
- Support complet documents européens (tous pays UE)
- Amélioration reconnaissance documents de mauvaise qualité
- Intégration OCR en temps réel (traitement pendant la prise de photo)

### Moyen terme (12 mois)
- Ajout détection fraude documentaire
- Extension aux documents d'assurance et financiers
- Fonctionnalité de comparaison automatique devis/facture

### Long terme (24 mois)
- OCR sur documents techniques complexes (schémas, diagrammes)
- Compréhension sémantique des manuels techniques
- Extraction automatique procédures maintenance spécifiques

## Ressources pour développeurs

### Accès à l'API

Le module OCR expose plusieurs endpoints API :

```
POST /api/v1/ocr/scan
GET /api/v1/ocr/supported-documents
POST /api/v1/ocr/validate
GET /api/v1/ocr/status/{job_id}
```

### Exemple d'intégration

```javascript
// Exemple d'appel au service OCR
async function scanDocument(imageFile, documentType = 'auto') {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('documentType', documentType);
  
  try {
    const response = await fetch('https://api.novaevo.com/api/v1/ocr/scan', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      },
      body: formData
    });
    
    return await response.json();
  } catch (error) {
    console.error('OCR processing failed:', error);
    throw error;
  }
}
```

### Documentation complète
- [API Reference](../api-docs/ocr-api.md)
- [Guide d'intégration](../integration-guides/ocr-integration.md)
- [Exemples de code](../code-examples/ocr-examples.md)

## Support et dépannage

### Problèmes courants

| Problème | Cause possible | Solution |
|----------|----------------|----------|
| **Faible précision** | Image floue ou mal cadrée | Utiliser guide de cadrage et vérifier éclairage |
| **Document non reconnu** | Type non supporté ou format inhabituel | Vérifier liste des documents supportés |
| **Champs manquants** | Zones textuelles trop pâles ou dégradées | Améliorer contraste ou saisir manuellement |
| **Lenteur traitement** | Connexion réseau faible ou image trop volumineuse | Réduire résolution ou utiliser WiFi |

### Contact support
- Support technique: [ocr-support@novaevo.com](mailto:ocr-support@novaevo.com)
- Documentation: [https://docs.novaevo.com/modules/ocr](https://docs.novaevo.com/modules/ocr)
- Communauté: [https://community.novaevo.com/ocr](https://community.novaevo.com/ocr)

## FAQ

### Questions fréquentes

**Q: Quels formats d'image sont supportés ?**
R: JPEG, PNG, TIFF et PDF jusqu'à 10 pages. Pour des performances optimales, privilégiez JPEG à résolution moyenne (min. 300 DPI).

**Q: Les documents peuvent-ils être traités hors-ligne ?**
R: Non, l'OCR nécessite une connexion internet pour accéder aux modèles de reconnaissance avancés et la validation des données.

**Q: Que se passe-t-il si le document n'est pas reconnu ?**
R: Le système propose une saisie manuelle guidée et enregistre l'échantillon pour amélioration future (avec consentement utilisateur).

**Q: Les données extraites sont-elles sauvegardées ?**
R: Oui, les données structurées sont intégrées au profil véhicule. Les images originales sont supprimées après traitement (délai max: 24h).

**Q: Comment corriger une erreur de reconnaissance ?**
R: L'interface de validation permet de corriger facilement les champs avant enregistrement final.

---

*Dernière mise à jour : 10 avril 2025*