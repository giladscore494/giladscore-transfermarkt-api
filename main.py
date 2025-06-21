from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/value")
def get_market_value(player: str = Query(...)):
    try:
        query = f"{player} site:transfermarkt.com"
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://www.google.com/search?q={query}"
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if "transfermarkt" in href and "/profil/" in href:
                link = href.split("/url?q=")[-1].split("&")[0]
                page = requests.get(link, headers=headers)
                soup = BeautifulSoup(page.text, "html.parser")
                val = soup.find("div", class_="dataMarktwert")
                if val:
                    return {"player": player, "value": val.text.strip()}
        return JSONResponse(status_code=404, content={"error": "Value not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
