import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import dateutil.parser
import re
import time
import random

class BaseScraper:
    def __init__(self, site_name, base_url):
        self.site_name = site_name
        self.base_url = base_url
        # Daha gerçekçi bir Header listesi
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]
        self.tr_months = {
            "Oca": "01", "Şub": "02", "Mar": "03", "Nis": "04", "May": "05", "Haz": "06",
            "Tem": "07", "Ağu": "08", "Eyl": "09", "Eki": "10", "Kas": "11", "Ara": "12"
        }

    def fetch_url(self, url):
        """HTTP isteği atar, Bot korumasını aşmak için önlemler içerir."""
        try:
            full_url = url if url.startswith("http") else f"{self.base_url}{url}"
            
            # Rastgele User-Agent seç
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
                "Referer": "https://www.google.com/"
            }
            
            # Sitelere yüklenmemek için rastgele kısa bekleme (0.5 - 1.5 sn)
            time.sleep(random.uniform(0.5, 1.5))
            
            response = requests.get(full_url, headers=headers, timeout=20)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"[{self.site_name}] HTTP Hatası ({url}): {e}")
            return None

    def parse_tr_date(self, date_text):
        try:
            date_text = date_text.replace("-", "").strip()
            parts = re.split(r'\s+', date_text)
            if len(parts) >= 4:
                day = parts[0].zfill(2)
                month_name = parts[1][:3].capitalize()
                month = self.tr_months.get(month_name, "01")
                year = parts[2]
                time_str = parts[3]
                return datetime.fromisoformat(f"{year}-{month}-{day}T{time_str}:00")
        except: pass
        return None

    def parse_date(self, soup):
        if not soup: return datetime.now()
        visible_date_tag = soup.find("span", class_="tarih")
        if visible_date_tag:
            tr_date = self.parse_tr_date(visible_date_tag.get_text(strip=True))
            if tr_date: return tr_date
        return datetime.now()

    def clean_text(self, text):
        if not text: return ""
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def is_within_days(self, news_date, days):
        limit_date = datetime.now() - timedelta(days=days)
        return news_date >= limit_date
