import asyncio
from datetime import datetime, timezone
from ..scraping import BaseScraper, scraper
import httpx
import feedparser
from readability import Document
import os


@scraper(name='uebermedien')
class ScrapeUebermedien(BaseScraper):

    def __init__(self):
        super().__init__()
        self.ueber_token = os.getenv("UEBER_TOKEN")
        if self.ueber_token is None:
            self.logger.warning(
                "UEBER_TOKEN environment variable is not defined.")
        self.headers = {"Cookie": f"steady-token={self.ueber_token}"}

    async def getArticleEntry(self, client, link):
        try:
            await asyncio.sleep(0.2)
            response = await client.get(link, headers=self.headers)
            response.raise_for_status()
            doc = Document(response.content)
            return doc.summary()
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            self.logger.error(
                f"An error occurred while requesting {e.request.url!r}.")

    async def scrape(self):
        modified_entries = []
        self.logger.info(
            f"Starting scrape process for {self.__class__.__name__}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("https://uebermedien.de/feed/")
                response.raise_for_status()

                feed = feedparser.parse(response.text)
                if feed.bozo and feed.bozo_exception:
                    self.logger.error(
                        f"Failed to parse feed: {feed.bozo_exception}")
                    raise ValueError(
                        f"Failed to parse feed: {feed.bozo_exception}")

                for entry in feed.entries:
                    modified_entry = entry
                    modified_entry['published'] = datetime(
                        *entry['published_parsed'][:6], tzinfo=timezone.utc)
                    article_content = await self.getArticleEntry(
                        client, entry.link)
                    if article_content:
                        modified_entry['content'] = article_content
                    modified_entries.append(modified_entry)

                return self.toRss("Übermedien", "Übermedien berichtet, Überraschung: über Medien. Seit Anfang 2016 setzen wir uns kontinuierlich mit der Arbeit von Journalistinnen und Journalisten auseinander.",
                                  "https://uebermedien.de", modified_entries)
            except httpx.HTTPStatusError as e:
                self.logger.error(f"HTTP error occurred: {e}")
            except httpx.RequestError as e:
                self.logger.error(
                    f"An error occurred while requesting {e.request.url!r}.")
            except ValueError as e:
                self.logger.error(f"Error: {e}")
