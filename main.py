from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

PROXY_URL = "https://api.allorigins.win/get?url="

def proxy_get_html(url: str):
    proxied_url = PROXY_URL + requests.utils.quote(url, safe='')
    res = requests.get(proxied_url, headers=HEADERS)
    if res.status_code != 200:
        return None
    data = res.json()
    return data.get("contents", "")

def search_transfermarkt_url(player_name: str):
    query = f"site:transfermarkt.com {player_name} profile"
    duckduckgo_url = f"https://html.duckduckgo.com/html/?q={query}"
    html = proxy_get_html(duckduckgo_url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    results = soup.select("a.result__a")
    for tag in results:
        href = tag.get("href", "")
        if "transfermarkt.com" in href and "/profil/spieler/" in href:
            return href
    return None

def extract_market_value(player_url: str):
    html = proxy_get_html(player_url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    mv_tag = soup.find("div", class_="dataMarktwert")
    if mv_tag:
        return mv_tag.text.strip()
    return None

@app.get("/value")
def get_market_value(player: str = Query(...)):
    try:
        url = search_transfermarkt_url(player)
        if not url:
            return JSONResponse(status_code=404, content={"error": "Player not found"})

        value = extract_market_value(url)
        if not value:
            return JSONResponse(status_code=404, content={"error": "Value not found"})

        return {"player": player, "value": value}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
