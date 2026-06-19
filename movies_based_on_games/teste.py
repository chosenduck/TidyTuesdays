import requests
from utils.constants import TMDB_API_KEY, TMDB_SEARCH_URL

r = requests.get(TMDB_SEARCH_URL, params={
    "api_key": TMDB_API_KEY,
    "query": "Resident Evil: The Final Chapter",
    "language": "en-US",
    "year": 2017,
})

for i, resultado in enumerate(r.json()["results"][:5]):
    print(f"{i+1}. id={resultado['id']} | {resultado['title']} ({resultado.get('release_date', '?')}) | poster={resultado.get('poster_path')}")