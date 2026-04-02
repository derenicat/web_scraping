const Haber = require('../models/haberModel');

class HaberRepository {
    /**
     * Haberleri toplu olarak (Bulk) kaydeder veya günceller.
     * URL bazlı mükerrer kontrolü yapar.
     */
    async bulkUpsert(newsList) {
        if (!newsList || newsList.length === 0) return { matchedCount: 0, upsertedCount: 0 };

        const operations = newsList.map(news => ({
            updateOne: {
                filter: { 'sources.url': news.sources[0].url }, // İlk kaynak URL'i ana anahtarımız
                update: { $set: news },
                upsert: true
            }
        }));

        return await Haber.bulkWrite(operations);
    }

    /**
     * Veritabanında daha önce bu adres metni için koordinat bulunmuş mu bakar.
     */
    async findCoordinatesByAddress(addressText) {
        // Tam eşleşme veya büyük/küçük harf duyarsız kontrol
        const result = await Haber.findOne({ 
            addressText: { $regex: new RegExp(`^${addressText}$`, 'i') },
            'location.coordinates': { $exists: true, $ne: [0, 0] }
        }).select('location');
        
        return result ? result.location.coordinates : null;
    }

    /**
     * Tüm haberleri filtreli (Kategori, Tarih) getirir.
     */
    async findAll(filters = {}) {
        const query = {};
        if (filters.category && filters.category !== 'Hepsi') query.category = filters.category;
        
        // Tarih filtresi: Son X gün (Saate göre dinamik pencere)
        if (filters.days) {
            const dateLimit = new Date();
            // 1 gün = 24 saat geriye git
            dateLimit.setHours(dateLimit.getHours() - (filters.days * 24));
            query.publishedDate = { $gte: dateLimit };
        }

        return await Haber.find(query).sort({ publishedDate: -1 });
    }
}

module.exports = new HaberRepository();
