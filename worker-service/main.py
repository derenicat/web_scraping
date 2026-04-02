from fastapi import FastAPI, Query
from scrapers.ses_kocaeli import SesKocaeliScraper
from scrapers.ozgur_kocaeli import OzgurKocaeliScraper
from nlp.processor import NLPProcessor
from utils.cleaner import Cleaner
import uvicorn
import os
import json
from typing import List, Dict

app = FastAPI(title="Kentsel Haber NLP Worker - Dual Source (Ses + Özgür)")

processor = NLPProcessor()
cleaner = Cleaner()

@app.get("/health")
def health_check():
    return {"status": "UP", "sources": ["Ses Kocaeli", "Özgür Kocaeli"]}

@app.post("/process-news")
async def process_news(days: int = Query(3, ge=1, le=3)):
    all_raw_news = []
    # Çağdaş bloklu olduğu için şimdilik çıkarıldı, Özgür eklendi
    scrapers = [SesKocaeliScraper(), OzgurKocaeliScraper()]
    
    print(f"\n[Worker] {len(scrapers)} haber kaynağı taranıyor (Son {days} gün)...")
    
    for s in scrapers:
        try:
            site_news = s.scrape(days)
            print(f"   -> {s.site_name}: {len(site_news)} haber bulundu.")
            all_raw_news.extend(site_news)
        except Exception as e:
            print(f"   !> {s.site_name} taranırken hata: {e}")
    
    if not all_raw_news:
        return {"status": "success", "processed_count": 0, "results": []}

    # 1. Temizleme ve Lokalite Filtresi
    processed_stage_1 = []
    for news in all_raw_news:
        news['content'] = cleaner.process(news['content'])
        extracted_loc = processor.extract_location(f"{news['title']} {news['content']}")
        
        if extracted_loc is None:
            continue
            
        news['addressText'] = extracted_loc
        news['category'] = processor.classify(news['title'], news['content'])
        processed_stage_1.append(news)
        
    print(f"[Worker] Lokalite filtresinden geçen haber sayısı: {len(processed_stage_1)}")

    # 2. Benzerlik Analizi ve Tekilleştirme (Threshold: %75)
    final_results, merge_logs = processor.check_similarity(processed_stage_1, threshold=0.75)
    
    # Başarılı birleşmeleri logla
    log_dir = "worker-service/logs"
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "successful_merges.json"), "w", encoding="utf-8") as f:
        json.dump(merge_logs, f, ensure_ascii=False, indent=4)

    print(f"[Worker] Tekilleştirme bitti. {len(merge_logs)} olay birleştirildi.")
    
    return {
        "status": "success",
        "processed_count": len(final_results),
        "results": final_results,
        "merges": merge_logs
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
