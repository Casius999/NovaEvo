import React, { useState, useEffect } from 'react';
import { Container, Card, Button, Form, Alert, Spinner, ProgressBar, Row, Col, Table } from 'react-bootstrap';
import axios from 'axios';

const ECUFlash = () => {
  const [ecuConnected, setEcuConnected] = useState(false);
  const [currentMap, setCurrentMap] = useState(null);
  const [tuningParams, setTuningParams] = useState({
    cartographie_injection: 100,
    boost_turbo: 1.0,
    avance_allumage: 0,
    limiteur_regime: 6500
  });
  const [secureLimits, setSecureLimits] = useState(null);
  const [loading, setLoading] = useState(false);
  const [flashProgress, setFlashProgress] = useState(0);
  const [flashStatus, setFlashStatus] = useState('idle'); // 'idle', 'flashing', 'success', 'error'
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  // Récupérer les limites de sécurité au chargement du composant
  useEffect(() => {
    const fetchSecureLimits = async () => {
      try {
        const response = await axios.get('/ecu_flash/parameters');
        if (response.data && response.data.parameters) {
          setSecureLimits(response.data.parameters);
        }
      } catch (err) {
        console.error("Erreur lors de la récupération des limites de sécurité:", err);
      }
    };

    fetchSecureLimits();
  }, []);

  // Connecter à l'ECU
  const connectECU = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('/ecu_flash/connect');
      
      if (response.data.success) {
        setEcuConnected(true);
        // Récupérer la cartographie actuelle
        readCurrentMap();
        // Ajouter l'événement à l'historique
        addToHistory('Connexion à l\'ECU réussie');
      } else {
        setError(response.data.message || "Erreur de connexion à l'ECU");
        addToHistory('Échec de connexion à l\'ECU');
      }
    } catch (err) {
      console.error("Erreur lors de la connexion à l'ECU:", err);
      setError("Impossible de se connecter à l'ECU. Vérifiez que l'interface est correctement branchée.");
      addToHistory('Erreur lors de la tentative de connexion');
    } finally {
      setLoading(false);
    }
  };

  // Déconnecter l'ECU
  const disconnectECU = () => {
    setEcuConnected(false);
    setCurrentMap(null);
    addToHistory('Déconnexion de l\'ECU');
  };

  // Lire la cartographie actuelle
  const readCurrentMap = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('/ecu_flash/read');
      
      if (!response.data.error) {
        setCurrentMap(response.data);
        // Mettre à jour les paramètres de tuning avec les valeurs actuelles
        if (response.data.parameters) {
          setTuningParams({
            cartographie_injection: response.data.parameters.cartographie_injection || 100,
            boost_turbo: response.data.parameters.boost_turbo || 1.0,
            avance_allumage: response.data.parameters.avance_allumage || 0,
            limiteur_regime: response.data.parameters.limiteur_regime || 6500
          });
        }
        addToHistory('Lecture de la cartographie actuelle réussie');
      } else {
        setError(response.data.error || "Erreur lors de la lecture de l'ECU");
        addToHistory('Échec de la lecture de la cartographie');
      }
    } catch (err) {
      console.error("Erreur lors de la lecture de l'ECU:", err);
      setError("Impossible de lire les données de l'ECU.");
      addToHistory('Erreur lors de la lecture de l\'ECU');
    } finally {
      setLoading(false);
    }
  };

  // Mettre à jour un paramètre de tuning
  const handleParamChange = (param, value) => {
    // Convertir en nombre
    const numValue = parseFloat(value);
    // Vérifier si la valeur est un nombre valide
    if (isNaN(numValue)) return;
    
    // Appliquer les limites de sécurité si disponibles
    if (secureLimits && secureLimits[param]) {
      const { min, max } = secureLimits[param];
      if (numValue < min) return;
      if (numValue > max) return;
    }
    
    setTuningParams({
      ...tuningParams,
      [param]: numValue
    });
  };

  // Simuler une progression de flash
  const simulateFlashProgress = () => {
    setFlashProgress(0);
    setFlashStatus('flashing');
    
    let progress = 0;
    const interval = setInterval(() => {
      progress += 5;
      setFlashProgress(progress);
      
      if (progress >= 100) {
        clearInterval(interval);
        setFlashStatus('success');
      }
    }, 300);
    
    return () => clearInterval(interval);
  };

  // Flasher l'ECU avec les paramètres actuels
  const flashECU = async () => {
    if (!ecuConnected) {
      setError("Veuillez d'abord connecter l'ECU");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Démarrer la simulation de progression
      const clearSimulation = simulateFlashProgress();
      
      // Envoyer les paramètres au backend
      const response = await axios.post('/ecu_flash', tuningParams);
      
      if (response.data.success) {
        addToHistory(`Flash ECU réussi avec les paramètres : Injection ${tuningParams.cartographie_injection}%, Boost ${tuningParams.boost_turbo}`);
        // La progression sera à 100% grâce à la simulation
      } else {
        clearSimulation(); // Arrêter la simulation
        setFlashStatus('error');
        setError(response.data.message || "Erreur lors du flash de l'ECU");
        addToHistory('Échec du flash ECU');
      }
    } catch (err) {
      console.error("Erreur lors du flash de l'ECU:", err);
      setFlashStatus('error');
      setError("Une erreur s'est produite lors du flash de l'ECU.");
      addToHistory('Erreur technique lors du flash ECU');
    } finally {
      setLoading(false);
    }
  };

  // Ajouter un événement à l'historique
  const addToHistory = (event) => {
    const timestamp = new Date().toLocaleTimeString();
    setHistory(prev => [...prev, { time: timestamp, event }]);
  };

  // Paramètres de tuning avec leurs limites, unités et descriptions
  const tuningParamDetails = [
    {
      id: 'cartographie_injection',
      label: 'Cartographie d\'injection',
      unit: '%',
      description: 'Pourcentage par rapport à la cartographie d\'origine',
      min: 80,
      max: 130,
      step: 1
    },
    {
      id: 'boost_turbo',
      label: 'Boost turbo',
      unit: 'x',
      description: 'Multiplicateur de pression turbo',
      min: 0.8,
      max: 1.5,
      step: 0.05
    },
    {
      id: 'avance_allumage',
      label: 'Avance à l\'allumage',
      unit: '°',
      description: 'Réglage de l\'avance à l\'allumage',
      min: -5,
      max: 10,
      step: 1
    },
    {
      id: 'limiteur_regime',
      label: 'Limiteur de régime',
      unit: 'tr/min',
      description: 'Régime maximal du moteur',
      min: 5500,
      max: 8500,
      step: 100
    }
  ];

  return (
    <Container className="my-4">
      <h2 className="mb-4">Tuning et Flashage ECU</h2>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      {/* État de connexion */}
      <Card className="mb-4">
        <Card.Body className="text-center">
          <h4>État de connexion ECU</h4>
          <div className="mb-3">
            <div className={`ecu-status ${ecuConnected ? 'connected' : 'disconnected'}`} 
                 style={{ 
                   display: 'inline-block', 
                   width: '20px', 
                   height: '20px', 
                   borderRadius: '50%', 
                   backgroundColor: ecuConnected ? 'green' : 'red',
                   marginRight: '10px'
                 }}>
            </div>
            <span>{ecuConnected ? 'Connecté' : 'Déconnecté'}</span>
          </div>
          
          <Button 
            variant={ecuConnected ? "danger" : "success"} 
            onClick={ecuConnected ? disconnectECU : connectECU}
            disabled={loading}
            className="mb-3"
          >
            {loading && !flashStatus ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                En cours...
              </>
            ) : ecuConnected ? (
              <>Déconnecter</>
            ) : (
              <>Connecter à l'ECU</>
            )}
          </Button>
          
          {ecuConnected && (
            <div className="mt-2">
              <Button 
                variant="outline-primary" 
                onClick={readCurrentMap}
                disabled={loading || flashStatus === 'flashing'}
                className="ms-2"
              >
                Lire les paramètres actuels
              </Button>
            </div>
          )}
        </Card.Body>
      </Card>
      
      {/* Paramètres de tuning */}
      <Card className="mb-4">
        <Card.Header as="h5">Paramètres de tuning</Card.Header>
        <Card.Body>
          {tuningParamDetails.map((param) => (
            <Form.Group as={Row} className="mb-3" key={param.id}>
              <Form.Label column sm={4}>
                {param.label} ({param.unit})
              </Form.Label>
              <Col sm={5}>
                <Form.Range
                  value={tuningParams[param.id]}
                  min={param.min}
                  max={param.max}
                  step={param.step}
                  onChange={(e) => handleParamChange(param.id, e.target.value)}
                  disabled={!ecuConnected || loading || flashStatus === 'flashing'}
                />
              </Col>
              <Col sm={3}>
                <Form.Control
                  type="number"
                  value={tuningParams[param.id]}
                  min={param.min}
                  max={param.max}
                  step={param.step}
                  onChange={(e) => handleParamChange(param.id, e.target.value)}
                  disabled={!ecuConnected || loading || flashStatus === 'flashing'}
                />
              </Col>
              <Form.Text className="text-muted ms-3">{param.description}</Form.Text>
            </Form.Group>
          ))}
          
          <div className="d-grid mt-4">
            <Button 
              variant="warning" 
              size="lg"
              onClick={flashECU}
              disabled={!ecuConnected || loading || flashStatus === 'flashing'}
            >
              {flashStatus === 'flashing' ? (
                <>
                  <Spinner animation="border" size="sm" className="me-2" />
                  Flash en cours...
                </>
              ) : (
                'Flasher l\'ECU'
              )}
            </Button>
          </div>
          
          {/* Barre de progression du flash */}
          {flashStatus === 'flashing' && (
            <div className="mt-3">
              <ProgressBar 
                animated 
                now={flashProgress} 
                label={`${flashProgress}%`} 
                variant="info" 
              />
            </div>
          )}
          
          {flashStatus === 'success' && (
            <Alert variant="success" className="mt-3">
              Flashage réussi ! Les nouveaux paramètres ont été appliqués à l'ECU.
            </Alert>
          )}
          
          {flashStatus === 'error' && (
            <Alert variant="danger" className="mt-3">
              Erreur lors du flashage de l'ECU. Veuillez vérifier la connexion et réessayer.
            </Alert>
          )}
        </Card.Body>
      </Card>
      
      {/* Cartographie actuelle */}
      {currentMap && (
        <Card className="mb-4">
          <Card.Header as="h5">Cartographie actuelle</Card.Header>
          <Card.Body>
            <Table striped bordered hover>
              <thead>
                <tr>
                  <th>Paramètre</th>
                  <th>Valeur</th>
                  <th>Unité</th>
                </tr>
              </thead>
              <tbody>
                {currentMap.parameters && Object.entries(currentMap.parameters).map(([key, value]) => {
                  const paramDetail = tuningParamDetails.find(p => p.id === key);
                  return (
                    <tr key={key}>
                      <td>{paramDetail ? paramDetail.label : key}</td>
                      <td>{value}</td>
                      <td>{paramDetail ? paramDetail.unit : ''}</td>
                    </tr>
                  );
                })}
              </tbody>
            </Table>
            
            {/* Informations supplémentaires */}
            {currentMap.ecu_info && (
              <div className="mt-3">
                <h6>Informations ECU</h6>
                <p><strong>Modèle:</strong> {currentMap.ecu_info.model || 'N/A'}</p>
                <p><strong>Version:</strong> {currentMap.ecu_info.version || 'N/A'}</p>
                <p><strong>Compatibilité:</strong> {currentMap.ecu_info.compatibility || 'N/A'}</p>
              </div>
            )}
          </Card.Body>
        </Card>
      )}
      
      {/* Historique des opérations */}
      <Card>
        <Card.Header as="h5">Historique des opérations</Card.Header>
        <Card.Body style={{ maxHeight: '200px', overflowY: 'auto' }}>
          {history.length === 0 ? (
            <p className="text-muted">Aucune opération effectuée.</p>
          ) : (
            <ul className="list-unstyled">
              {history.map((item, index) => (
                <li key={index} className="mb-1">
                  <small className="text-muted">{item.time}</small> - {item.event}
                </li>
              ))}
            </ul>
          )}
        </Card.Body>
      </Card>
      
      {/* Avertissements */}
      <Alert variant="danger" className="mt-4">
        <h5>⚠️ Attention</h5>
        <p>
          La modification des paramètres de l'ECU peut entraîner des dommages irréversibles à votre moteur, 
          l'invalidation de votre garantie, et rendre votre véhicule non conforme aux réglementations en vigueur.
        </p>
        <p className="mb-0">
          Utilisez cette fonctionnalité à vos propres risques et uniquement si vous comprenez parfaitement 
          les conséquences de ces modifications.
        </p>
      </Alert>
    </Container>
  );
};

export default ECUFlash;