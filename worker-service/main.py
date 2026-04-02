from fastapi import FastAPI, Query
from scrapers.ozgur_kocaeli import OzgurKocaeliScraper
from scrapers.cagdas_kocaeli import CagdasKocaeliScraper
from scrapers.ses_kocaeli import SesKocaeliScraper
from scrapers.yeni_kocaeli import YeniKocaeliScraper
from scrapers.bizim_yaka import BizimYakaScraper
from nlp.processor import NLPProcessor
from utils.cleaner import Cleaner
import uvicorn

app = FastAPI(title="Kentsel Haber NLP Worker")

# Servisler yüklendiğinde modeller belleğe alınır
processor = NLPProcessor()
cleaner = Cleaner()

@app.get("/health")
def health_check():
    return {"status": "UP", "service": "Python Worker"}

@app.post("/process-news")
async def process_news(days: int = Query(3, ge=1, le=3)):
    all_raw_news = []
    
    # Tüm Scraper'lar
    scrapers = [
        OzgurKocaeliScraper(),
        CagdasKocaeliScraper(),
        SesKocaeliScraper(),
        YeniKocaeliScraper(),
        BizimYakaScraper()
    ]
    
    print(f"[Worker] {len(scrapers)} site taranıyor...")
    
    for s in scrapers:
        try:
            site_news = s.scrape(days)
            print(f"   -> {s.site_name}: {len(site_news)} haber bulundu.")
            all_raw_news.extend(site_news)
        except Exception as e:
            print(f"   !> {s.site_name} taranırken hata: {e}")
    
    if not all_raw_news:
        return {"status": "success", "processed_count": 0, "results": []}

    # NLP İşleme Hattı
    processed_news = []
    for news in all_raw_news:
        # Temizle
        news['content'] = cleaner.clean_html(news['content'])
        # Akıllı Konum Çıkar (Mahalle + Cadde + İlçe)
        news['addressText'] = processor.extract_location(news['content'])
        # Kategori Sınıflandır
        news['category'] = processor.classify(news['content'])
        processed_news.append(news)
        
    # Benzerlik Analizi (%85 eşik ile grupla)
    final_news = processor.check_similarity(processed_news, threshold=0.85)
    
    return {
        "status": "success",
        "processed_count": len(final_news),
        "results": final_news
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
