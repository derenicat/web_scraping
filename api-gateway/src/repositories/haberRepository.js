const Haber = require('../models/haberModel');

class HaberRepository {
    /**
     * Yeni bir haberi veya haber listesini veritabanına kaydeder.
     * Mükerrer kontrolü (URL bazlı) yapar.
     */
    async createOrUpdate(newsData) {
        // Her bir haber için URL üzerinden mükerrer kontrolü yap
        // Eğer varsa güncelle, yoksa yeni oluştur (upsert)
        const ops = newsData.map(news => ({
            updateOne: {
                filter: { 'sources.url': news.sources[0].url }, // İlk kaynak URL'i ile kontrol
                update: { $set: news },
                upsert: true
            }
        }));

        if (ops.length === 0) return { nUpserted: 0 };
        return await Haber.bulkWrite(ops);
    }

    /**
     * Tüm haberleri filtreli bir şekilde getirir.
     */
    async findAll(filters = {}) {
        const query = {};
        
        if (filters.category) query.category = filters.category;
        if (filters.startDate && filters.endDate) {
            query.publishedDate = {
                $gte: new Date(filters.startDate),
                $lte: new Date(filters.endDate)
            };
        }

        return await Haber.find(query).sort({ publishedDate: -1 });
    }

    /**
     * Belirli bir lokasyon metnine karşılık gelen koordinatları 
     * daha önce kaydedilmiş haberlerden bulur (Location Caching).
     */
    async findCoordinatesByAddress(addressText) {
        const result = await Haber.findOne({ 
            addressText: { $regex: new RegExp(`^${addressText}$`, 'i') },
            'location.coordinates': { $ne: [0, 0] }
        }).select('location');
        
        return result ? result.location.coordinates : null;
    }
}

module.exports = new HaberRepository();
