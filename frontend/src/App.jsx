import React, { useState, useEffect, useCallback } from 'react';
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from '@react-google-maps/api';
import { RefreshCw, MapPin, Calendar, ExternalLink, Filter } from 'lucide-react';
import axios from 'axios';

const containerStyle = { width: '100%', height: '100vh' };
const center = { lat: 40.7654, lng: 29.9408 };

// Haber kategorilerine göre marker renkleri ve ikonları
const categoryConfig = {
  'Trafik Kazası': { color: '#ef4444', icon: '🚗' },
  'Yangın': { color: '#f97316', icon: '🔥' },
  'Elektrik Kesintisi': { color: '#eab308', icon: '⚡' },
  'Hırsızlık': { color: '#6366f1', icon: '👤' },
  'Kültürel Etkinlikler': { color: '#22c55e', icon: '🎭' },
  'Diğer': { color: '#94a3b8', icon: '📍' }
};

function App() {
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ""
  });

  const [news, setNews] = useState([]);
  const [selectedNews, setSelectedNews] = useState(null);
  const [selectedDays, setSelectedDays] = useState(3);
  const [loading, setLoading] = useState(false);
  const [filterCategory, setFilterCategory] = useState('Hepsi');

  // Haberleri backend'den çek
  const fetchNews = useCallback(async () => {
    try {
      const response = await axios.get(`/api/haberler?category=${filterCategory === 'Hepsi' ? '' : filterCategory}`);
      setNews(response.data);
    } catch (err) {
      console.error("Haberler yüklenirken hata:", err);
    }
  }, [filterCategory]);

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  // Yeni veri çekme tetikleyicisi
  const handleUpdate = async () => {
    setLoading(true);
    try {
      await axios.post('/api/haberler/scrape', { days: selectedDays });
      await fetchNews(); // Yeni verileri getir
      alert("Haberler başarıyla güncellendi!");
    } catch (err) {
      console.error("Güncelleme hatası:", err);
      alert("Güncelleme sırasında bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  };

  return isLoaded ? (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'sans-serif' }}>
      {/* Yan Panel */}
      <aside style={{ width: '380px', padding: '24px', background: '#ffffff', borderRight: '1px solid #e2e8f0', overflowY: 'auto' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1e293b', marginBottom: '8px' }}>Kocaeli Haber Haritası</h1>
        <p style={{ color: '#64748b', fontSize: '0.9rem', marginBottom: '24px' }}>Şehirdeki olayları canlı izleyin.</p>
        
        <div style={{ marginBottom: '24px', padding: '16px', background: '#f1f5f9', borderRadius: '8px' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px' }}>Veri Kaynağı:</label>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
            <select 
              value={selectedDays} 
              onChange={(e) => setSelectedDays(Number(e.target.value))}
              style={{ flex: 1, padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
            >
              <option value={1}>Son 1 Gün</option>
              <option value={2}>Son 2 Gün</option>
              <option value={3}>Son 3 Gün</option>
            </select>
            <button 
              onClick={handleUpdate}
              disabled={loading}
              style={{ 
                padding: '10px 16px', background: '#2563eb', color: 'white', 
                border: 'none', borderRadius: '6px', cursor: 'pointer', transition: 'all 0.2s'
              }}
            >
              <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
            </button>
          </div>

          <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px' }}>Filtrele:</label>
          <select 
            value={filterCategory} 
            onChange={(e) => setFilterCategory(e.target.value)}
            style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
          >
            <option value="Hepsi">Tüm Kategoriler</option>
            {Object.keys(categoryConfig).map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div style={{ marginTop: '24px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '16px' }}>Son Haberler ({news.length})</h3>
          {news.map((item) => (
            <div 
              key={item._id} 
              onClick={() => setSelectedNews(item)}
              style={{ 
                padding: '12px', borderBottom: '1px solid #f1f5f9', cursor: 'pointer',
                background: selectedNews?._id === item._id ? '#eff6ff' : 'transparent',
                borderRadius: '6px', transition: 'background 0.2s'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span style={{ fontSize: '1.2rem' }}>{categoryConfig[item.category]?.icon || '📍'}</span>
                <span style={{ fontSize: '0.75rem', fontWeight: '600', color: categoryConfig[item.category]?.color }}>
                  {item.category.toUpperCase()}
                </span>
              </div>
              <div style={{ fontWeight: '600', fontSize: '0.95rem', color: '#1e293b' }}>{item.title}</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '4px' }}>
                {new Date(item.publishedDate).toLocaleDateString('tr-TR')} - {item.addressText}
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* Harita Alanı */}
      <main style={{ flex: 1, position: 'relative' }}>
        <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={11}>
          {news.map((item) => (
            <Marker
              key={item._id}
              position={{ 
                lat: item.location.coordinates[1], 
                lng: item.location.coordinates[0] 
              }}
              onClick={() => setSelectedNews(item)}
              icon={{
                path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z",
                fillColor: categoryConfig[item.category]?.color || '#94a3b8',
                fillOpacity: 1,
                strokeWeight: 1,
                strokeColor: '#ffffff',
                scale: 1.5,
                anchor: new window.google.maps.Point(12, 22)
              }}
            />
          ))}

          {selectedNews && (
            <InfoWindow
              position={{ 
                lat: selectedNews.location.coordinates[1], 
                lng: selectedNews.location.coordinates[0] 
              }}
              onCloseClick={() => setSelectedNews(null)}
            >
              <div style={{ maxWidth: '250px', padding: '8px' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '1rem' }}>{selectedNews.title}</h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: '#666', marginBottom: '8px' }}>
                  <Calendar size={14} />
                  {new Date(selectedNews.publishedDate).toLocaleString('tr-TR')}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: '#666', marginBottom: '12px' }}>
                  <MapPin size={14} />
                  {selectedNews.addressText}
                </div>
                <div style={{ borderTop: '1px solid #eee', paddingTop: '8px' }}>
                  <p style={{ fontSize: '0.85rem', margin: '0 0 12px 0', color: '#333' }}>
                    {selectedNews.content.substring(0, 100)}...
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {selectedNews.sources.map((src, idx) => (
                      <a 
                        key={idx} 
                        href={src.url} 
                        target="_blank" 
                        rel="noreferrer"
                        style={{ 
                          display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', 
                          padding: '4px 8px', background: '#f1f5f9', borderRadius: '4px', textDecoration: 'none', color: '#2563eb'
                        }}
                      >
                        <ExternalLink size={12} />
                        {src.siteName}
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            </InfoWindow>
          )}
        </GoogleMap>
      </main>
      
      <style>{`
        .animate-spin { animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .gm-style-iw { padding: 0 !important; }
      `}</style>
    </div>
  ) : <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center' }}>Harita Yükleniyor...</div>;
}

export default App;
