const axios = require('axios');
const HaberRepository = require('../repositories/haberRepository');
require('dotenv').config();

class HaberService {
    constructor() {
        this.workerUrl = process.env.PYTHON_WORKER_URL || 'http://localhost:8000';
        this.googleApiKey = process.env.GOOGLE_MAPS_API_KEY;
    }

    /**
     * Python Worker'ı tetikleyerek haber çekme sürecini başlatır.
     */
    async triggerScrape(days) {
        try {
            console.log(`[Service] Python Worker tetikleniyor: ${days} gün...`);
            const response = await axios.post(`${this.workerUrl}/process-news?days=${days}`);
            
            if (response.data.status === 'success') {
                const rawNews = response.data.results;
                console.log(`[Service] ${rawNews.length} adet ham haber geldi. Geocoding başlıyor...`);
                
                // Her haber için koordinat tespiti yap
                const processedNews = await Promise.all(rawNews.map(async (news) => {
                    const coords = await this.getCoordinates(news.addressText);
                    return {
                        ...news,
                        location: {
                            type: 'Point',
                            coordinates: coords || [29.9408, 40.7654] // Bulunamazsa Kocaeli Merkez (Fallback)
                        }
                    };
                }));

                // Veritabanına kaydet (Repository Pattern)
                const result = await HaberRepository.createOrUpdate(processedNews);
                return { success: true, count: rawNews.length, dbResult: result };
            }
            
            throw new Error('Python Worker hata döndü.');
        } catch (error) {
            console.error('[Service Error] Scraping hatası:', error.message);
            throw error;
        }
    }

    /**
     * Adres metnini koordinatlara çevirir. 
     * Önce DB Cache'e bakar, yoksa Google Maps'e gider.
     */
    async getCoordinates(addressText) {
        if (!addressText || addressText === "Kocaeli") return [29.9408, 40.7654];

        // 1. Önce DB'den kontrol et (Location Caching)
        const cachedCoords = await HaberRepository.findCoordinatesByAddress(addressText);
        if (cachedCoords) {
            console.log(`[Cache Hit] ${addressText} için koordinatlar DB'den alındı.`);
            return cachedCoords;
        }

        // 2. DB'de yoksa Google Geocoding API'ye git
        try {
            console.log(`[Geocoding API] ${addressText} için Google'a soruluyor...`);
            const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(addressText + ', Kocaeli')}&key=${this.googleApiKey}`;
            const response = await axios.get(url);

            if (response.data.results && response.data.results.length > 0) {
                const { lng, lat } = response.data.results[0].geometry.location;
                return [lng, lat];
            }
        } catch (error) {
            console.error('[Geocoding Error]:', error.message);
        }

        return null;
    }

    /**
     * Haberleri listeleme mantığı.
     */
    async getAllNews(filters) {
        return await HaberRepository.findAll(filters);
    }
}

module.exports = new HaberService();
