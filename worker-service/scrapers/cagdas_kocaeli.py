from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from datetime import datetime

class CagdasKocaeliScraper(BaseScraper):
    def __init__(self):
        super().__init__("Çağdaş Kocaeli", "https://www.cagdaskocaeli.com.tr")

    def scrape(self, days=3):
        news_list = []
        # Senin belirttiğin doğru URL rotası
        url = f"{self.base_url}/kocaeli-asayis-haberleri"
        html = self.fetch_url(url)
        if not html: return []
        
        soup = BeautifulSoup(html, "html.parser")
        # Çağdaş Kocaeli haber kartları (Genellikle 'article' veya belirli divler)
        articles = soup.select(".card") or soup.select(".item")
        
        for article in articles:
            try:
                link_tag = article.find("a")
                if not link_tag: continue
                
                news_url = link_tag['href']
                if not news_url.startswith("http"):
                    news_url = self.base_url + news_url
                
                title_tag = article.select_one(".title") or article.find("h3")
                if not title_tag: continue
                title = title_tag.get_text(strip=True)
                
                # Detaya git
                news_html = self.fetch_url(news_url)
                if not news_html: continue
                news_soup = BeautifulSoup(news_html, "html.parser")
                
                # Tarih ve İçerik tespiti
                time_tag = news_soup.find("time")
                news_date = datetime.now() # Fallback
                if time_tag and time_tag.has_attr('datetime'):
                    news_date = datetime.fromisoformat(time_tag['datetime'].replace("Z", "+00:00")).replace(tzinfo=None)
                
                if not self.is_within_days(news_date, days): continue
                
                content_tag = news_soup.select_one(".content-text") or news_soup.select_one("article")
                if not content_tag: continue
                content = content_tag.get_text(strip=True)
                
                news_list.append({
                    "title": title,
                    "content": content,
                    "publishedDate": news_date,
                    "url": news_url,
                    "siteName": self.site_name,
                    "addressText": "Kocaeli"
                })
                if len(news_list) >= 5: break
            except: continue
                
        return news_list
