import React, { useState, useEffect } from 'react';
import { Container, Card, Button, Row, Col, Alert, Spinner, Table } from 'react-bootstrap';
import axios from 'axios';

const OBD2Dashboard = () => {
  const [vehicleData, setVehicleData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [connected, setConnected] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(null);

  // Fonction pour récupérer les données OBD2
  const fetchOBD2Data = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('/obd2');
      setVehicleData(response.data);
      
      // Si la connexion est établie
      if (!response.data.error) {
        setConnected(true);
      } else {
        setConnected(false);
        setError(response.data.error);
      }
    } catch (err) {
      console.error("Erreur lors de la récupération des données OBD-II:", err);
      setError("Impossible de récupérer les données du véhicule. Vérifiez que le dongle OBD-II est correctement connecté.");
      setConnected(false);
    } finally {
      setLoading(false);
    }
  };

  // Gérer la connexion/déconnexion
  const toggleConnection = () => {
    if (!connected) {
      // Se connecter
      fetchOBD2Data();
      // Mettre en place un rafraîchissement périodique (toutes les 3 secondes)
      const interval = setInterval(fetchOBD2Data, 3000);
      setRefreshInterval(interval);
    } else {
      // Se déconnecter: arrêter le rafraîchissement
      if (refreshInterval) {
        clearInterval(refreshInterval);
        setRefreshInterval(null);
      }
      setConnected(false);
      setVehicleData(null);
    }
  };

  // Nettoyage lors du démontage du composant
  useEffect(() => {
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [refreshInterval]);

  // Rendre les données du véhicule
  const renderVehicleData = () => {
    if (!vehicleData) return null;

    return (
      <Card className="mt-3">
        <Card.Header as="h5">Données du véhicule</Card.Header>
        <Card.Body>
          <Row>
            <Col>
              <div className="mb-4">
                <h3 className="text-center mb-3">Paramètres moteur</h3>
                <Table striped bordered hover>
                  <tbody>
                    <tr>
                      <td><strong>Régime moteur (RPM)</strong></td>
                      <td>{vehicleData.RPM || "N/A"}</td>
                    </tr>
                    <tr>
                      <td><strong>Vitesse</strong></td>
                      <td>{vehicleData.Speed ? `${vehicleData.Speed} km/h` : "N/A"}</td>
                    </tr>
                    <tr>
                      <td><strong>Température du moteur</strong></td>
                      <td>{vehicleData.EngineTemp ? `${vehicleData.EngineTemp}°C` : "N/A"}</td>
                    </tr>
                    <tr>
                      <td><strong>Charge moteur</strong></td>
                      <td>{vehicleData.EngineLoad ? `${vehicleData.EngineLoad}%` : "N/A"}</td>
                    </tr>
                  </tbody>
                </Table>
              </div>
            </Col>
          </Row>
          
          {/* Codes d'erreur */}
          <Row className="mt-2">
            <Col>
              <h3 className="text-center mb-3">Codes d'erreur (DTC)</h3>
              {vehicleData.DTC && vehicleData.DTC !== "Aucun code détecté" ? (
                <Alert variant="warning">
                  <h5>Codes détectés :</h5>
                  <ul>
                    {Array.isArray(vehicleData.DTC) ? 
                      vehicleData.DTC.map((code, index) => (
                        <li key={index}>{code}</li>
                      )) : 
                      <li>{vehicleData.DTC}</li>
                    }
                  </ul>
                </Alert>
              ) : (
                <Alert variant="success">
                  Aucun code d'erreur détecté
                </Alert>
              )}
            </Col>
          </Row>
        </Card.Body>
      </Card>
    );
  };

  return (
    <Container className="my-4">
      <h2 className="mb-4">Diagnostic OBD-II</h2>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Card>
        <Card.Body className="text-center">
          <h4>État de la connexion OBD-II</h4>
          <div className="mb-3">
            <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`} 
                 style={{ 
                   display: 'inline-block', 
                   width: '20px', 
                   height: '20px', 
                   borderRadius: '50%', 
                   backgroundColor: connected ? 'green' : 'red',
                   marginRight: '10px'
                 }}>
            </div>
            <span>{connected ? 'Connecté' : 'Déconnecté'}</span>
          </div>
          
          <Button 
            variant={connected ? "danger" : "success"} 
            onClick={toggleConnection}
            disabled={loading}
          >
            {loading ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                En cours...
              </>
            ) : connected ? (
              <>Déconnecter</>
            ) : (
              <>Connecter au véhicule</>
            )}
          </Button>
        </Card.Body>
      </Card>
      
      {/* Affichage des données du véhicule */}
      {connected && renderVehicleData()}
      
      {/* Conseils d'utilisation */}
      <Card className="mt-4">
        <Card.Header>Conseils d'utilisation</Card.Header>
        <Card.Body>
          <ul>
            <li>Assurez-vous que le dongle OBD-II est correctement branché sur le port de diagnostic</li>
            <li>Le moteur doit être démarré pour certaines données (régime moteur, vitesse, etc.)</li>
            <li>Certains véhicules peuvent nécessiter un adaptateur spécifique</li>
            <li>Les codes d'erreur peuvent être recherchés dans la section NLP pour plus de détails</li>
          </ul>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default OBD2Dashboard;