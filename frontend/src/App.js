import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { Container, Nav, Navbar, Card, Row, Col, Button, Dropdown, Alert, Badge } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Import des composants
import OCRCapture from './components/OCRCapture';
import OBD2Dashboard from './components/OBD2Dashboard';
import NLPAssistant from './components/NLPAssistant';
import ImageRecognition from './components/ImageRecognition';
import ECUFlash from './components/ECUFlash';
import PartsFinder from './components/PartsFinder';
import Auth from './components/Auth';

// Nouveaux imports pour l'étape 10
import Subscriptions from './components/Subscriptions';
import MappingAffiliations from './components/MappingAffiliations';

// Import du composant Feedback pour l'étape 11
import Feedback from './components/Feedback';

// Page d'accueil avec des cartes pour chaque module
const Home = () => {
  const [user, setUser] = useState(null);

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

  return (
    <Container className="mt-4">
      <div className="text-center mb-5">
        <h1 className="display-4 mb-3">Assistant Auto Ultime</h1>
        <p className="lead">
          Votre suite complète d'outils pour le diagnostic, l'optimisation et l'entretien de votre véhicule.
        </p>
        {user && (
          <div className="mb-4">
            <Alert variant="info">
              Bienvenue, <strong>{user.name}</strong>! 
              {user.subscriptionType && (
                <>
                  Vous avez un abonnement <Badge bg="primary">{user.subscriptionType}</Badge> 
                  {user.subscriptionEndDate && ` valable jusqu'au ${user.subscriptionEndDate}`}.
                </>
              )}
            </Alert>
          </div>
        )}
      </div>

      <Row>
        <Col md={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=OCR" />
            <Card.Body>
              <Card.Title>OCR</Card.Title>
              <Card.Text>
                Scannez votre carte grise et extrayez automatiquement toutes les informations de votre véhicule.
              </Card.Text>
              <Link to="/ocr" className="btn btn-primary">Accéder</Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=OBD-II" />
            <Card.Body>
              <Card.Title>OBD-II</Card.Title>
              <Card.Text>
                Connectez-vous à votre véhicule et obtenez des diagnostics en temps réel et des codes d'erreur.
              </Card.Text>
              <Link to="/obd2" className="btn btn-primary">Accéder</Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=NLP" />
            <Card.Body>
              <Card.Title>Assistant NLP</Card.Title>
              <Card.Text>
                Posez vos questions en langage naturel et obtenez des réponses précises sur votre véhicule.
              </Card.Text>
              <Link to="/nlp" className="btn btn-primary">Accéder</Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=Image" />
            <Card.Body>
              <Card.Title>Reconnaissance d'image</Card.Title>
              <Card.Text>
                Analysez visuellement des pannes ou anomalies en soumettant simplement une photo.
              </Card.Text>
              <Link to="/image-recognition" className="btn btn-primary">Accéder</Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=ECU" />
            <Card.Body>
              <Card.Title>ECU Flash</Card.Title>
              <Card.Text>
                Optimisez les performances de votre véhicule en reprogrammant l'ECU avec des paramètres personnalisés.
              </Card.Text>
              <Link to="/ecu-flash" className="btn btn-primary">Accéder</Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=Parts" />
            <Card.Body>
              <Card.Title>Parts Finder</Card.Title>
              <Card.Text>
                Trouvez facilement des pièces détachées pour votre véhicule à partir de multiples sources.
              </Card.Text>
              <Link to="/parts-finder" className="btn btn-primary">Accéder</Link>
            </Card.Body>
          </Card>
        </Col>
        {/* Nouvelles cartes pour les modules de l'étape 10 */}
        <Col md={6} className="mb-4">
          <Card className="h-100 shadow-sm border-primary">
            <Card.Header className="bg-primary text-white">
              <h5 className="mb-0">NOUVEAU</h5>
            </Card.Header>
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=Abonnement+Premium" />
            <Card.Body>
              <Card.Title>Abonnements</Card.Title>
              <Card.Text>
                Souscrivez à notre abonnement mensuel à 19,90€ et recevez un dongle OBD-II offert pour un diagnostic complet de votre véhicule.
              </Card.Text>
              <Link to="/subscriptions" className="btn btn-primary">Découvrir nos offres</Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6} className="mb-4">
          <Card className="h-100 shadow-sm border-success">
            <Card.Header className="bg-success text-white">
              <h5 className="mb-0">NOUVEAU</h5>
            </Card.Header>
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=Cartographies+Pro" />
            <Card.Body>
              <Card.Title>Cartographies Pro</Card.Title>
              <Card.Text>
                Trouvez les meilleures offres de reprogrammation moteur pour optimiser les performances ou réduire la consommation de votre véhicule.
              </Card.Text>
              <Link to="/mapping-affiliations" className="btn btn-success">Explorer les offres</Link>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* Ajout du composant Feedback pour l'étape 11 */}
      <Row className="mt-5">
        <Col md={8} className="mx-auto">
          <Feedback />
        </Col>
      </Row>
    </Container>
  );
};

