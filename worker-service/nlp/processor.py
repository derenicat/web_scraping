import spacy
from sentence_transformers import SentenceTransformer, util
import re
import torch
from typing import List, Dict, Optional

class NLPProcessor:
    def __init__(self):
        print("[NLP] Gelişmiş Lokal Modeller yükleniyor...")
        try:
            self.nlp = spacy.load("tr_core_news_lg")
        except:
            self.nlp = None
            
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embed_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', device=self.device)

        self.districts = ["Başiskele", "Çayırova", "Darıca", "Derince", "Dilovası", "Gebze", "Gölcük", "İzmit", "Kandıra", "Karamürsel", "Kartepe", "Körfez"]

        # GELİŞMİŞ NİŞ ANAHTAR KELİMELER VE PUANLAMA
        self.categories = {
            'Cinayet': {
                'strong': ['cinayet', 'öldürüldü', 'infaz', 'ceset bulundu', 'kurşun yağmuru', 'boğazı kesildi', 'kan davası', 'kanlı saldırı',"Faili meçhul","cinayete kurban gitti"],
                'weak': ['ateş açıldı', 'silahlı saldırı', 'kanlar içinde', 'hayatını kaybetti', 'operasyon'],
                'negative': ['maç', 'gol', 'kaza', 'yangın']
            },
            'Yangın': {
                'strong': ['yangın çıktı', 'itfaiye ekipleri', 'alevler yükseldi', 'dumanlar yükseldi', 'soğutma çalışması', 'kontrol altına alındı', 'alevlere teslim',"Kül oldu"],
                'weak': ['tutuştur',"tutuştu", 'patlama', 'şofben', 'orman yangını', 'ev yangını', 'itfaiye müdahale',"yangın"],
                'negative': ['denetim', 'ziyaret', 'kaza']
            },
            'Trafik Kazası': {
                'strong': ['trafik kazası', 'zincirleme kaza', 'direksiyon hakimiyeti', 'şarampole devrildi', 'kafa kafaya çarpıştı', 'plakalı otomobil', 'çarpıp kaçtı', 'yaya geçidi'],
                'weak': ['kaza', 'çarpışma', 'çarpıştı', "çarptı", 'yaralılar var', 'motosiklet kazası', 'tır devrildi', 'araç içinde sıkıştı', 'bariyerlere çarptı',"altında kaldı","servis","kör nokta"],
                'negative': ['ötv', 'vergi', 'ihale', 'cinayet', 'yangın']
            },
            'Hırsızlık': {
                'strong': ['hırsızlık', 'soygun', 'ziynet eşyası', 'kasayı boşalttı', 'yankesicilik', 'dolandırıcılık', 'çalındı', 'yağma',],
                'weak': ['şüpheli yakalandı', 'gözaltına alındı', 'polis baskını', 'asayiş uygulaması', 'ele geçirildi', 'hırsız', 'soyguncu', 'dolandırıcı', 'yankesici',"Suçüstü yakalandı"],
                'negative': ['etkinlik', 'belediye', 'spor', 'kaza']
            },
            'Elektrik Kesintisi': {
                'strong': ['elektrik kesintisi', 'planlı kesinti', 'bakım çalışması nedeniyle', 'elektriksiz kalacak', 'sedaş duyurdu'],
                'weak': ['elektrik arıza', 'trafo patlaması', 'karanlığa gömüldü'],
                'negative': ['cinayet', 'kaza']
            },
            'Kültürel Etkinlikler': {
                'strong': ['konser', 'tiyatro oyunu', 'sergi açılışı', 'festival heyecanı', 'kültür sanat merkezi', 'açılış töreni', 'konferans'],
                'weak': ['etkinlik düzenlendi', 'panel', 'sanatseverler', 'ziyaret etti', 'buluşma',"buluştu", 'heyet', 'protokol', 'katıldı','gösteri', 'sahne aldı',"kültür"],
                'negative': ['kaza', 'cinayet', 'yangın', 'soygun']
            }
        }

    def classify(self, title: str, content: str) -> str:
        text = (title + " " + content).lower()
        scores = {}
        for cat_name, keywords in self.categories.items():
            score = 0
            for word in keywords['strong']:
                if word in text: score += 20 # Güçlü kelime ağırlığı 20'ye çıktı
            for word in keywords['weak']:
                if word in text: score += 5
            for word in keywords['negative']:
                if word in text: score -= 25 # Negatif filtre daha sert
            if score > 0: scores[cat_name] = score
        
        if not scores: return "Diğer"
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        # Baraj puanı 10'a yükseltildi (Kesinlik için)
        return sorted_scores[0][0] if sorted_scores[0][1] >= 10 else "Diğer"

    def extract_location(self, text: str) -> Optional[str]:
        for d in self.districts:
            if d.lower() in text.lower(): return f"{d}, Kocaeli"
        return "Kocaeli" if "kocaeli" in text.lower() else None

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
