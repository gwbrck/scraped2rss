from fastapi import APIRouter, Response
from ..scraping import scraper_registry

router = APIRouter()


def create_route_function(name, scraper_class):

    async def dynamic_route():
        scraper_instance = scraper_class()
        data = await scraper_instance.scrape()
        return Response(content=data, media_type="application/rss+xml")

    return dynamic_route


def register_dynamic_routes():
    for name, scraper_class in scraper_registry.get_all_scrapers().items():
        route_function = create_route_function(name, scraper_class)
        router.add_api_route(f"/run/{name}",
                             route_function,
                             response_class=Response,
                             methods=["GET"])


register_dynamic_routes()
