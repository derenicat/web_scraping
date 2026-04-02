const HaberService = require('../services/haberService');

class HaberController {
    /**
     * Haberleri çekme ve işleme sürecini başlatır (Trigger).
     */
    async scrapeNews(req, res) {
        try {
            const { days } = req.body;
            const result = await HaberService.triggerScrape(days || 3);
            res.status(200).json(result);
        } catch (error) {
            res.status(500).json({ error: 'Scraping süreci başlatılamadı.', message: error.message });
        }
    }

    /**
     * Harita üzerinde gösterilecek tüm haberleri getirir.
     */
    async listNews(req, res) {
        try {
            const filters = {
                category: req.query.category,
                startDate: req.query.startDate,
                endDate: req.query.endDate
            };
            const news = await HaberService.getAllNews(filters);
            res.status(200).json(news);
        } catch (error) {
            res.status(500).json({ error: 'Haberler listelenemedi.', message: error.message });
        }
    }
}

module.exports = new HaberController();
