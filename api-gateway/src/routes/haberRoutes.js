const express = require('express');
const router = express.Router();
const HaberController = require('../controllers/haberController');

// Haberleri Çek (Trigger) - POST /api/haberler/scrape
router.post('/scrape', (req, res) => HaberController.scrapeNews(req, res));

// Haberleri Listele - GET /api/haberler
router.get('/', (req, res) => HaberController.listNews(req, res));

module.exports = router;
