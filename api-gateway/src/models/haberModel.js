const mongoose = require('mongoose');

const HaberSchema = new mongoose.Schema({
  title: { type: String, required: true },
  content: { type: String, required: true },
  category: { 
    type: String, 
    required: true,
    enum: ['Trafik Kazası', 'Yangın', 'Elektrik Kesintisi', 'Hırsızlık', 'Kültürel Etkinlikler']
  },
  publishedDate: { type: Date, required: true },
  addressText: { type: String, required: true },
  location: {
    type: { type: String, enum: ['Point'], default: 'Point' },
    coordinates: { type: [Number], required: true } // [lng, lat]
  },
  sources: [{
    siteName: { type: String, required: true },
    url: { type: String, required: true }
  }],
  embedding: { type: [Number], select: false },
  createdAt: { type: Date, default: Date.now }
});

// Coğrafi sorgular için index
HaberSchema.index({ location: '2dsphere' });

module.exports = mongoose.model('Haber', HaberSchema);
