from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from datetime import datetime

class SesKocaeliScraper(BaseScraper):
    def __init__(self):
        super().__init__("Ses Kocaeli", "https://www.seskocaeli.com")

    def scrape(self, days=3):
        news_list = []
        url = f"{self.base_url}/asayis" # Ses Kocaeli asayiş yolu
        html = self.fetch_url(url)
        if not html: return []
        
        soup = BeautifulSoup(html, "html.parser")
        all_links = soup.find_all("a", href=True)
        
        for link in all_links:
            href = link['href']
            # Haber detay linki kontrolü
            if "/haber/" in href and (href.startswith("/") or self.base_url in href):
                news_url = self.base_url + href if href.startswith("/") else href
                if any(n['url'] == news_url for n in news_list): continue
                
                title = link.get_text(strip=True)
                if len(title) < 20: continue
                
                news_html = self.fetch_url(news_url)
                if not news_html: continue
                news_soup = BeautifulSoup(news_html, "html.parser")
                
                time_tag = news_soup.find("time")
                news_date = datetime.now()
                if time_tag and time_tag.has_attr('datetime'):
                    try:
                        news_date = datetime.fromisoformat(time_tag['datetime'].replace("Z", "+00:00")).replace(tzinfo=None)
                    except: pass
                
                if not self.is_within_days(news_date, days): continue
                
                content_tag = news_soup.select_one(".content-text") or news_soup.select_one("article")
                if not content_tag: continue
                
                news_list.append({
                    "title": title,
                    "content": content_tag.get_text(strip=True),
                    "publishedDate": news_date,
                    "url": news_url,
                    "siteName": self.site_name,
                    "addressText": "Kocaeli"
                })
                if len(news_list) >= 5: break
        return news_list
