from datetime import datetime, timezone, timedelta
import requests
from feedgen.feed import FeedGenerator
from feedgen.entry import FeedEntry
import feedgen.util
from fastapi import FastAPI
from fastapi.responses import Response


link = "https://www.tuxedocomputers.com/index.php?module=tuxedoList&type=api"
head = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Content-Type": "application/json;charset=utf-8",
    "Cookie": "cookieconsent_status=dismiss; HHGsid=n420f23khpj2ikn7tghs674jg6; HHGsid=g1bobf9f33otm7salptkl9q2td",
    "DNT": "1",
    "Origin": "https://www.tuxedocomputers.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0"
}

json = {
    "filter_id": "1532",
    "sort_1": "p.products_sort",
    "sort_2": "DESC",
    "filter": "category",
    "SEQ_TOKEN_12b75eef7c0bebf9f89580399a2d1fa7": "8ec05210e9934600664283cc8a283ac3",
    "return": "ZGUvSW5mb3MvTmV3cy50dXhlZG8=",
    "keywords": ""
}


def getTuxedoFeed(url, headers, data) -> FeedGenerator:
    response = requests.post(url, headers=headers, json=data, timeout=60)
    parsed = response.json()
    f = FeedGenerator()
    f.title('Tuxedo News')
    f.link(href='https://www.tuxedocomputers.com/de/Infos/News.tuxedo')
    f.description('Scraped Newsfeed from Tuxedo')

    for i in range(0, 10):
        e = FeedEntry()
        e.link(href=parsed['list'][i]['product']['link'])
        e.description(parsed['list'][i]['product']['data']['products_short_description'])
        e.content(parsed['list'][i]['product']['data']['products_description'])
        d = datetime.strptime(
            parsed['list'][i]['product']['data']['products_date_added'],
            "%Y-%m-%d %H:%M:%S"
        )
        dtz = d.replace(tzinfo=timezone(timedelta(hours=1), 'CET'))
        e.pubDate(feedgen.util.formatRFC2822(dtz))
        e.title(parsed['list'][i]['product']['data']['products_heading_title'])
        f.add_entry(e)

    return f


app = FastAPI()


@app.get('/tuxedo')
def rss_feed():
    rss_feed_xml = getTuxedoFeed(link, head, json).rss_str(pretty=True)
    return Response(content=rss_feed_xml, media_type='application/xml')
