from ..scraping import BaseScraper, scraper
import httpx
from datetime import datetime, timezone, timedelta


@scraper(name='tuxedo-news')
class TuxedoNewsScraper(BaseScraper):

    async def scrape(self):
        link = "https://www.tuxedocomputers.com/index.php?module=tuxedoList&type=api"
        headers = {
            "Accept": "application/json, text/plain, */*",
        }

        data = {
            "filter_id": "1532",
            "sort_1": "p.products_sort",
            "sort_2": "DESC",
            "filter": "category",
            "SEQ_TOKEN_12b75eef7c0bebf9f89580399a2d1fa7":
            "8ec05210e9934600664283cc8a283ac3",
            "return": "ZGUvSW5mb3MvTmV3cy50dXhlZG8="
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(link,
                                             headers=headers,
                                             json=data,
                                             timeout=60)
                response.raise_for_status()
                parsed = response.json()
                modified_entries = []
                for item in parsed.get('list', [])[:10]:
                    link = item['product']['link']

                    description = item['product']['data'][
                        'products_short_description']
                    content = item['product']['data']['products_description']

                    d = datetime.strptime(
                        item['product']['data']['products_date_added'],
                        "%Y-%m-%d %H:%M:%S")
                    published = d.replace(
                        tzinfo=timezone(timedelta(hours=1), 'CET'))

                    title = item['product']['data'][
                        'products_heading_title'] or item['product']['data'][
                            'products_name']
                    modified_entries.append({
                        'link': link,
                        'description': description,
                        'content': content,
                        'published': published,
                        'title': title
                    })

                return self.toRss(
                    "Tuxedo News", "Scraped Newsfeed from Tuxedo",
                    "https://www.tuxedocomputers.com/de/Infos/News.tuxedo",
                    modified_entries)

            except httpx.HTTPStatusError as e:
                self.logger.error(f"HTTP error occurred: {e}")
            except httpx.RequestError as e:
                self.logger.error(
                    f"An error occurred while requesting {e.request.url!r}.")
            except ValueError as e:
                self.logger.error(f"Error: {e}")
