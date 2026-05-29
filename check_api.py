import urllib.request, json
url = "http://116.203.230.103/api/details/movie/tt1190634?lang=en"
try:
    data = json.loads(urllib.request.urlopen(url).read())
    omdb = data.get('omdb')
    print("Type of OMDB:", type(omdb))
    if isinstance(omdb, str):
        print("OMDB starts with:", omdb[:50])
    else:
        print("OMDB keys:", omdb.keys() if omdb else "None")
except Exception as e:
    print("Error:", e)