// Composant principal de l'application
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  
  // Vérifier l'authentification au chargement de l'application
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('user');
    
    if (token && userStr) {
      setIsAuthenticated(true);
      try {
        setUser(JSON.parse(userStr));
      } catch (e) {
        console.error("Erreur lors du parsing des données utilisateur:", e);
      }
    }
  }, []);
  
  // Gérer la déconnexion
  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <Router>
      <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
        <Container>
          <Navbar.Brand as={Link} to="/">
            <img
              src="/logo192.png"
              width="30"
              height="30"
              className="d-inline-block align-top me-2"
              alt="Assistant Auto Ultime"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = "https://via.placeholder.com/30?text=AAU";
              }}
            />
            Assistant Auto Ultime
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link as={Link} to="/">Accueil</Nav.Link>
              
              {/* Menu déroulant pour le diagnostic */}
              <Dropdown as={Nav.Item}>
                <Dropdown.Toggle as={Nav.Link}>Diagnostic</Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item as={Link} to="/ocr">OCR Carte Grise</Dropdown.Item>
                  <Dropdown.Item as={Link} to="/obd2">OBD-II</Dropdown.Item>
                  <Dropdown.Item as={Link} to="/image-recognition">Reconnaissance d'image</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
              
              {/* Menu déroulant pour l'optimisation */}
              <Dropdown as={Nav.Item}>
                <Dropdown.Toggle as={Nav.Link}>Optimisation</Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item as={Link} to="/ecu-flash">ECU Flash</Dropdown.Item>
                  <Dropdown.Item as={Link} to="/mapping-affiliations">Cartographies Pro</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
              
              <Nav.Link as={Link} to="/nlp">Assistant Auto</Nav.Link>
              <Nav.Link as={Link} to="/parts-finder">Pièces détachées</Nav.Link>
              
              {/* Nouveaux liens pour l'étape 10 */}
              <Nav.Link as={Link} to="/subscriptions" className="text-primary">Abonnements</Nav.Link>
              
              {/* Nouveau lien pour le feedback (étape 11) */}
              <Nav.Link as={Link} to="/feedback" className="text-warning">Feedback</Nav.Link>
            </Nav>
            
            {isAuthenticated ? (
              <Dropdown align="end">
                <Dropdown.Toggle variant="outline-light" id="dropdown-user">
                  {user?.name || 'Profil'}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item as={Link} to="/profile">Mon Profil</Dropdown.Item>
                  <Dropdown.Item as={Link} to="/subscriptions">Gérer mon abonnement</Dropdown.Item>
                  <Dropdown.Item as={Link} to="/settings">Paramètres</Dropdown.Item>
                  <Dropdown.Divider />
                  <Dropdown.Item onClick={handleLogout}>Déconnexion</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            ) : (
              <>
                <Button variant="outline-light" as={Link} to="/auth" className="me-2">
                  Connexion
                </Button>
                <Button variant="primary" as={Link} to="/subscriptions">
                  S'abonner
                </Button>
              </>
            )}
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/ocr" element={isAuthenticated ? <OCRCapture /> : <Navigate to="/auth" />} />
        <Route path="/obd2" element={isAuthenticated ? <OBD2Dashboard /> : <Navigate to="/auth" />} />
        <Route path="/nlp" element={isAuthenticated ? <NLPAssistant /> : <Navigate to="/auth" />} />
        <Route path="/image-recognition" element={isAuthenticated ? <ImageRecognition /> : <Navigate to="/auth" />} />
        <Route path="/ecu-flash" element={isAuthenticated ? <ECUFlash /> : <Navigate to="/auth" />} />
        <Route path="/parts-finder" element={isAuthenticated ? <PartsFinder /> : <Navigate to="/auth" />} />
        <Route path="/auth" element={<Auth setIsAuthenticated={setIsAuthenticated} />} />
        
        {/* Nouvelles routes pour l'étape 10 */}
        <Route path="/subscriptions" element={<Subscriptions />} />
        <Route path="/mapping-affiliations" element={isAuthenticated ? <MappingAffiliations /> : <Navigate to="/auth" />} />
        
        {/* Nouvelle route dédiée au feedback (étape 11) */}
        <Route path="/feedback" element={
          <Container className="py-5">
            <Row>
              <Col md={8} className="mx-auto">
                <h2 className="mb-4 text-center">Votre avis compte</h2>
                <p className="text-center mb-5">
                  Nous travaillons constamment à améliorer Assistant Auto Ultime. 
                  Partagez vos impressions, signalez des bugs ou proposez des améliorations !
                </p>
                <Feedback />
              </Col>
            </Row>
          </Container>
        } />
        
        {/* Redirection par défaut */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
      
      <footer className="bg-light py-4 mt-5">
        <Container>
          <Row>
            <Col md={4}>
              <h5>Assistant Auto Ultime</h5>
              <p className="text-muted">
                © 2025 Assistant Auto Ultime. Tous droits réservés.
              </p>
            </Col>
            <Col md={4}>
              <h6>Abonnements</h6>
              <Nav className="flex-column">
                <Nav.Link as={Link} to="/subscriptions" className="text-muted p-0 mb-1">Offres & Tarifs</Nav.Link>
                <Nav.Link as={Link} to="/mapping-affiliations" className="text-muted p-0 mb-1">Cartographies Pro</Nav.Link>
                <Nav.Link as={Link} to="/feedback" className="text-muted p-0 mb-1">Donnez votre avis</Nav.Link>
                <Nav.Link href="#" className="text-muted p-0 mb-1">Devenir Partenaire</Nav.Link>
              </Nav>
            </Col>
            <Col md={4} className="text-md-end">
              <Button variant="link" className="text-muted">Conditions d'utilisation</Button>
              <Button variant="link" className="text-muted">Politique de confidentialité</Button>
              <Button variant="link" className="text-muted">Contact</Button>
            </Col>
          </Row>
        </Container>
      </footer>
    </Router>
  );
}

export default App;
