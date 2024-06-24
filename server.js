require('dotenv').config();
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

// Middleware untuk menyediakan variabel lingkungan ke frontend
app.use((req, res, next) => {
  res.locals.neo4jUri = process.env.NEO4J_URI;
  res.locals.neo4jUsername = process.env.NEO4J_USERNAME;
  res.locals.neo4jPassword = process.env.NEO4J_PASSWORD;
  next();
});

// Rute untuk menyajikan file HTML, CSS, dan JavaScript
app.use(express.static('app'));

app.get('/env', (req, res) => {
  res.json({
    NEO4J_URI: process.env.NEO4J_URI,
    NEO4J_USERNAME: process.env.NEO4J_USERNAME,
    NEO4J_PASSWORD: process.env.NEO4J_PASSWORD
  });
});

app.listen(port, () => {
  console.log(`App running at http://localhost:${port}`);
});