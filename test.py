from keys import ameritrade
import requests

url = "https://api.tdameritrade.com/v1/instruments"
payload = {
    "apikey": ameritrade,
    "symbol": "GS",
    "projection": "fundamental"
}

result = requests.get(url, params=payload)
print(result.json())