import urllib.request
import json

req = urllib.request.urlopen("http://116.203.230.103/api/details/movie/tt1375666")
data = json.loads(req.read())
omdb = data.get('omdb')

print(f"Type of omdb: {type(omdb)}")
if isinstance(omdb, str):
    print("It's a string! Let's try parsing it.")
    try:
        parsed = json.loads(omdb)
        print("Parsed ratings:", parsed.get('Ratings'))
    except:
        print("Parse error")
else:
    print("Ratings:", omdb.get('Ratings') if omdb else "omdb is null")
