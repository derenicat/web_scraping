import React, { useState, useEffect, useCallback } from 'react';
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from '@react-google-maps/api';
import { RefreshCw, MapPin, Calendar, ExternalLink, Filter, Clock } from 'lucide-react';
import axios from 'axios';

const containerStyle = { width: '100%', height: '100vh' };
const center = { lat: 40.7654, lng: 29.9408 };

const categoryConfig = {
  'Cinayet': { color: 'purple', icon: '💀', hex: '#a855f7' },
  'Yangın': { color: 'orange', icon: '🔥', hex: '#f97316' },
  'Trafik Kazası': { color: 'red', icon: '🚗', hex: '#ef4444' },
  'Elektrik Kesintisi': { color: 'yellow', icon: '⚡', hex: '#eab308' },
  'Hırsızlık': { color: 'blue', icon: '👤', hex: '#3b82f6' },
  'Kültürel Etkinlikler': { color: 'green', icon: '🎭', hex: '#22c55e' },
  'Diğer': { color: 'pink', icon: '📍', hex: '#ec4899' }
};

function App() {
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ""
  });

  const [news, setNews] = useState([]);
  const [selectedNews, setSelectedNews] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filterCategory, setFilterCategory] = useState('Hepsi');
  const [daysFilter, setDaysFilter] = useState(3); // Yeni Tarih Filtresi State'i

  const fetchNews = useCallback(async () => {
    try {
      const response = await axios.get(`/api/haberler?category=${filterCategory === 'Hepsi' ? '' : filterCategory}&days=${daysFilter}`);
      setNews(response.data);
    } catch (err) {
      console.error("Haberler yüklenirken hata:", err);
    }
  }, [filterCategory, daysFilter]);

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  const handleUpdate = async () => {
    setLoading(true);
    try {
      await axios.post('/api/haberler/scrape', { days: 3 });
      await fetchNews();
      alert("Harita verileri güncellendi!");
    } catch (err) {
      alert("Hata oluştu.");
    } finally {
      setLoading(false);
    }
  };

  return isLoaded ? (
    <div style={{ display: 'flex', height: '100vh', fontFamily: "system-ui, -apple-system, sans-serif", background: '#f8fafc' }}>
      {/* Sidebar */}
      <aside style={{ width: '400px', padding: '20px', background: 'white', borderRight: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: '20px' }}>
          <h1 style={{ fontSize: '1.4rem', fontWeight: '800', color: '#0f172a' }}>Kocaeli Haber Haritası</h1>
          <p style={{ color: '#64748b', fontSize: '0.85rem' }}>Canlı Asayiş ve Gündem Takibi</p>
        </div>

        <div style={{ background: '#f1f5f9', padding: '15px', borderRadius: '12px', marginBottom: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <span style={{ fontWeight: '700', fontSize: '0.9rem' }}>Veri Kaynaklarını Tara</span>
            <button 
              onClick={handleUpdate} 
              disabled={loading}
              style={{ padding: '8px 12px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
              {loading ? 'Yükleniyor' : 'Güncelle'}
            </button>
          </div>

          {/* Tarih Slider Filtresi */}
          <div style={{ marginBottom: '15px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#475569', display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Clock size={14} /> Zaman Aralığı
              </label>
              <span style={{ fontSize: '0.85rem', fontWeight: '800', color: '#2563eb' }}>Son {daysFilter} Gün</span>
            </div>
            <input 
              type="range" min="1" max="3" step="1"
              value={daysFilter}
              onChange={(e) => setDaysFilter(parseInt(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', accentColor: '#2563eb' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#94a3b8', marginTop: '4px' }}>
              <span>24 Saat</span>
              <span>48 Saat</span>
              <span>72 Saat</span>
            </div>
          </div>
          
          <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '15px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#475569', display: 'block', marginBottom: '8px' }}>Kategori Filtrele</label>
            <select 
              value={filterCategory} 
              onChange={(e) => setFilterCategory(e.target.value)}
              style={{ width: '100%', padding: '8px', borderRadius: '8px', border: '1px solid #cbd5e1' }}
            >
              <option value="Hepsi">Tüm Kategoriler</option>
              {Object.keys(categoryConfig).map(cat => <option key={cat} value={cat}>{cat}</option>)}
            </select>
          </div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto' }}>
          <h3 style={{ fontSize: '0.8rem', fontWeight: '800', color: '#94a3b8', marginBottom: '12px', letterSpacing: '0.05em' }}>LISTELENEN HABERLER ({news.length})</h3>
          {news.map((item) => (
            <div 
              key={item._id} 
              onClick={() => setSelectedNews(item)}
              style={{ 
                padding: '12px', marginBottom: '10px', borderRadius: '10px', cursor: 'pointer', border: '1px solid #f1f5f9',
                background: selectedNews?._id === item._id ? '#eff6ff' : 'white'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '0.7rem', fontWeight: '800', color: categoryConfig[item.category]?.hex }}>
                  {categoryConfig[item.category]?.icon} {item.category.toUpperCase()}
                </span>
                <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>{new Date(item.publishedDate).toLocaleDateString('tr-TR')}</span>
              </div>
              <div style={{ fontWeight: '600', fontSize: '0.9rem', color: '#1e293b' }}>{item.title}</div>
            </div>
          ))}
        </div>
      </aside>

      {/* Harita */}
      <main style={{ flex: 1 }}>
        <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={11}>
          {news.map((item) => (
            <Marker
              key={item._id}
              position={{ lat: item.location.coordinates[1], lng: item.location.coordinates[0] }}
              onClick={() => setSelectedNews(item)}
              icon={`http://maps.google.com/mapfiles/ms/icons/${categoryConfig[item.category]?.color || 'red'}-dot.png`}
            />
          ))}

          {selectedNews && (
            <InfoWindow
              position={{ lat: selectedNews.location.coordinates[1], lng: selectedNews.location.coordinates[0] }}
              onCloseClick={() => setSelectedNews(null)}
            >
              <div style={{ maxWidth: '280px', padding: '5px' }}>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '1rem' }}>{selectedNews.title}</h4>
                <div style={{ fontSize: '0.8rem', color: '#666', marginBottom: '8px' }}>
                  <div>📅 {new Date(selectedNews.publishedDate).toLocaleString('tr-TR')}</div>
                  <div>📍 {selectedNews.addressText}</div>
                </div>
                <p style={{ fontSize: '0.85rem', margin: '0 0 10px 0' }}>{selectedNews.content.substring(0, 120)}...</p>
                <div style={{ borderTop: '1px solid #eee', paddingTop: '8px' }}>
                  <span style={{ fontSize: '0.7rem', fontWeight: 'bold', display: 'block', marginBottom: '5px' }}>KAYNAKLAR:</span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                    {selectedNews.sources.map((src, idx) => (
                      <a key={idx} href={src.url} target="_blank" rel="noreferrer" style={{ fontSize: '0.7rem', color: '#2563eb', textDecoration: 'none', background: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>
                        🔗 {src.siteName}
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
      `}</style>
    </div>
  ) : <div>Yükleniyor...</div>;
}

export default App;
