from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

app = FastAPI()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
}

def find_transfermarkt_url(player_name: str):
    query = f"site:transfermarkt.com {player_name} profile"
    with DDGS() as ddgs:
        results = ddgs.text(query)
        for r in results:
            if "/profil/spieler/" in r.get("href", ""):
                return r["href"]
    return None

def extract_market_value(player_url: str):
    res = requests.get(player_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    mv_tag = soup.find("div", class_="dataMarktwert")
    if mv_tag:
        return mv_tag.text.strip()
    return None

@app.get("/value")
def get_market_value(player: str = Query(...)):
    try:
        url = find_transfermarkt_url(player)
        if not url:
            return JSONResponse(status_code=404, content={"error": "Player not found"})

        value = extract_market_value(url)
        if not value:
            return JSONResponse(status_code=404, content={"error": "Value not found"})

        return {"player": player, "value": value}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

