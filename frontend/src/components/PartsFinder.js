import React, { useState } from 'react';
import { Container, Card, Button, Form, Alert, Spinner, Row, Col, Table, Badge, Tabs, Tab } from 'react-bootstrap';
import axios from 'axios';

const PartsFinder = () => {
  const [reference, setReference] = useState('');
  const [partType, setPartType] = useState('origine');
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeSource, setActiveSource] = useState('all');
  const [selectedPart, setSelectedPart] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  // Listes des types de pièces disponibles
  const partTypes = [
    { value: 'origine', label: "Pièce d'origine", badge: 'primary' },
    { value: 'sport', label: 'Pièce Sport', badge: 'success' },
    { value: 'competition', label: 'Pièce Compétition', badge: 'danger' }
  ];

  // Rechercher des pièces
  const searchParts = async () => {
    if (!reference.trim()) {
      setError("Veuillez entrer une référence de pièce");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSearchResults(null);
      setShowDetails(false);
      setSelectedPart(null);
      
      const response = await axios.post('/parts_finder', {
        reference: reference,
        type: partType
      });
      
      if (response.data.status === 'success') {
        setSearchResults(response.data);
        if (response.data.offers && response.data.offers.length === 0) {
          setError("Aucune pièce trouvée pour cette référence et ce type.");
        }
      } else if (response.data.status === 'error') {
        setError(response.data.message || "Erreur lors de la recherche");
      } else {
        setSearchResults(response.data);
      }
    } catch (err) {
      console.error("Erreur lors de la recherche de pièces:", err);
      setError("Une erreur s'est produite lors de la recherche. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  // Filtrer les résultats par source
  const getFilteredResults = () => {
    if (!searchResults || !searchResults.offers) return [];
    
    if (activeSource === 'all') {
      return searchResults.offers;
    } else {
      return searchResults.offers.filter(offer => offer.source === activeSource);
    }
  };

  // Obtenir les sources disponibles
  const getAvailableSources = () => {
    if (!searchResults || !searchResults.offers) return [];
    
    const sources = new Set();
    searchResults.offers.forEach(offer => {
      if (offer.source) {
        sources.add(offer.source);
      }
    });
    
    return ['all', ...Array.from(sources)];
  };

  // Afficher les détails d'une pièce
  const viewPartDetails = (part) => {
    setSelectedPart(part);
    setShowDetails(true);
  };

  // Formater le prix
  const formatPrice = (price, currency = 'EUR') => {
    if (price === undefined || price === null) return 'N/A';
    
    return new Intl.NumberFormat('fr-FR', { 
      style: 'currency', 
      currency: currency 
    }).format(price);
  };

  // Obtenir le badge pour le type de pièce
  const getPartTypeBadge = (type) => {
    const partType = partTypes.find(pt => pt.value === type);
    if (!partType) return <Badge bg="secondary">Autre</Badge>;
    
    return <Badge bg={partType.badge}>{partType.label}</Badge>;
  };

  // Afficher les résultats de recherche
  const renderSearchResults = () => {
    if (!searchResults || !searchResults.offers) return null;
    
    const filteredResults = getFilteredResults();
    const sources = getAvailableSources();
    
    if (filteredResults.length === 0) {
      return (
        <Alert variant="info">
          Aucune pièce trouvée pour cette source. Essayez une autre source ou modifiez vos critères de recherche.
        </Alert>
      );
    }
    
    return (
      <>
        {/* Onglets des sources */}
        <div className="mb-3">
          <Tabs
            activeKey={activeSource}
            onSelect={(key) => setActiveSource(key)}
            className="mb-3"
          >
            {sources.map((source) => (
              <Tab 
                key={source} 
                eventKey={source} 
                title={source === 'all' ? 'Toutes les sources' : source}
              />
            ))}
          </Tabs>
        </div>
        
        {/* Tableau des résultats */}
        <Table responsive striped hover>
          <thead>
            <tr>
              <th>Nom</th>
              <th>Prix</th>
              <th>Vendeur</th>
              <th>Source</th>
              <th>Livraison</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredResults.map((part, index) => (
              <tr key={index}>
                <td>
                  {part.name || 'Non spécifié'}
                  <br />
                  <small className="text-muted">Réf: {part.reference}</small>
                </td>
                <td>{formatPrice(part.price, part.currency)}</td>
                <td>{part.vendor || 'Non spécifié'}</td>
                <td>
                  <Badge 
                    bg={
                      part.source === 'API Officielle' ? 'primary' :
                      part.source === 'Facebook Marketplace' ? 'info' :
                      part.source === 'Leboncoin' ? 'success' :
                      part.source === 'Groupe Facebook' ? 'warning' :
                      'secondary'
                    }
                  >
                    {part.source || 'Non spécifié'}
                  </Badge>
                </td>
                <td>{part.delivery || 'Non spécifié'}</td>
                <td>
                  <Button 
                    variant="outline-primary" 
                    size="sm"
                    onClick={() => viewPartDetails(part)}
                  >
                    Détails
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </>
    );
  };

  // Afficher les détails d'une pièce
  const renderPartDetails = () => {
    if (!selectedPart) return null;
    
    return (
      <Card className="mb-4">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Détails de la pièce</h5>
          <Button 
            variant="outline-secondary" 
            size="sm"
            onClick={() => setShowDetails(false)}
          >
            Retour aux résultats
          </Button>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              <h4>{selectedPart.name || 'Non spécifié'}</h4>
              <p className="text-muted">Référence: {selectedPart.reference}</p>
              
              <h5 className="mt-4">Informations générales</h5>
              <Table bordered>
                <tbody>
                  <tr>
                    <th>Prix</th>
                    <td>{formatPrice(selectedPart.price, selectedPart.currency)}</td>
                  </tr>
                  <tr>
                    <th>Type</th>
                    <td>{getPartTypeBadge(partType)}</td>
                  </tr>
                  <tr>
                    <th>Vendeur</th>
                    <td>{selectedPart.vendor || 'Non spécifié'}</td>
                  </tr>
                  <tr>
                    <th>Source</th>
                    <td>{selectedPart.source || 'Non spécifié'}</td>
                  </tr>
                  <tr>
                    <th>Livraison</th>
                    <td>{selectedPart.delivery || 'Non spécifié'}</td>
                  </tr>
                  {selectedPart.stock !== undefined && (
                    <tr>
                      <th>Stock</th>
                      <td>
                        {selectedPart.stock > 0 ? (
                          <Badge bg="success">En stock ({selectedPart.stock})</Badge>
                        ) : (
                          <Badge bg="danger">Indisponible</Badge>
                        )}
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Col>
            
            <Col md={6}>
              <h5>Description</h5>
              <p>{selectedPart.description || 'Aucune description disponible'}</p>
              
              {selectedPart.compatible_models && selectedPart.compatible_models.length > 0 && (
                <>
                  <h5 className="mt-4">Modèles compatibles</h5>
                  <ul className="list-unstyled">
                    {selectedPart.compatible_models.map((model, index) => (
                      <li key={index}>
                        <i className="bi bi-check-circle-fill text-success me-2"></i>
                        {model.manufacturer} {model.name} ({model.years})
                      </li>
                    ))}
                  </ul>
                </>
              )}
              
              {selectedPart.url && (
                <div className="mt-4">
                  <a 
                    href={selectedPart.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="btn btn-primary"
                  >
                    Voir l'annonce
                  </a>
                </div>
              )}
            </Col>
          </Row>
        </Card.Body>
      </Card>
    );
  };

  return (
    <Container className="my-4">
      <h2 className="mb-4">Recherche de Pièces Détachées</h2>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      {/* Formulaire de recherche */}
      <Card className="mb-4">
        <Card.Body>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Référence de la pièce</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Ex: F-001, INJ-330D-01, etc."
                    value={reference}
                    onChange={(e) => setReference(e.target.value)}
                  />
                </Form.Group>
              </Col>
              
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Type de pièce</Form.Label>
                  <Form.Select
                    value={partType}
                    onChange={(e) => setPartType(e.target.value)}
                  >
                    {partTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            
            <div className="d-grid">
              <Button 
                variant="primary" 
                onClick={searchParts}
                disabled={loading || !reference.trim()}
              >
                {loading ? (
                  <>
                    <Spinner animation="border" size="sm" className="me-2" />
                    Recherche en cours...
                  </>
                ) : (
                  'Rechercher'
                )}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
      
      {/* Résultats de recherche ou détails de pièce */}
      {searchResults && (
        <Card>
          <Card.Header>
            <h5 className="mb-0">
              Résultats pour <strong>{searchResults.reference}</strong> (Type: {partType})
            </h5>
          </Card.Header>
          <Card.Body>
            {showDetails ? renderPartDetails() : renderSearchResults()}
          </Card.Body>
        </Card>
      )}
      
      {/* Informations sur les sources */}
      <Card className="mt-4">
        <Card.Header>Informations sur les sources</Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              <h5>Sources officielles</h5>
              <ul>
                <li><strong>API Officielle</strong> : Pièces détachées neuves de fournisseurs officiels</li>
                <li>Prix compétitifs, garantie fabricant, large disponibilité</li>
              </ul>
            </Col>
            
            <Col md={6}>
              <h5>Sources alternatives</h5>
              <ul>
                <li><strong>Facebook Marketplace</strong> : Particuliers et petits professionnels</li>
                <li><strong>Leboncoin</strong> : Petites annonces locales, bonnes affaires</li>
                <li><strong>Groupes Facebook</strong> : Communautés spécialisées, pièces rares</li>
              </ul>
            </Col>
          </Row>
          <Alert variant="info" className="mb-0 mt-3">
            <i className="bi bi-info-circle-fill me-2"></i>
            Vérifiez toujours la compatibilité avec votre véhicule et l'état des pièces avant achat, 
            particulièrement pour les sources alternatives.
          </Alert>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default PartsFinder;