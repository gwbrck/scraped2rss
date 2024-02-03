from fastapi import FastAPI
from .routes import overview, log, targets

app = FastAPI()

# Include routers from the routes module
app.include_router(overview.router)
app.include_router(log.router)
app.include_router(targets.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Real-time Scraping API"}
