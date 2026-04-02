from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from datetime import datetime

class CagdasKocaeliScraper(BaseScraper):
    def __init__(self):
        super().__init__("Çağdaş Kocaeli", "https://www.cagdaskocaeli.com.tr")
        self.endpoints = [
            "/kocaeli-gundem-haberleri",
            "/kocaeli-asayis-haberleri",
            "/kultur-sanat"
        ]

    def scrape(self, days=3):
        all_news = []
        news_urls = set()

        for endpoint in self.endpoints:
            print(f"[{self.site_name}] '{endpoint}' taranıyor...")
            html = self.fetch_url(endpoint)
            if not html: continue
            
            soup = BeautifulSoup(html, "html.parser")
            # Daktilo sistemi standart seçicileri
            links = soup.select(".post h3.b a")
            links += soup.select("ul.list.t-2 li a")

            for link in links:
                href = link.get("href")
                if href and "/haber/" in href:
                    news_url = self.base_url + href if href.startswith("/") else href
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
        
        # 1. Tarih Kontrolü
        published_date = self.parse_date(soup)
        if not self.is_within_days(published_date, days):
            return None

        # 2. Başlık
        title_tag = soup.find("h1")
        title = self.clean_text(title_tag.get_text()) if title_tag else "Başlıksız"

        # 3. İçerik
        content_div = soup.find("div", id="main-text")
        if content_div:
            # Önemli metinleri koru (Mahalle, ilçe vb.)
            for tag in content_div.select(".tag-link"):
                tag.unwrap()
            
            # Çöpleri temizle
            for junk in content_div.select(".google-news-button, .entry-share, .ad-channel, script, style, figure, blockquote"):
                junk.decompose()
            
            paragraphs = content_div.find_all("p")
            content = " ".join([p.get_text() for p in paragraphs])
            content = self.clean_text(content)
        else:
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
