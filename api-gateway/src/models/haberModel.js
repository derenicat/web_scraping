const mongoose = require('mongoose');

const haberSchema = new mongoose.Schema({
    title: { type: String, required: true },
    content: { type: String, required: true },
    category: { 
        type: String, 
        required: true,
        enum: ['Trafik Kazası', 'Yangın', 'Elektrik Kesintisi', 'Hırsızlık', 'Kültürel Etkinlikler', 'Cinayet', 'Diğer']
    },
    publishedDate: { type: Date, required: true },
    addressText: { type: String, required: true },
    location: {
        type: { type: String, default: 'Point' },
        coordinates: { type: [Number], index: '2dsphere' } // [longitude, latitude]
    },
    sources: [{
        siteName: String,
        url: String
    }],
    createdAt: { type: Date, default: Date.now }
});

// Aynı URL'in tekrar kaydedilmesini önlemek için kaynak URL bazlı indeks (İsteğe bağlı ek güvenlik)
haberSchema.index({ "sources.url": 1 });

module.exports = mongoose.model('Haber', haberSchema);
