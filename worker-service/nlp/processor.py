from sentence_transformers import SentenceTransformer, util
import spacy
from typing import List, Dict

class NLPProcessor:
    def __init__(self):
        print("[NLP] Modeller yükleniyor (Turkish NLP Suite & BERT)...")
        # BERT tabanlı benzerlik modeli
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        # Turkish NLP Suite modeli
        self.nlp = spacy.load("tr_core_news_lg")
        
        # Kategori anahtar kelimeleri
        self.categories = {
            'Trafik Kazası': ['kaza', 'çarpışma', 'zincirleme', 'devrildi', 'otomobil', 'yaralı', 'motosiklet'],
            'Yangın': ['yangın', 'alev', 'itfaiye', 'duman', 'soğutma', 'orman'],
            'Elektrik Kesintisi': ['elektrik', 'kesinti', 'edaş', 'arıza', 'trafo', 'karanlık'],
            'Hırsızlık': ['hırsız', 'çalındı', 'soygun', 'asayiş', 'polis', 'gözaltı'],
            'Kültürel Etkinlikler': ['konser', 'sergi', 'festival', 'tiyatro', 'sanat', 'müze']
        }

    def extract_location(self, text: str) -> str:
        """Metinden ilçe ve mahalle isimlerini çıkarır."""
        doc = self.nlp(text)
        locations = [ent.text for ent in doc.ents if ent.label_ == "LOC"]
        
        districts = ["izmit", "gebze", "darıca", "körfez", "gölcük", "derince", "kartepe", "çayırova", "başiskele", "karamürsel", "kandıra", "dilovası"]
        
        found_districts = [loc for loc in locations if loc.lower() in districts]
        if found_districts:
            return f"{found_districts[0]}, Kocaeli"
        
        return "Kocaeli"

    def classify(self, text: str) -> str:
        text = text.lower()
        for cat, keywords in self.categories.items():
            if any(word in text for word in keywords):
                return cat
        return "Diğer"

    def check_similarity(self, news_list: List[Dict], threshold: float = 0.90) -> List[Dict]:
        """
        %90 ve üzeri benzerlikte haberleri birleştirir ve terminalde LOG gösterir.
        """
        if not news_list: return []
        
        print(f"\n[Similarity] {len(news_list)} haber benzerlik için analiz ediliyor...")
        
        titles = [n['title'] for n in news_list]
        embeddings = self.model.encode(titles, convert_to_tensor=True)
        
        processed_indices = set()
        final_results = []
        
        for i in range(len(news_list)):
            if i in processed_indices: continue
            
            main_news = news_list[i].copy()
            # Başlangıçta tek bir kaynak var
            main_news['sources'] = [{
                'siteName': main_news.pop('siteName'),
                'url': main_news.pop('url')
            }]
            
            cosine_scores = util.cos_sim(embeddings[i], embeddings)[0]
            
            for j in range(i + 1, len(news_list)):
                if j in processed_indices: continue
                
                score = cosine_scores[j].item()
                if score >= threshold:
                    print(f"   [MERGE] '{main_news['title'][:40]}...' << >> '{news_list[j]['title'][:40]}...' (Score: {score:.2f})")
                    
                    # Kaynağı ekle
                    main_news['sources'].append({
                        'siteName': news_list[j]['siteName'],
                        'url': news_list[j]['url']
                    })
                    processed_indices.add(j)
            
            final_results.append(main_news)
            processed_indices.add(i)
            
        print(f"[Similarity] Analiz bitti. Toplam {len(final_results)} tekil haber marker'ı oluşturuldu.\n")
        return final_results
