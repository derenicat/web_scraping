const app = require('./app');
const connectDB = require('./config/db');
require('dotenv').config();

const PORT = process.env.PORT || 5000;

// Veritabanına Bağlan
connectDB();

// Sunucuyu Başlat
app.listen(PORT, () => {
  console.log(`API Gateway ${PORT} portunda çalışıyor... 🚀`);
});
