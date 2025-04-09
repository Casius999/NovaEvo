import React, { useState, useEffect } from 'react';
import { Container, Card, Row, Col, Button, Alert, Badge, Form, Spinner } from 'react-bootstrap';

const Subscriptions = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [success, setSuccess] = useState(null);
  const [user, setUser] = useState(null);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    confirmPassword: '',
  });
  const [step, setStep] = useState('select-plan'); // steps: select-plan, register, payment, success
  const [processing, setProcessing] = useState(false);

  // Charger l'utilisateur depuis le localStorage s'il existe
  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const userData = JSON.parse(userStr);
        setUser(userData);
        // Si l'utilisateur a déjà un abonnement actif
        if (userData.subscriptionStatus === 'active') {
          setSuccess(`Vous avez déjà un abonnement actif (${userData.subscriptionType}).`);
        }
      } catch (e) {
        console.error("Erreur lors du parsing des données utilisateur:", e);
      }
    }
  }, []);

  // Charger les plans d'abonnement
  useEffect(() => {
    const fetchPlans = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch('/subscribe/plans');
        if (!response.ok) throw new Error('Erreur lors de la récupération des plans');
        
        const data = await response.json();
        if (data.status === 'success' && Array.isArray(data.plans)) {
          setPlans(data.plans);
          // Sélectionner le plan basic par défaut (19,90€/mois)
          const basicPlan = data.plans.find(p => p.id === 'price_basic');
          if (basicPlan) setSelectedPlan(basicPlan);
        } else {
          throw new Error('Format de données invalide');
        }
      } catch (err) {
        console.error('Erreur:', err);
        setError('Impossible de charger les plans d\'abonnement. Veuillez réessayer plus tard.');

        // En mode développement, utiliser des plans de secours
        const fallbackPlans = [
          {
            id: "price_basic",
            name: "Formule Standard",
            price: 19.90,
            currency: "EUR",
            interval: "month",
            description: "Abonnement mensuel à 19,90€ avec dongle OBD-II offert",
            features: [
              "Diagnostic OBD-II en temps réel",
              "Reconnaissance de pièces par image",
              "Assistant NLP automobile",
              "Recherche de pièces détachées",
              "OCR pour cartes grises",
              "Cartographies moteur standard",
              "Dongle OBD-II inclus"
            ]
          },
          {
            id: "price_premium",
            name: "Formule Premium",
            price: 29.90,
            currency: "EUR",
            interval: "month",
            description: "Abonnement premium avec fonctionnalités avancées",
            features: [
              "Toutes les fonctionnalités Standard",
              "Cartographies moteur avancées",
              "Flash ECU illimité",
              "Support technique prioritaire",
              "Dongle OBD-II Pro inclus",
              "Mise à jour hebdomadaire des bases de données"
            ]
          }
        ];
        
        setPlans(fallbackPlans);
        setSelectedPlan(fallbackPlans[0]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchPlans();
  }, []);

  // Gérer le changement dans les champs du formulaire
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  // Sélectionner un plan
  const handleSelectPlan = (plan) => {
    setSelectedPlan(plan);
    setStep('register');
  };

  // Validation du formulaire
  const validateForm = () => {
    if (!formData.email || !formData.password) {
      setError('Veuillez remplir tous les champs obligatoires.');
      return false;
    }
    
    if (step === 'register' && formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas.');
      return false;
    }
    
    if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      setError('Veuillez entrer une adresse email valide.');
      return false;
    }
    
    if (formData.password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères.');
      return false;
    }
    
    return true;
  };

  // Soumettre le formulaire d'inscription/paiement
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    
    if (!validateForm()) return;
    
    setProcessing(true);
    
    try {
      // Préparation des données pour l'API
      const subscriptionData = {
        email: formData.email,
        password: formData.password,
        name: formData.name,
        plan_id: selectedPlan.id
      };
      
      // Appel à l'API d'abonnement
      const response = await fetch('/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(subscriptionData)
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        // Si le paiement est déjà confirmé (comme dans notre cas de démonstration)
        setSuccess('Félicitations ! Votre abonnement a été créé avec succès.');
        setStep('success');
        
        // Mettre à jour les informations utilisateur en local
        const userData = {
          email: formData.email,
          name: formData.name || 'Utilisateur',
          subscriptionId: data.subscription_id,
          subscriptionStatus: data.subscription_status,
          subscriptionType: selectedPlan.name
        };
        
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('auth_token', 'subscription_token_' + Math.random().toString(36).substr(2, 9));
        setUser(userData);
      } else {
        setError(data.message || 'Une erreur est survenue lors de la création de l\'abonnement.');
      }
    } catch (err) {
      console.error('Erreur:', err);
      setError('Erreur de communication avec le serveur. Veuillez réessayer plus tard.');
    } finally {
      setProcessing(false);
    }
  };

  // Afficher le formulaire selon l'étape actuelle
  const renderForm = () => {
    if (step === 'select-plan') {
      return (
        <Row>
          {plans.map((plan) => (
            <Col md={6} key={plan.id} className="mb-4">
              <Card className={`h-100 ${selectedPlan && selectedPlan.id === plan.id ? 'border-primary' : ''}`}>
                <Card.Header className={selectedPlan && selectedPlan.id === plan.id ? 'bg-primary text-white' : ''}>
                  <h5 className="mb-0">{plan.name}</h5>
                </Card.Header>
                <Card.Body>
                  <h3 className="mb-3">{plan.price.toFixed(2)}€ <small className="text-muted">/ mois</small></h3>
                  <p>{plan.description}</p>
                  <hr />
                  <h6>Fonctionnalités incluses :</h6>
                  <ul className="list-unstyled">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="mb-2">
                        <i className="bi bi-check-circle-fill text-success me-2"></i>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </Card.Body>
                <Card.Footer>
                  <Button 
                    variant={selectedPlan && selectedPlan.id === plan.id ? 'primary' : 'outline-primary'} 
                    className="w-100"
                    onClick={() => handleSelectPlan(plan)}
                  >
                    Choisir cette formule
                  </Button>
                </Card.Footer>
              </Card>
            </Col>
          ))}
        </Row>
      );
    }
    
    if (step === 'register') {
      return (
        <Card>
          <Card.Header>
            <h5 className="mb-0">Inscription</h5>
          </Card.Header>
          <Card.Body>
            <p>Vous avez sélectionné : <Badge bg="primary">{selectedPlan?.name}</Badge> à {selectedPlan?.price.toFixed(2)}€/mois</p>
            
            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3">
                <Form.Label>Email*</Form.Label>
                <Form.Control 
                  type="email" 
                  name="email" 
                  value={formData.email} 
                  onChange={handleInputChange} 
                  required 
                />
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Nom</Form.Label>
                <Form.Control 
                  type="text" 
                  name="name" 
                  value={formData.name} 
                  onChange={handleInputChange} 
                />
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Mot de passe*</Form.Label>
                <Form.Control 
                  type="password" 
                  name="password" 
                  value={formData.password} 
                  onChange={handleInputChange} 
                  required 
                />
                <Form.Text className="text-muted">
                  Minimum 6 caractères
                </Form.Text>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Confirmer le mot de passe*</Form.Label>
                <Form.Control 
                  type="password" 
                  name="confirmPassword" 
                  value={formData.confirmPassword} 
                  onChange={handleInputChange} 
                  required 
                />
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Check 
                  type="checkbox" 
                  id="terms" 
                  label="J'accepte les conditions générales de vente" 
                  required 
                />
              </Form.Group>
              
              <div className="d-grid gap-2">
                <Button 
                  variant="primary" 
                  type="submit" 
                  disabled={processing}
                >
                  {processing ? (
                    <>
                      <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
                      Traitement en cours...
                    </>
                  ) : (
                    "S'abonner maintenant"
                  )}
                </Button>
                <Button 
                  variant="outline-secondary" 
                  onClick={() => setStep('select-plan')}
                  disabled={processing}
                >
                  Retour aux plans
                </Button>
              </div>
            </Form>
          </Card.Body>
        </Card>
      );
    }
    
    if (step === 'success') {
      return (
        <Card className="border-success">
          <Card.Header className="bg-success text-white">
            <h5 className="mb-0">Abonnement confirmé</h5>
          </Card.Header>
          <Card.Body>
            <div className="text-center mb-4">
              <i className="bi bi-check-circle-fill text-success" style={{ fontSize: "3rem" }}></i>
              <h4 className="mt-3">Félicitations !</h4>
            </div>
            
            <Alert variant="success">
              {success}
            </Alert>
            
            <p>Vous êtes maintenant abonné à la formule <strong>{selectedPlan?.name}</strong>.</p>
            <p>Votre dongle OBD-II sera expédié dans les prochains jours à l'adresse renseignée dans votre profil.</p>
            
            <hr />
            
            <div className="d-grid gap-2">
              <Button variant="primary" href="/">
                Accéder à votre espace
              </Button>
            </div>
          </Card.Body>
        </Card>
      );
    }
  };

  return (
    <Container className="py-4">
      <h2 className="mb-4">Abonnements</h2>
      
      {user && user.subscriptionStatus === 'active' ? (
        <Alert variant="info">
          <h5>Vous avez déjà un abonnement actif</h5>
          <p>Vous êtes actuellement abonné à la formule <Badge bg="primary">{user.subscriptionType}</Badge>.</p>
          <p>Pour gérer votre abonnement, rendez-vous dans votre espace "Profil".</p>
        </Alert>
      ) : (
        <>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}
          
          {loading ? (
            <div className="text-center my-5">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Chargement...</span>
              </Spinner>
              <p className="mt-3">Chargement des offres d'abonnement...</p>
            </div>
          ) : (
            renderForm()
          )}
        </>
      )}
      
      <div className="mt-5">
        <h5>Avantages de l'abonnement</h5>
        <Row className="mt-3">
          <Col sm={6} md={3} className="mb-3">
            <Card className="h-100 text-center">
              <Card.Body>
                <i className="bi bi-box-seam text-primary mb-3" style={{ fontSize: "2rem" }}></i>
                <h6>Dongle OBD-II Offert</h6>
                <p className="small text-muted">Matériel professionnel pour le diagnostic</p>
              </Card.Body>
            </Card>
          </Col>
          <Col sm={6} md={3} className="mb-3">
            <Card className="h-100 text-center">
              <Card.Body>
                <i className="bi bi-graph-up text-primary mb-3" style={{ fontSize: "2rem" }}></i>
                <h6>Fonctionnalités Premium</h6>
                <p className="small text-muted">Accès à toutes les fonctionnalités avancées</p>
              </Card.Body>
            </Card>
          </Col>
          <Col sm={6} md={3} className="mb-3">
            <Card className="h-100 text-center">
              <Card.Body>
                <i className="bi bi-cloud-check text-primary mb-3" style={{ fontSize: "2rem" }}></i>
                <h6>Mises à jour automatiques</h6>
                <p className="small text-muted">Toujours à jour avec les dernières versions</p>
              </Card.Body>
            </Card>
          </Col>
          <Col sm={6} md={3} className="mb-3">
            <Card className="h-100 text-center">
              <Card.Body>
                <i className="bi bi-headset text-primary mb-3" style={{ fontSize: "2rem" }}></i>
                <h6>Support prioritaire</h6>
                <p className="small text-muted">Assistance technique par email et téléphone</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </div>
    </Container>
  );
};

export default Subscriptions;
