from fastapi import APIRouter
from ..scraping import scraper_registry

router = APIRouter()


@router.get("/overview", response_model=list)
async def get_overview():
    scraper_names = list(scraper_registry.get_all_scrapers().keys())
    return scraper_names
