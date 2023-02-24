import bodyParser from 'body-parser';
import express from 'express';
import fetch from 'node-fetch';
import path from 'path';

// Importer l'application express
const app = express();

const __dirname = path.resolve();

// Définition du répertoire statique
app.use(express.static(path.join(__dirname, 'public')));

// Middleware pour parser le corps des requêtes
app.use(bodyParser.urlencoded({ extended: true }));

// Route pour envoyer le message au chat bot
app.post('/send-message', async (req, res) => {
  const message = req.body.message;
  const url = 'http://127.0.0.1/predict';
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  const data = await response.json();
  res.send(data.response);
});

// Lancement du serveur
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});