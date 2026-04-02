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
        # Çok dilli ve kararlı bir model
        self.embed_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', device=self.device)

        self.districts = ["Başiskele", "Çayırova", "Darıca", "Derince", "Dilovası", "Gebze", "Gölcük", "İzmit", "Kandıra", "Karamürsel", "Kartepe", "Körfez"]

        self.categories = {
            'Cinayet': {'strong': ['cinayet', 'öldürüldü', 'infaz'], 'weak': ['polis'], 'negative': []},
            'Yangın': {'strong': ['yangın çıktı'], 'weak': ['itfaiye'], 'negative': []},
            'Trafik Kazası': {'strong': ['trafik kazası'], 'weak': ['kaza'], 'negative': []},
            'Hırsızlık': {'strong': ['hırsızlık'], 'weak': ['çalındı'], 'negative': []},
            'Elektrik Kesintisi': {'strong': ['elektrik kesintisi'], 'weak': ['kesinti'], 'negative': []},
            'Kültürel Etkinlikler': {'strong': ['konser'], 'weak': ['ziyaret'], 'negative': []}
        }

    def classify(self, title: str, content: str) -> str:
        text = (title + " " + content).lower()
        for cat, keywords in self.categories.items():
            if any(w in text for w in keywords['strong']): return cat
        return "Diğer"

    def extract_location(self, text: str) -> Optional[str]:
        for d in self.districts:
            if d.lower() in text.lower(): return f"{d}, Kocaeli"
        return "Kocaeli" if "kocaeli" in text.lower() else None

    def check_similarity(self, news_list: List[Dict], threshold: float = 0.75) -> tuple[List[Dict], List[Dict]]:
        if not news_list: return [], []
        
        print(f"\n[Similarity] {len(news_list)} haber tekilleştiriliyor (Eşik: {threshold})...")
        
        titles = [n['title'] for n in news_list]
        embeddings = self.embed_model.encode(titles, convert_to_tensor=True)
        
        processed_indices = set()
        final_results = []
        merge_logs = [] # Sadece başarılı birleşmeleri tutacağız
        
        for i in range(len(news_list)):
            if i in processed_indices: continue
            
            main_news = news_list[i].copy()
            main_news['sources'] = [{'siteName': main_news.pop('siteName'), 'url': main_news.pop('url')}]
            
            cosine_scores = util.cos_sim(embeddings[i], embeddings)[0]
            
            for j in range(len(news_list)):
                if i == j or j in processed_indices: continue
                
                score = float(cosine_scores[j])
                
                if score >= threshold:
                    print(f"   [MERGE FOUND] {score:.2f} | '{titles[i][:40]}' <<>> '{titles[j][:40]}'")
                    
                    # Loga ekle
                    merge_logs.append({
                        "score": round(score, 4),
                        "news_a": {"title": titles[i], "site": main_news['sources'][0]['siteName']},
                        "news_b": {"title": titles[j], "site": news_list[j]['siteName']}
                    })
                    
                    # Kaynağı birleştir
                    main_news['sources'].append({
                        'siteName': news_list[j]['siteName'], 
                        'url': news_list[j]['url']
                    })
                    processed_indices.add(j)
            
            final_results.append(main_news)
            processed_indices.add(i)
            
        return final_results, merge_logs
