from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from search_engine import SearchEngine

app = FastAPI()

templates = Jinja2Templates(directory="templates")

search_engine = SearchEngine()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search")
def search(q: str = Query(...)):

    results = search_engine.search(q)

    return results