import sys
import os
import json

# Modülleri içe aktarmak için yolu ayarla
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.ozgur_kocaeli import OzgurKocaeliScraper
from scrapers.cagdas_kocaeli import CagdasKocaeliScraper
from nlp.processor import NLPProcessor
from utils.cleaner import Cleaner

def run_real_test():
    print("--- Kentsel Haber İzleme Sistemi - Canlı Veri Testi (Özgür & Çağdaş) ---")
    
    # 1. Modülleri Başlat
    print("[1/3] NLP Modelleri yükleniyor...")
    processor = NLPProcessor()
    cleaner = Cleaner()
    
    scrapers = [OzgurKocaeliScraper(), CagdasKocaeliScraper()]

    # 2. Canlı Scraping
    print("[2/3] Haber sitelerinden canlı veri çekiliyor...")
    all_raw_news = []
    for s in scrapers:
        print(f"-> {s.site_name} taranıyor...")
        site_news = s.scrape(days=3)
        print(f"   {len(site_news)} adet haber bulundu.")
        all_raw_news.extend(site_news)
    
    if not all_raw_news:
        print("❌ Hiç haber bulunamadı! Lütfen URL'leri veya internet bağlantınızı kontrol edin.")
        return

    # 3. NLP İşleme
    print("[3/3] NLP İşleme Hattı (NER, Sınıflandırma, Benzerlik) çalışıyor...")
    processed_news = []
    for news in all_raw_news:
        # Metni temizle
        news['content'] = cleaner.clean_html(news['content'])
        
        # NER ile Konum Çıkar
        news['addressText'] = processor.extract_location(news['content'])
        
        # Kategori Sınıflandır
        news['category'] = processor.classify(news['content'])
        
        processed_news.append(news)

    # Benzerlik Analizi (%85 eşik ile daha esnek bir test yapalım)
    final_output = processor.check_similarity(processed_news, threshold=0.85)

    print("\n--- ANALİZ TAMAMLANDI - CANLI VERİ ÇIKTISI ---")
    print(json.dumps(final_output, indent=2, ensure_ascii=False, default=str))

if __name__ == "__main__":
    run_real_test()
