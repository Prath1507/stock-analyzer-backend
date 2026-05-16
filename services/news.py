import requests
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET


def get_stock_news(stock: str):

    try:
        # =========================
        # MULTIPLE QUERY FALLBACKS
        # =========================
        queries = [
            f"{stock} NSE",
            f"{stock} stock India",
            f"{stock} pharma India",
            f"{stock} share price"
        ]

        all_news = []

        for q in queries:

            url = f"https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-IN&gl=IN&ceid=IN:en"

            response = requests.get(url, timeout=10)

            root = ET.fromstring(response.content)

            items = root.findall(".//item")

            for item in items:
                title = item.find("title")
                link = item.find("link")
                pubDate = item.find("pubDate")

                if title is not None and link is not None:

                    news_item = {
                        "title": title.text,
                        "link": link.text,
                        "published": pubDate.text if pubDate is not None else None
                    }

                    # avoid duplicates
                    if news_item not in all_news:
                        all_news.append(news_item)

                if len(all_news) >= 8:
                    break

            if len(all_news) >= 8:
                break

        # =========================
        # SAFE FALLBACK
        # =========================
        if len(all_news) == 0:
            return [
                {
                    "title": f"No recent news found for {stock}",
                    "link": None,
                    "published": None
                }
            ]

        return all_news[:8]

    except Exception as e:
        return [
            {
                "title": "News system error - fallback activated",
                "link": None,
                "published": None
            }
        ]