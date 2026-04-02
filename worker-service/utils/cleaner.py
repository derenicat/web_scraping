import re
import unicodedata

class Cleaner:
    def __init__(self):
        # Temizlenecek gereksiz metin kalıpları (Regex)
        self.junk_patterns = [
            r"WhatsApp İhbar Hattı:?\s*\d*",
            r"Bizi Twitter'da takip edin.*",
            r"https?://\S+",                 # Kalan URL'ler
            r"Paylaş:.*?(?=\w|$)",           # Paylaş buton yazıları
            r"Abone ol.*?(?=\w|$)",          # Abone ol yazıları
            r"Tıkla ve.*?(?=\w|$)",          # Tıkla oku yazıları
            r"Daha fazla haber için.*",
            r"Resme tıklayın.*",
            r"İlgili Haberler.*",
            r"Bizi takip edin.*",
            r"\d+\s+izlenme",
            r"Yorum yaz.*",
            r"Beğen.*",
            r"Kaynak:.*",
            r"Haberin videosu için.*",
            r"Son Dakika",
            r"\s*-\s*Kocaeli\s*$"           # Haber sonundaki şehir etiketi
        ]

    def normalize_text(self, text):
        """Unicode normalizasyonu yapar ve metni standartlaştırır."""
        if not text: return ""
        # Unicode karakterlerini normalize et (örn: ince i harfi sorunları için)
        text = unicodedata.normalize('NFKC', text)
        # Özel tırnak işaretlerini standartlaştır
        text = text.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")
        return text

    def clean_junk(self, text):
        """Reklam ve alakasız bölümleri temizler."""
        for pattern in self.junk_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        return text

    def clean_whitespace(self, text):
        """Fazla boşlukları ve satır sonlarını temizler."""
        # Çoklu satır sonlarını tek satıra indir
        text = re.sub(r'\n+', ' ', text)
        # Çoklu boşlukları tek boşluğa indir
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def process(self, text):
        """Tüm temizleme adımlarını sırasıyla uygular."""
        if not text: return ""
        text = self.normalize_text(text)
        text = self.clean_junk(text)
        text = self.clean_whitespace(text)
        return text
