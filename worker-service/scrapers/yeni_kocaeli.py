from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

class YeniKocaeliScraper(BaseScraper):
    def __init__(self):
        super().__init__("Yeni Kocaeli", "https://www.yenikocaeli.com")

    def scrape(self, days=3):
        news_list = []
        # URL 404'ten düzeltildi
        url = f"{self.base_url}/kocaeli-asayis-haberleri"
        html = self.fetch_url(url)
        if not html: return []
        
        soup = BeautifulSoup(html, "html.parser")
        # Yeni Kocaeli haber linkleri genelde 'card-title' içinde
        all_links = soup.find_all("a", href=True)
        
        for link in all_links:
            href = link['href']
            if "/haber/" in href:
                news_url = self.base_url + href if href.startswith("/") else href
                if any(n['url'] == news_url for n in news_list): continue
                
                news_html = self.fetch_url(news_url)
                if not news_html: continue
                news_soup = BeautifulSoup(news_html, "html.parser")
                
                # Gerçek yayın tarihi çekme (Meta Tags)
                time_tag = news_soup.find("meta", property="article:published_time")
                news_date = self.parse_date(time_tag['content'] if time_tag else None)
                
                if not self.is_within_days(news_date, days): continue
                
                title_tag = news_soup.find("h1")
                content_tag = news_soup.select_one(".content-text") or news_soup.select_one("article")
                
                if title_tag and content_tag:
                    news_list.append({
                        "title": title_tag.get_text(strip=True),
                        "content": content_tag.get_text(strip=True),
                        "publishedDate": news_date,
                        "url": news_url,
                        "siteName": self.site_name,
                        "addressText": "Kocaeli"
                    })
        return news_list
