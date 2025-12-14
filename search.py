import requests

GOOGLE_API_KEY = "AIzaSyAcuGIz4sDObUNuy4JGrMRmfCN-pYXInYs"
GOOGLE_CSE_ID = "033faded5246a48a1"

def google_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "q": query}
    try:
        res = requests.get(url, params=params).json()
        items = res.get("items", [])
        return items[0]["link"] if items else None
    except:
        return None
