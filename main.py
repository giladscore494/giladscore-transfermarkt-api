from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def search_transfermarkt(player_name: str):
    search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={player_name}"
    res = requests.get(search_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    link_tag = soup.select_one("a.spielprofil_tooltip")
    if link_tag:
        relative_link = link_tag.get("href", "")
        player_url = f"https://www.transfermarkt.com{relative_link}"
        return player_url
    return None

def extract_market_value(player_url: str):
    res = requests.get(player_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    mv_tag = soup.find("div", class_="dataMarktwert")
    if mv_tag:
        value = mv_tag.text.strip()
        return value
    return None

@app.get("/value")
def get_market_value(player: str = Query(...)):
    try:
        url = search_transfermarkt(player)
        if not url:
            return JSONResponse(status_code=404, content={"error": "Player not found"})

        value = extract_market_value(url)
        if not value:
            return JSONResponse(status_code=404, content={"error": "Value not found"})

        return {"player": player, "value": value}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
