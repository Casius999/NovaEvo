import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, InputGroup, Spinner, Alert, Badge } from 'react-bootstrap';

const MappingAffiliations = () => {
  // État local
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState('default');
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });
  const [user, setUser] = useState(null);

  // Charger l'utilisateur depuis le localStorage s'il existe
  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const userData = JSON.parse(userStr);
        setUser(userData);
      } catch (e) {
        console.error("Erreur lors du parsing des données utilisateur:", e);
      }
    }
  }, []);

  // Suggestions de recherche populaires
  const popularQueries = [
    'cartographie golf 7 gti',
    'reprogrammation bmw 320d',
    'stage 1 audi a3',
    'eco reprogrammation 308',
    'cartographie renault megane rs'
  ];

  // Effectuer la recherche
  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Veuillez entrer un terme de recherche');
      return;
    }
    
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await fetch('/mapping_affiliations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: query,
          category: category || null
        })
      });
      
      if (!response.ok) {
        throw new Error(`Erreur de serveur: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.offers && Array.isArray(data.offers)) {
        if (data.offers.length === 0) {
          setError('Aucun résultat trouvé pour votre recherche. Essayez d\'autres termes ou catégories.');
        } else {
          setResults(data.offers);
          setSuccess(`${data.offers.length} résultat(s) trouvé(s) pour votre recherche.`);
        }
      } else if (data.error) {
        setError(data.error);
      } else {
        setError('Format de réponse invalide');
      }
    } catch (err) {
      console.error('Erreur lors de la recherche:', err);
      setError(`Erreur lors de la recherche: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Effectuer une recherche à partir d'une suggestion
  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    // Soumettre la recherche automatiquement
    const event = { preventDefault: () => {} };
    handleSearch(event);
  };

  // Trier les résultats
  const sortResults = (resultsToSort) => {
    if (!resultsToSort) return [];
    
    let sortedResults = [...resultsToSort];
    
    switch (sortBy) {
      case 'price-asc':
        sortedResults.sort((a, b) => {
          const priceA = parseFloat(a.price.replace(/[^\d.-]/g, ''));
          const priceB = parseFloat(b.price.replace(/[^\d.-]/g, ''));
          return priceA - priceB;
        });
        break;
      case 'price-desc':
        sortedResults.sort((a, b) => {
          const priceA = parseFloat(a.price.replace(/[^\d.-]/g, ''));
          const priceB = parseFloat(b.price.replace(/[^\d.-]/g, ''));
          return priceB - priceA;
        });
        break;
      case 'rating':
        sortedResults.sort((a, b) => {
          const ratingA = a.rating || 0;
          const ratingB = b.rating || 0;
          return ratingB - ratingA;
        });
        break;
      default:
        // Par défaut, on ne trie pas
        break;
    }
    
    // Filtrer par fourchette de prix si définie
    if (priceRange.min || priceRange.max) {
      sortedResults = sortedResults.filter(item => {
        const price = parseFloat(item.price.replace(/[^\d.-]/g, ''));
        
        if (priceRange.min && priceRange.max) {
          return price >= parseFloat(priceRange.min) && price <= parseFloat(priceRange.max);
        } else if (priceRange.min) {
          return price >= parseFloat(priceRange.min);
        } else if (priceRange.max) {
          return price <= parseFloat(priceRange.max);
        }
        
        return true;
      });
    }
    
    return sortedResults;
  };

  // Formater le prix pour l'affichage
  const formatPrice = (price) => {
    if (!price) return 'Prix non disponible';
    
    // S'assurer que le prix est une chaîne
    const priceStr = String(price);
    
    // Vérifier si le prix contient déjà un symbole monétaire
    if (priceStr.includes('€') || priceStr.includes('$')) {
      return priceStr;
    }
    
    return `${priceStr}€`;
  };

  // Afficher la source avec un badge
  const renderSourceBadge = (source) => {
    let variant = 'secondary';
    
    if (source.includes('API') || source.includes('Officiel')) {
      variant = 'primary';
    } else if (source.includes('Facebook')) {
      variant = 'info';
    } else if (source.includes('Leboncoin')) {
      variant = 'warning';
    }
    
    return <Badge bg={variant}>{source}</Badge>;
  };

  // Afficher les étoiles pour les notes
  const renderRating = (rating) => {
    if (!rating) return null;
    
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    return (
      <div className="mb-2">
        {[...Array(fullStars)].map((_, i) => (
          <i key={`full-${i}`} className="bi bi-star-fill text-warning"></i>
        ))}
        {hasHalfStar && <i className="bi bi-star-half text-warning"></i>}
        {[...Array(emptyStars)].map((_, i) => (
          <i key={`empty-${i}`} className="bi bi-star text-warning"></i>
        ))}
        <span className="ms-1 text-muted">({rating.toFixed(1)})</span>
      </div>
    );
  };

  // Gérer le clic sur un lien d'affiliation
  const handleAffiliateClick = (offer) => {
    // Enregistrer la conversion (pour des statistiques, par exemple)
    console.log('Clic sur affiliation:', offer);
    
    // En situation réelle, on pourrait envoyer ces données au serveur
    // fetch('/api/affiliate/track', { method: 'POST', body: JSON.stringify({ offer_id: offer.id }) });
    
    // Rediriger vers le lien d'affiliation (dans une nouvelle fenêtre/onglet)
    window.open(offer.affiliate_link, '_blank');
  };

  return (
    <Container className="py-4">
      <h2 className="mb-4">Cartographies Pro Affiliées</h2>
      
      {!user || !user.subscriptionStatus === 'active' ? (
        <Alert variant="warning">
          <h5>Abonnement requis</h5>
          <p>Cette fonctionnalité nécessite un abonnement actif. Veuillez vous abonner pour accéder à notre service d'affiliation de cartographies.</p>
          <Button variant="primary" href="/subscriptions">Voir les abonnements</Button>
        </Alert>
      ) : (
        <>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
          
          <Card className="mb-4">
            <Card.Body>
              <Form onSubmit={handleSearch}>
                <Form.Group className="mb-3">
                  <Form.Label>Rechercher une cartographie</Form.Label>
                  <InputGroup>
                    <Form.Control
                      type="text"
                      placeholder="Ex: cartographie golf 7 gti, reprogrammation bmw 320d..."
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                    />
                    <Button variant="primary" type="submit" disabled={loading}>
                      {loading ? (
                        <>
                          <Spinner
                            as="span"
                            animation="border"
                            size="sm"
                            role="status"
                            aria-hidden="true"
                            className="me-2"
                          />
                          Recherche...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-search me-2"></i>
                          Rechercher
                        </>
                      )}
                    </Button>
                  </InputGroup>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Catégorie</Form.Label>
                  <Form.Select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                  >
                    <option value="">Toutes catégories</option>
                    <option value="origine">Origine / Éco</option>
                    <option value="sport">Sport</option>
                    <option value="competition">Compétition</option>
                  </Form.Select>
                </Form.Group>
                
                <div className="d-flex align-items-center mb-3">
                  <Button
                    variant="link"
                    className="p-0 me-3"
                    onClick={() => setShowFilters(!showFilters)}
                  >
                    <i className={`bi bi-funnel-fill me-1 ${showFilters ? 'text-primary' : ''}`}></i>
                    {showFilters ? 'Masquer les filtres' : 'Afficher les filtres'}
                  </Button>
                  
                  {results.length > 0 && (
                    <small className="text-muted ms-auto">{results.length} résultat(s) trouvé(s)</small>
                  )}
                </div>
                
                {showFilters && (
                  <Row className="mb-3">
                    <Col md={6}>
                      <Form.Group>
                        <Form.Label>Trier par</Form.Label>
                        <Form.Select
                          value={sortBy}
                          onChange={(e) => setSortBy(e.target.value)}
                        >
                          <option value="default">Pertinence</option>
                          <option value="price-asc">Prix croissant</option>
                          <option value="price-desc">Prix décroissant</option>
                          <option value="rating">Meilleures notes</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group>
                        <Form.Label>Fourchette de prix (€)</Form.Label>
                        <Row>
                          <Col>
                            <Form.Control
                              type="number"
                              placeholder="Min"
                              value={priceRange.min}
                              onChange={(e) => setPriceRange({ ...priceRange, min: e.target.value })}
                            />
                          </Col>
                          <Col>
                            <Form.Control
                              type="number"
                              placeholder="Max"
                              value={priceRange.max}
                              onChange={(e) => setPriceRange({ ...priceRange, max: e.target.value })}
                            />
                          </Col>
                        </Row>
                      </Form.Group>
                    </Col>
                  </Row>
                )}
              </Form>
              
              {/* Suggestions de recherche */}
              {!loading && results.length === 0 && (
                <div className="mt-3">
                  <small className="text-muted">Recherches populaires :</small>
                  <div className="mt-2">
                    {popularQueries.map((suggestion, index) => (
                      <Badge
                        bg="light"
                        text="dark"
                        className="me-2 mb-2"
                        key={index}
                        style={{ cursor: 'pointer' }}
                        onClick={() => handleSuggestionClick(suggestion)}
                      >
                        {suggestion}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </Card.Body>
          </Card>
          
          {/* Résultats de recherche */}
          {loading ? (
            <div className="text-center my-5">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Chargement...</span>
              </Spinner>
              <p className="mt-3">Recherche de cartographies en cours...</p>
            </div>
          ) : (
            results.length > 0 && (
              <div className="mb-4">
                <h4 className="mb-3">Résultats</h4>
                <Row>
                  {sortResults(results).map((offer, index) => (
                    <Col md={6} lg={4} className="mb-4" key={index}>
                      <Card className="h-100 shadow-sm">
                        <Card.Header>
                          <div className="d-flex justify-content-between align-items-center">
                            <Badge bg={
                              offer.category === 'origine' ? 'success' :
                              offer.category === 'sport' ? 'warning' :
                              offer.category === 'competition' ? 'danger' : 'secondary'
                            }>
                              {offer.category === 'origine' ? 'Origine / Éco' : 
                               offer.category === 'sport' ? 'Sport' : 
                               offer.category === 'competition' ? 'Compétition' : 
                               offer.category}
                            </Badge>
                            {renderSourceBadge(offer.source)}
                          </div>
                        </Card.Header>
                        <Card.Body>
                          <Card.Title className="text-truncate">{offer.preparateur}</Card.Title>
                          <Card.Text className="mb-3">
                            {offer.description}
                          </Card.Text>
                          
                          {offer.rating && renderRating(offer.rating)}
                          
                          {offer.gains && (
                            <div className="mb-3">
                              <small className="text-muted">Gains estimés :</small>
                              <div className="d-flex flex-wrap mt-1">
                                {Object.entries(offer.gains).map(([key, value]) => (
                                  <Badge bg="light" text="dark" className="me-2 mb-1" key={key}>
                                    {key}: {value}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {offer.compatibility && offer.compatibility.length > 0 && (
                            <div className="mb-3">
                              <small className="text-muted">Compatibilité :</small>
                              <div className="d-flex flex-wrap mt-1">
                                {offer.compatibility.map((item, i) => (
                                  <Badge bg="light" text="dark" className="me-2 mb-1" key={i}>
                                    {item}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </Card.Body>
                        <Card.Footer className="d-flex justify-content-between align-items-center">
                          <h5 className="mb-0 text-primary">{formatPrice(offer.price)}</h5>
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handleAffiliateClick(offer)}
                          >
                            <i className="bi bi-box-arrow-up-right me-1"></i>
                            Voir l'offre
                          </Button>
                        </Card.Footer>
                      </Card>
                    </Col>
                  ))}
                </Row>
              </div>
            )
          )}
          
          {/* Informations sur le service */}
          <Card className="bg-light border-0 mt-4">
            <Card.Body>
              <h5>À propos des cartographies proposées</h5>
              <p>
                Notre service vous permet de trouver les meilleures offres de cartographies moteur pour votre véhicule.
                Nous sélectionnons des préparateurs qualifiés et de confiance pour vous garantir une reprogrammation de qualité.
              </p>
              <Row className="mt-4">
                <Col md={4} className="mb-3 mb-md-0">
                  <div className="d-flex align-items-center">
                    <div className="me-3">
                      <i className="bi bi-shield-check text-success" style={{ fontSize: "2rem" }}></i>
                    </div>
                    <div>
                      <h6 className="mb-1">Sécurité</h6>
                      <p className="small text-muted mb-0">Préparateurs certifiés et cartographies testées</p>
                    </div>
                  </div>
                </Col>
                <Col md={4} className="mb-3 mb-md-0">
                  <div className="d-flex align-items-center">
                    <div className="me-3">
                      <i className="bi bi-speedometer2 text-primary" style={{ fontSize: "2rem" }}></i>
                    </div>
                    <div>
                      <h6 className="mb-1">Performance</h6>
                      <p className="small text-muted mb-0">Gains de puissance et d'économie garantis</p>
                    </div>
                  </div>
                </Col>
                <Col md={4}>
                  <div className="d-flex align-items-center">
                    <div className="me-3">
                      <i className="bi bi-tools text-warning" style={{ fontSize: "2rem" }}></i>
                    </div>
                    <div>
                      <h6 className="mb-1">Service</h6>
                      <p className="small text-muted mb-0">Installation et support technique inclus</p>
                    </div>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </>
      )}
    </Container>
  );
};

export default MappingAffiliations;
