import os
import cloudscraper
from bs4 import BeautifulSoup

def scrape_wiki():
    """
    Scrapes lore from Attack on Titan Fandom Wiki.
    Targets specific character and faction pages and extracts text.
    """
    urls = [
        "https://attackontitan.fandom.com/wiki/Eren_Yeager",
        "https://attackontitan.fandom.com/wiki/Marley",
        "https://attackontitan.fandom.com/wiki/Survey_Corps"
    ]
    
    # Ensure our data directory exists
    os.makedirs("data", exist_ok=True)
    raw_lore_path = "data/raw_lore.txt"
    
    print("Scraping wiki pages...")
    all_text = []
    
    # Use cloudscraper to bypass CloudFlare protection
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    for url in urls:
        print(f"Fetching {url}...")
        try:
            response = scraper.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # The main content is usually in divs with class 'mw-parser-output'
                content = soup.find('div', class_='mw-parser-output')
                if content:
                    paragraphs = content.find_all('p', recursive=False)
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        # Filter out empty strings or very short snippets
                        if text and len(text) > 20: 
                            all_text.append(text)
                else:
                    print(f"  -> Could not find main content for {url}")
            else:
                print(f"  -> Failed to fetch {url}. Status code: {response.status_code}")
        except Exception as e:
            print(f"  -> Error fetching {url}: {e}")
            
    with open(raw_lore_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_text))
        
    print(f"Scraped {len(all_text)} paragraphs. Saved to {raw_lore_path}")

if __name__ == "__main__":
    scrape_wiki()
