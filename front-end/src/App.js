import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

const socket = io('http://localhost:5000', {
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
});

function App() {
  const [apiStats, setApiStats] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [mode, setMode] = useState('kafka');
  
  // Couleurs pour les graphiques
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  useEffect(() => {
    console.log('[INIT] Démarrage du composant');

    // Charger les données initiales
    const fetchInitialData = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/data');
        const data = await response.json();
        
        // Formater les données API
        const formattedApiStats = Object.entries(data.api_stats).map(([api, stats]) => ({
          api,
          avg: stats.avg,
          min: stats.min,
          max: stats.max
        }));
        setApiStats(formattedApiStats);
      } catch (error) {
        console.error('Erreur lors du chargement des données initiales:', error);
      }
    };

    fetchInitialData();

    // Vérifier le mode de fonctionnement
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/health');
        const data = await response.json();
        setMode(data.mode);
      } catch (error) {
        console.error('Erreur lors de la vérification du mode:', error);
      }
    };

    checkHealth();

    // Écouteurs d'événements Socket.IO
    const onConnect = () => {
      console.log('[SOCKET] Connecté au serveur');
      setIsConnected(true);
    };

    const onDisconnect = () => {
      console.log('[SOCKET] Déconnecté du serveur');
      setIsConnected(false);
    };

    const onApiUpdate = (data) => {
      console.log('[DATA] Reçu API Update:', data);
      setLastUpdate(new Date());
      
      setApiStats(prev => {
        const existingIndex = prev.findIndex(item => item.api === data.endpoint);
        if (existingIndex >= 0) {
          const updated = [...prev];
          updated[existingIndex] = {
            ...updated[existingIndex],
            avg: data.stats.avg,
            min: data.stats.min,
            max: data.stats.max
          };
          return updated;
        }
        return [...prev, {
          api: data.endpoint,
          avg: data.stats.avg,
          min: data.stats.min,
          max: data.stats.max
        }];
      });
    };

    // Configuration des écouteurs
    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('api_update', onApiUpdate);

    // Nettoyage
    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('api_update', onApiUpdate);
    };
  }, []);

  // Formater les nombres
  const formatNumber = (num) => {
    const number = parseFloat(num);
    return isNaN(number) ? 'N/A' : number % 1 === 0 ? number : number.toFixed(2);
  };

  // Extraire le nom de l'API (sans la méthode HTTP)
  const getApiName = (apiPath) => {
    return apiPath.split(' ')[1] || apiPath;
  };

  return (
    <div className="dashboard">
      <header>
        <h1>API Performance Dashboard</h1>
        <div className="connection-info">
          <div className={`status ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? 'CONNECTÉ' : 'DÉCONNECTÉ'}
          </div>
          <div className={`mode ${mode}`}>
            Mode: {mode === 'kafka' ? 'Kafka (temps réel)' : 'Aléatoire'}
          </div>
          {lastUpdate && (
            <div className="last-update">
              Dernière mise à jour: {lastUpdate.toLocaleTimeString()}
            </div>
          )}
        </div>
      </header>

      <div className="dashboard-content">
        <div className="api-table-container">
          <h2>API Response Times</h2>
          <table className="api-table">
            <thead>
              <tr>
                <th>API Endpoint</th>
                <th>Average (ms)</th>
                <th>Minimum (ms)</th>
                <th>Maximum (ms)</th>
              </tr>
            </thead>
            <tbody>
              {apiStats.map((stat, index) => (
                <tr key={index}>
                  <td>{getApiName(stat.api)}</td>
                  <td>{formatNumber(stat.avg)}</td>
                  <td>{formatNumber(stat.min)}</td>
                  <td>{formatNumber(stat.max)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="api-charts">
          <div className="chart-container">
            <h3>Average Response Times</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={apiStats}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="api" tickFormatter={getApiName} />
                <YAxis />
                <Tooltip formatter={(value) => [value, 'ms']} />
                <Legend />
                <Bar dataKey="avg" name="Average (ms)" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-container">
            <h3>Response Time Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={apiStats}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="api" tickFormatter={getApiName} />
                <YAxis />
                <Tooltip formatter={(value) => [value, 'ms']} />
                <Legend />
                <Bar dataKey="min" name="Min (ms)" fill="#82ca9d" />
                <Bar dataKey="max" name="Max (ms)" fill="#ff8042" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-container">
            <h3>API Call Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={apiStats}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="avg"
                  nameKey="api"
                  label={({ api, percent }) => `${getApiName(api)} ${(percent * 100).toFixed(1)}%`}
                >
                  {apiStats.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [value, 'ms']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;