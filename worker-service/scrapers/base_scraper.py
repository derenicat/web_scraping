import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import dateutil.parser

class BaseScraper:
    def __init__(self, site_name, base_url):
        self.site_name = site_name
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_url(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Hata ({self.site_name} - {url}): {e}")
            return None

    def parse_date(self, news_soup: BeautifulSoup):
        """
        Web sitesindeki haber tarihini meta etiketlerinden çekmeye çalışır.
        Fallback olarak datetime.now() döner.
        """
        # 1. Meta Tags (Standart)
        meta_selectors = [
            {'property': 'article:published_time'},
            {'name': 'publish-date'},
            {'itemprop': 'datePublished'},
            {'property': 'og:published_time'}
        ]
        
        for selector in meta_selectors:
            tag = news_soup.find("meta", selector)
            if tag and tag.get('content'):
                try:
                    return dateutil.parser.parse(tag['content']).replace(tzinfo=None)
                except: continue

        # 2. Time Tag
        time_tag = news_soup.find("time")
        if time_tag and time_tag.get('datetime'):
            try:
                return dateutil.parser.parse(time_tag['datetime']).replace(tzinfo=None)
            except: pass
        
        # 3. Fallback: Haber başlığında veya içerikte tarih arama (Karmaşık ama gerekirse eklenebilir)
        return datetime.now()

    def is_within_days(self, news_date, days):
        limit_date = datetime.now() - timedelta(days=days)
        return news_date >= limit_date
