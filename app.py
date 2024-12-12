from flask import Flask, jsonify, render_template
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

BASE_URL = "https://mashable.com"  # Base URL for constructing relative links
SITEMAP_URL = "https://mashable.com/sitemap/2022/1"  # Correct URL for the sitemap

@app.route('/api/scrape')
def scrape():
    try:
        response = requests.get(SITEMAP_URL)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []

        # Select articles based on the structure
        for article in soup.select('li.mt-2'):
            # Extract date
            date_element = article.select_one('span.inline-block.w-full.lg\\:w-28')
            if not date_element:
                continue
            raw_date = date_element.get_text(strip=True)
            try:
                # Parse date into YYYY-MM-DD format
                date = datetime.strptime(raw_date, "%m/%d/%Y").strftime("%Y-%m-%d")
            except ValueError:
                continue

            # Extract title and link
            title_element = article.select_one('a.inline-block.text-gray-dark')
            if not title_element or 'href' not in title_element.attrs:
                continue
            title = title_element.get_text(strip=True)
            link = title_element['href']

            # Add the base domain if the link is relative
            if not link.startswith('http'):
                link = f"{BASE_URL}{link}"

            # Include only articles published on or after January 1, 2022
            if datetime.strptime(date, "%Y-%m-%d") >= datetime(2022, 1, 1):
                articles.append({
                    "title": title,
                    "link": link,
                    "date": date
                })

        # Sort articles in reverse chronological order
        articles.sort(key=lambda x: x['date'], reverse=True)

        return jsonify(articles)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
