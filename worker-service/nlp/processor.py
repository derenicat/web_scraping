import spacy
from sentence_transformers import SentenceTransformer, util
import re
import torch
from typing import List, Dict, Optional

class NLPProcessor:
    def __init__(self):
        print("[NLP] Katı Lokalite Modelleri yükleniyor...")
        try:
            self.nlp = spacy.load("tr_core_news_lg")
        except:
            self.nlp = None
            
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embed_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', device=self.device)

        # KOCAELİ İLÇELERİ (DOĞRULAMA ANAHTARIDIR)
        self.districts = ["Başiskele", "Çayırova", "Darıca", "Derince", "Dilovası", "Gebze", "Gölcük", "İzmit", "Kandıra", "Karamürsel", "Kartepe", "Körfez"]
        
        # Dış İller (Eleme Listesi)
        self.other_cities = ["Bursa", "Aydın", "İstanbul", "Sakarya", "Yalova", "Düzce", "Bolu", "Ankara", "İzmir"]

        self.categories = {
            'Cinayet': {'strong': ['cinayet', 'öldürüldü', 'infaz', 'ceset bulundu', 'kurşun yağmuru', 'kan davası', 'kanlı saldırı'], 'weak': ['ateş açıldı', 'silahlı saldırı', 'kanlar içinde'], 'negative': ['maç', 'gol', 'kaza', 'yangın']},
            'Yangın': {'strong': ['yangın çıktı', 'itfaiye ekipleri', 'alevler yükseldi', 'dumanlar yükseldi', 'soğutma çalışması', 'alevlere teslim'], 'weak': ['tutuştur', 'patlama', 'şofben', 'orman yangını'], 'negative': ['denetim', 'ziyaret', 'kaza']},
            'Trafik Kazası': {'strong': ['trafik kazası', 'zincirleme kaza', 'direksiyon hakimiyeti', 'şarampole devrildi', 'kafa kafaya çarpıştı', 'plakalı otomobil', 'çarpıp kaçtı'], 'weak': ['kaza', 'çarpışma', 'yaralılar var', 'motosiklet kazası', 'bariyerlere çarptı'], 'negative': ['ötv', 'vergi', 'ihale', 'cinayet', 'yangın']},
            'Hırsızlık': {'strong': ['hırsızlık', 'soygun', 'ziynet eşyası', 'kasayı boşalttı', 'yankesicilik', 'dolandırıcılık', 'çalındı'], 'weak': ['şüpheli yakalandı', 'gözaltına alındı', 'polis baskını'], 'negative': ['etkinlik', 'belediye', 'spor', 'kaza']},
            'Elektrik Kesintisi': {'strong': ['elektrik kesintisi', 'planlı kesinti', 'bakım çalışması nedeniyle', 'elektriksiz kalacak'], 'weak': ['elektrik arıza', 'trafo patlaması'], 'negative': ['cinayet', 'kaza']},
            'Kültürel Etkinlikler': {'strong': ['konser', 'tiyatro oyunu', 'sergi açılışı', 'festival heyecanı', 'kültür sanat merkezi', 'açılış töreni', 'konferans'], 'weak': ['etkinlik düzenlendi', 'panel', 'konferans', 'sanatseverler', 'ziyaret etti', 'buluşma'], 'negative': ['kaza', 'cinayet', 'yangın', 'soygun']}
        }

    def classify(self, title: str, content: str) -> str:
        text = (title + " " + content).lower()
        scores = {}
        for cat_name, keywords in self.categories.items():
            score = 0
            for word in keywords['strong']:
                if word in text: score += 20
            for word in keywords['weak']:
                if word in text: score += 5
            for word in keywords['negative']:
                if word in text: score -= 25
            if score > 0: scores[cat_name] = score
        if not scores: return "Diğer"
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[0][0] if sorted_scores[0][1] >= 10 else "Diğer"

    def extract_location(self, text: str) -> Optional[str]:
        """Kocaeli sınırları içerisinde en spesifik adresi çıkarır."""
        text_lower = text.lower()
        
        # 1. KOCAELİ DOĞRULAMASI (Kritik Filtre)
        # Eğer metinde Kocaeli'ye ait bir ilçe veya "Kocaeli" geçmiyorsa haber dışarıdandır.
        found_districts = [d for d in self.districts if d.lower() in text_lower]
        is_kocaeli_mention = "kocaeli" in text_lower
        
        # Bursa, Aydın gibi başka iller geçiyorsa ve Kocaeli ilçesi yoksa direkt ele
        found_other_cities = [c for c in self.other_cities if c.lower() in text_lower]
        if found_other_cities and not found_districts:
            return None # Kocaeli dışı haber

        if not found_districts and not is_kocaeli_mention:
            return None # Kocaeli ile bağı yok

        # 2. Mikro-Lokasyon Regex Taraması
        micro_patterns = [
            r"([A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s?)+ (Mahallesi|Caddesi|Sokak|Bulvarı|Mevkii|Kavşağı|Tesisleri|Camii|Yolu|Giseleri|Stadyumu)",
            r"([A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s?)+(Parkı|Bahçesi|Meydanı|Köprüsü|Tüneli|Durağı)"
        ]
        
        found_locations = []
        for pattern in micro_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                loc_text = match.group(0).strip()
                if len(loc_text) > 5:
                    found_locations.append(loc_text)

        # 3. Sonuç Birleştirme
        if found_locations:
            best_loc = max(found_locations, key=len)
            
            # Eğer bulunan lokasyon Bursa/Aydın gibi bir yerdeyse (Context check)
            # Bizim ilçelerimizden biriyle beraber geçiyorsa Kocaeli'dir.
            district_prefix = ""
            if found_districts:
                district_prefix = f"{found_districts[0]}, "
            
            return f"{best_loc}, {district_prefix}Kocaeli"

        if found_districts:
            return f"{found_districts[0]}, Kocaeli"

        if is_kocaeli_mention:
            return "Kocaeli"
            
        return None

    def check_similarity(self, news_list: List[Dict], threshold: float = 0.75) -> tuple[List[Dict], List[Dict]]:
        if not news_list: return [], []
        titles = [n['title'] for n in news_list]
        hybrid_texts = [f"{n['title']} {n['content'][:150]}" for n in news_list]
        embeddings = self.embed_model.encode(hybrid_texts, convert_to_tensor=True)
        processed_indices = set()
        final_results = []
        merge_logs = []
        for i in range(len(news_list)):
            if i in processed_indices: continue
            main_news = news_list[i].copy()
            main_news['sources'] = [{'siteName': main_news.pop('siteName'), 'url': main_news.pop('url')}]
            cosine_scores = util.cos_sim(embeddings[i], embeddings)[0]
            for j in range(i + 1, len(news_list)):
                if j in processed_indices: continue
                score = float(cosine_scores[j])
                if score >= threshold:
                    merge_logs.append({"score": round(score, 4), "news_a": {"title": titles[i], "site": main_news['sources'][0]['siteName']}, "news_b": {"title": titles[j], "site": news_list[j]['siteName']}})
                    main_news['sources'].append({'siteName': news_list[j]['siteName'], 'url': news_list[j]['url']})
                    processed_indices.add(j)
            final_results.append(main_news)
            processed_indices.add(i)
        return final_results, merge_logs
