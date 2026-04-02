# Kentsel Haber İzleme Sistemi: Gelişmiş Scraping Modülü Planı

Bu döküman, projenin veri toplama katmanının (Data Collection Layer) teknik mimarisini ve implementasyon adımlarını tanımlar.

## 1. Kullanılan Teknolojiler ve Tercih Sebepleri

| Kütüphane | Teknik Rolü | Tercih Sebebi (Senior Perspective) |
| :--- | :--- | :--- |
| **Requests** | HTTP Katmanı | Hafif ve hızlıdır. `headers` manipülasyonu ile bot korumalarını aşmaya yardımcı olur. |
| **BeautifulSoup4** | DOM Parsing | Esnek CSS selector desteği sunar. HTML bozuk olsa bile ("lenient parsing") veriyi kurtarabilir. |
| **dateutil** | Tarih Normalizasyonu | Web sitelerindeki karmaşık tarih formatlarını (ISO, Türkçe metin vb.) standart Python objesine dönüştürür. |
| **re (Regex)** | Agresif Temizlik | WhatsApp numaraları, "Paylaş" kalıpları gibi metin bazlı çerçöpün ayıklanmasında en güçlü araçtır. |
| **URL Normalize** | Mükerrer Kontrolü | URL'lerin sonundaki `/` veya query parametrelerini normalize ederek aynı haberin 2 kez çekilmesini önler. |

## 2. Implementasyon Adımları (Ses Kocaeli Odaklı)

### Faz 1: Ham Veri Analizi (Tamamlandı ✅)
- `/kocaeli-asayis-haberleri` ve `/kocaeli-son-dakika-haberler` sayfaları indirildi.
- Haber linklerinin `.post h3.b a` içinde olduğu saptandı.
- Detay sayfasında içeriğin `#main-text` ID'sine sahip `div` içinde olduğu doğrulandı.

### Faz 2: Esnek Scraper Altyapısı (Base Class)
- Tüm scraperların kalıtım alacağı bir `BaseScraper` sınıfı oluşturulacak.
- Ortak HTTP istek yönetimi ve hata yakalama (Logging) burada yapılacak.

### Faz 3: SesKocaeliScraper Yazımı
- Listeleme sayfasından linklerin toplanması.
- Her link için detay sayfasına gidilip verilerin (Title, Date, Content) sökülmesi.
- **İnce Ayar:** Haber içeriğindeki reklam linklerinin (`tag-link`) temizlenmesi.

### Faz 4: Veri Doğrulama ve Kayıt
- Çekilen verinin şemaya uygunluğunun kontrolü.
- Veritabanı öncesi "Unique Check" (URL Hash tabanlı).

---

## 3. İlk Kod: `BaseScraper` ve `SesKocaeliScraper`

Şimdi bu planı hayata geçirmek için kodlamaya başlıyoruz.
