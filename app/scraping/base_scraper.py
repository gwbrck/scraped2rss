import logging
from feedgen.feed import FeedGenerator
from feedgen.entry import FeedEntry
import feedgen.util


class ScraperRegistry:

    def __init__(self):
        self.scrapers = {}

    def register(self, name, scraper_class):
        self.scrapers[name] = scraper_class

    def get_scraper(self, name):
        return self.scrapers.get(name)

    def get_all_scrapers(self):
        return self.scrapers


def scraper(name):

    def decorator(cls):
        scraper_registry.register(name, cls)
        return cls

    return decorator


scraper_registry = ScraperRegistry()


class BaseScraper:

    def __init__(self):
        self.logger = logging.getLogger("uvicorn")

    async def scrape(self):
        raise NotImplementedError(
            "Die scrape-Methode muss in der abgeleiteten Klasse implementiert werden."
        )

    def toRss(self, title, description, link, items):
        f = FeedGenerator()
        f.title(title)
        f.link(href=link)
        f.id(link)
        f.description(description)

        for item in items:
            e = FeedEntry()

            e.id(id=item['link'])
            e.link(href=item['link'])

            if 'description' in item:
                e.description(item['description'])

            if 'content' in item:
                e.content(item['content'], type="CDATA")

            if 'title' in item:
                e.title(item['title'])

            if 'author' in item:
                e.author(name=item['author'])

            try:
                pub_date = feedgen.util.formatRFC2822(item['published'])
                e.pubDate(pub_date)
            except AttributeError:
                pass

            f.add_entry(e)

        return f.atom_str(pretty=True)
