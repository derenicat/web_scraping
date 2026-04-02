# Kentsel Haber İzleme Sistemi - Polyglot Microservices Yol Haritası

Bu proje, Node.js (API Gateway) ve Python (NLP Worker) servislerinden oluşan, Repository Pattern tabanlı bir mikroservis mimarisidir.

## 1. Mimari Katmanlar

### A. API Gateway & Management (Node.js + Express)
- **Görev:** Frontend iletişimi, Kullanıcı yönetimi, MongoDB veri kalıcılığı (Persistence).
- **Mimari:** Repository Pattern.
    - `Controller`: API uç noktaları.
    - `Service`: Python servisiyle iletişim (Axios) ve iş mantığı.
    - `Repository`: Mongoose ile MongoDB soyutlama katmanı.
    - `Model`: Haber ve Konum şemaları.

### B. NLP & Scraping Worker (Python + FastAPI)
- **Görev:** Yoğun hesaplama gerektiren işlemler (Scraping, NLP, Embedding).
- **Süreçler:**
    - `Scrapers`: 5 yerel site için özelleşmiş modüller.
    - `NLP Engine`: spaCy/nltk ile metin temizleme ve konum tespiti.
    - `Similarity Engine`: `sentence-transformers` ile %90 benzerlik kontrolü.
    - `Classifier`: Anahtar kelime tabanlı kategori belirleme.

---

## 2. Teknoloji Yığını (Tech Stack)

| Bileşen | Teknoloji | Neden? |
| :--- | :--- | :--- |
| **Main API** | Node.js (JavaScript) | Hızlı I/O ve asenkron yönetim. |
| **Worker API** | Python + FastAPI | NLP kütüphaneleri ve yüksek performanslı Python API. |
| **Veritabanı** | MongoDB (**Zorunlu**) | Mongoose kütüphanesi ile şema yönetimi. |
| **Scraping** | Axios + Cheerio / Puppeteer | Hızlı ve güvenilir veri çekimi. |
| **NLP / Embedding** | Sentence-Transformers | %90 benzerlik doğruluğu için endüstri standardı. |
| **Frontend** | React.js (JavaScript) | Dinamik harita ve filtreleme UI. |
| **Harita** | Google Maps JS API | Proje isterlerini karşılayan GIS servisi. |

---

## 3. Uygulama Planı (To-Do List)

### Faz 1: Altyapı ve İletişim Protokolü
- [ ] Klasör yapısının kurulması (`/api-gateway`, `/worker-service`, `/frontend`).
- [ ] Node.js ve Python servisleri arasında temel "Health Check" iletişiminin kurulması.
- [ ] MongoDB bağlantısının Node.js tarafında (Mongoose) yapılandırılması.

### Faz 2: Python Worker - Veri İşleme Hattı
- [ ] 5 haber sitesi için scraper modüllerinin yazılması.
- [ ] `sentence-transformers` entegrasyonu ile içerik benzerliği analizi.
- [ ] Metinden mahalle/sokak çıkaran konum tespiti algoritmasının geliştirilmesi.
- [ ] FastAPI üzerinden `/process-news?days=3` uç noktasının hazırlanması.

### Faz 3: Node.js API - Repository Pattern
- [ ] `HaberRepository` ve `KonumRepository` sınıflarının yazılması.
- [ ] Python servisinden gelen JSON verisini doğrulayıp DB'ye kaydeden servis katmanı.
- [ ] Google Geocoding API entegrasyonu ve koordinatların saklanması.
- [ ] **Maliyet Kontrolü:** Daha önce işlenmiş adreslerin koordinatlarını DB'den getiren cache mantığı.

### Faz 4: Frontend ve Görselleştirme
- [ ] Google Maps üzerinde haber türüne göre marker render edilmesi.
- [ ] "Verileri Güncelle" tetikleyicisi ve Loading durumlarının yönetimi.
- [ ] Filtreleme (Tür, İlçe, Tarih) arayüzünün tamamlanması.

---

## 4. Kritik Başarı Faktörleri ve Sorular

1. **Transaction Yönetimi:** Python servisi veri dönerken hata alırsa, Node.js tarafında DB tutarlılığını nasıl sağlarsın?
2. **Geocoding Optimizasyonu:** Bir sokak ismi için Google API'ye gitmeden önce DB'de "Bu sokak Kocaeli'nin hangi koordinatındaydı?" sorgusunu nasıl kurgulayacaksın?
3. **Senaryo Analizi:** Aynı haberi iki farklı site paylaştığında (Similarity > 0.90), haritadaki marker penceresinde iki kaynağın da linkini göstermeyi unutma!
4. **Hız:** Embedding modelleri (SBERT) CPU üzerinde yavaş çalışabilir. Performansı artırmak için küçük modeller (DistilBERT gibi) mi tercih edilmeli?
