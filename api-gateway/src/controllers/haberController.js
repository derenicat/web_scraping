const haberService = require('../services/haberService');

class HaberController {
    /**
     * Haberleri çekme ve işleme sürecini başlatır (Trigger).
     */
    async scrapeNews(req, res) {
        try {
            const { days } = req.body;
            // PDF isteri: Son 3 günlük zaman dilimine göre veri çekilmelidir.
            const result = await haberService.triggerScrapeAndProcess(days || 3);
            res.status(200).json(result);
        } catch (error) {
            res.status(500).json({ 
                error: 'Scraping ve entegrasyon süreci başarısız.', 
                message: error.message 
            });
        }
    }

    /**
     * Veritabanındaki tüm haberleri getirir.
     */
    async listNews(req, res) {
        try {
            const filters = {
                category: req.query.category,
                days: req.query.days ? parseInt(req.query.days) : null
            };
            const news = await haberService.listAllNews(filters);
            res.status(200).json(news);
        } catch (error) {
            res.status(500).json({ error: 'Haber listeleme hatası.', message: error.message });
        }
    }
}

module.exports = new HaberController();
