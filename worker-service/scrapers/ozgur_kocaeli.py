from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from datetime import datetime

class OzgurKocaeliScraper(BaseScraper):
    def __init__(self):
        super().__init__("Özgür Kocaeli", "https://www.ozgurkocaeli.com.tr")

    def scrape(self, days=3):
        news_list = []
        # Senin belirttiğin doğru URL rotası
        url = f"{self.base_url}/kocaeli-asayis-haberleri"
        html = self.fetch_url(url)
        if not html: return []
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Agresif Tarama: Sayfadaki TÜM linkleri (a tag) bul ve asayişle ilgili olanları süz
        # Çünkü 'div.item' bazen 'div.news-item' veya 'article' olabiliyor.
        all_links = soup.find_all("a", href=True)
        
        for link in all_links:
            href = link['href']
            # Eğer linkin içinde asayiş geçiyorsa ve bu bir haber detayıysa
            if "/kocaeli-asayis-haberleri/" in href or (href.startswith("/") and len(href.split("/")) > 2):
                news_url = self.base_url + href if href.startswith("/") else href
                
                # Zaten listede mi kontrol et
                if any(n['url'] == news_url for n in news_list): continue
                
                # Başlığı yakala
                title = link.get_text(strip=True)
                if len(title) < 15: # Çok kısa başlıklar muhtemelen buton/etikettir
                    # Çevredeki başlığı bulmaya çalış
                    parent_text = link.parent.get_text(strip=True)
                    title = parent_text if len(parent_text) > 15 else title
                
                if len(title) < 15: continue
                
                # Habere Git
                news_html = self.fetch_url(news_url)
                if not news_html: continue
                news_soup = BeautifulSoup(news_html, "html.parser")
                
                # Tarih ve İçerik
                time_tag = news_soup.find("time")
                news_date = datetime.now()
                if time_tag and time_tag.has_attr('datetime'):
                    try:
                        news_date = datetime.fromisoformat(time_tag['datetime'].replace("Z", "+00:00")).replace(tzinfo=None)
                    except: pass
                
                if not self.is_within_days(news_date, days): continue
                
                # İçerik kısmını al (En geniş seçicileri kullanıyoruz)
                content_tag = news_soup.select_one("div.content-text") or news_soup.select_one("article") or news_soup.select_one(".text")
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
                
        return news_list
