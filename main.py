from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import re
import unidecode

app = FastAPI()

def normalize_name(name: str):
    name = unidecode.unidecode(name)
    name = name.lower().replace(" ", "-")
    return name

@app.get("/value")
def get_market_value(player: str = Query(...)):
    try:
        name_url = normalize_name(player)
        url = f"https://www.transfermarkt.com/{name_url}/profil/spieler"
        headers = {'User-Agent': 'Mozilla/5.0'}

        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")

        value_element = soup.find("div", class_="dataMarktwert")
        if value_element:
            value = value_element.get_text(strip=True)
            return {"player": player, "value": value}

        return JSONResponse(status_code=404, content={"error": "Value not found"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
