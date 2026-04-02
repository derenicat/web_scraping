const axios = require('axios');
const haberRepository = require('../repositories/haberRepository');
require('dotenv').config();

class HaberService {
    constructor() {
        this.workerUrl = process.env.PYTHON_WORKER_URL || 'http://localhost:8001';
        this.googleApiKey = process.env.GOOGLE_MAPS_API_KEY;
    }

    /**
     * Python Worker'ı tetikler ve gelen verileri işleyip DB'ye kaydeder.
     */
    async triggerScrapeAndProcess(days) {
        try {
            console.log(`[HaberService] Python Worker tetikleniyor: ${days} gün...`);
            const response = await axios.post(`${this.workerUrl}/process-news?days=${days}`);
            
            if (response.data.status === 'success') {
                const newsList = response.data.results;
                console.log(`[HaberService] ${newsList.length} adet olay geldi. Geocoding süreci başlıyor...`);
                
                const processedNews = [];
                
                for (const news of newsList) {
                    const coords = await this.getCoordinates(news.addressText);
                    
                    // Eğer konum bulunamazsa PDF isteri gereği haberi haritada göstermeyeceğiz (kaydetmeyeceğiz).
                    if (coords) {
                        processedNews.push({
                            ...news,
                            location: {
                                type: 'Point',
                                coordinates: coords // [lng, lat]
                            }
                        });
                    }
                }

                // Toplu kayıt (Repository üzerinden)
                const result = await haberRepository.bulkUpsert(processedNews);
                console.log(`[HaberService] İşlem tamamlandı. DB Sonucu: ${result.upsertedCount} yeni, ${result.matchedCount} güncellenen.`);
                
                return { success: true, count: processedNews.length, db: result };
            }
            throw new Error('Python Worker servisi hata döndü.');
        } catch (error) {
            console.error('[HaberService Hata]:', error.message);
            throw error;
        }
    }

    /**
     * Adres metnini koordinata çevirir (With Caching).
     */
    async getCoordinates(addressText) {
        if (!addressText) return null;

        // 1. Kocaeli Merkez Sabiti
        if (addressText.toLowerCase() === "kocaeli") return [29.9408, 40.7654];

        // 2. DB Cache Kontrolü
        const cached = await haberRepository.findCoordinatesByAddress(addressText);
        if (cached) {
            console.log(`   [GeoCache Hit] ${addressText}`);
            return cached;
        }

        // 3. Google Geocoding API
        try {
            console.log(`   [GeoAPI Call] ${addressText} için Google'a soruluyor...`);
            const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(addressText + ', Kocaeli')}&key=${this.googleApiKey}`;
            const response = await axios.get(url);

            if (response.data.results && response.data.results.length > 0) {
                const { lng, lat } = response.data.results[0].geometry.location;
                return [lng, lat];
            }
        } catch (error) {
            console.error(`   [GeoAPI Hata] ${addressText}:`, error.message);
        }

        return null;
    }

    /**
     * Haberleri filtreli getirir.
     */
    async listAllNews(filters) {
        return await haberRepository.findAll(filters);
    }
}

module.exports = new HaberService();
