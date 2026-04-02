const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
const haberRoutes = require('./routes/haberRoutes');
app.use('/api/haberler', haberRoutes);

// Health Check
app.get('/health', (req, res) => {
  res.json({ status: 'UP', service: 'API Gateway' });
});

module.exports = app;
