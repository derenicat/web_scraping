from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from datetime import datetime
import re

class YeniKocaeliScraper(BaseScraper):
    def __init__(self):
        super().__init__("Yeni Kocaeli", "https://www.yenikocaeli.com")
        self.endpoints = [
            "/haber/polis-adliye.html",
            "/haber/guncel.html",
            "/haber/yasam.html"
        ]

    def scrape(self, days=3):
        all_news = []
        news_urls = set()

        for endpoint in self.endpoints:
            print(f"[{self.site_name}] '{endpoint}' taranıyor...")
            html = self.fetch_url(endpoint)
            if not html: continue
            
            soup = BeautifulSoup(html, "html.parser")
            # Yeni Kocaeli haber linkleri .post-title a içinde
            links = soup.select(".post-title a")

            for link in links:
                href = link.get("href")
                if href:
                    # Link göreceli ise tam URL yap
                    news_url = self.base_url + "/" + href if not href.startswith("http") else href
                    if news_url not in news_urls:
                        news_urls.add(news_url)
                        detail = self.scrape_detail(news_url, days)
                        if detail:
                            all_news.append(detail)
                            print(f"   -> [Yeni Haber] {detail['title'][:50]}...")
        return all_news

    def scrape_detail(self, url, days):
        html = self.fetch_url(url)
        if not html: return None
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Tarih Çıkarımı (Bu site için özel)
        published_date = self.extract_yeni_date(soup)
        if not self.is_within_days(published_date, days):
            return None

        # 2. Başlık
        title_tag = soup.find("h1")
        title = self.clean_text(title_tag.get_text()) if title_tag else "Başlıksız"

        # 3. İçerik (JSON-LD veya .news içinden)
        content_para = soup.select(".news p")
        if content_para:
            content = " ".join([p.get_text() for p in content_para])
            content = self.clean_text(content)
        else:
            # Fallback to articleBody meta/json if needed
            content = ""

        if not content or len(content) < 50:
            return None

        return {
            "title": title,
            "content": content,
            "publishedDate": published_date,
            "url": url,
            "siteName": self.site_name,
            "addressText": "Kocaeli"
        }

    def extract_yeni_date(self, soup):
        """Yeni Kocaeli'ye özel tarih ayrıştırma (30 Mart 2026 formatı)."""
        try:
            # Öncelikle meta og:url veya ld+json bakılabilir ama span.clock daha garantili
            date_tag = soup.select_one(".news-date .clock")
            if date_tag:
                date_text = date_tag.get_text(strip=True)
                # '30 Mart 2026 19:57' gibi bir metin bekliyoruz
                # Sadece tarih ve saati alalım
                match = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4}).*?(\d{2}:\d{2})", date_text)
                if match:
                    day = match.group(1).zfill(2)
                    month_name = match.group(2)[:3].capitalize()
                    month = self.tr_months.get(month_name, "01")
                    year = match.group(3)
                    time_str = match.group(4)
                    return datetime.fromisoformat(f"{year}-{month}-{day}T{time_str}:00")
        except: pass
        return datetime.now()
