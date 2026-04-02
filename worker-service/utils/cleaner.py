import re
from bs4 import BeautifulSoup

class Cleaner:
    def __init__(self):
        # Temizlenecek gereksiz metin kalıpları (Regex)
        self.junk_patterns = [
            r"WhatsApp İhbar Hattı:?\s*\d+", # WhatsApp numaraları
            r"https?://\S+",                 # Kalan tüm URL'ler
            r"Paylaş:.*?(?=\w|$)",           # Paylaş buton yazıları
            r"Abone ol.*?(?=\w|$)",          # Abone ol yazıları
            r"Tıkla ve.*?(?=\w|$)",          # Tıkla oku yazıları
            r"Gerçekleşen olayla ilgili.*",  # Standart haber sonu kalıpları
            r"Haberin devamı için.*",
            r"Özel Haber",
            r"Editör:.*",
            r"Kaynak:.*",
            r"Yorum yaz.*",
            r"Beğen.*",
            r"İlgili Haberler.*",
            r"Bizi takip edin.*",
            r"\d+\s+izlenme",
            r"Son Dakika",
            r"\s*-\s*Kocaeli\s*$"           # Haber sonundaki şehir etiketi
        ]

    def clean_html(self, html_content):
        if not html_content: return ""
        
        # 1. HTML Tag Temizliği
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Gereksiz etiketleri tamamen kaldır
        for tag in soup(["script", "style", "header", "footer", "nav", "aside", "form", "button"]):
            tag.decompose()
            
        text = soup.get_text(separator=' ')
        
        # 2. Metin Normalizasyonu
        text = re.sub(r'\s+', ' ', text).strip() # Çoklu boşluklar
        text = text.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")
        
        # 3. Agresif Reklam ve Kalıp Temizliği
        for pattern in self.junk_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
            
        return text.strip()
