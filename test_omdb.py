import urllib.request, json
url = "http://www.omdbapi.com/?i=tt0111161&apikey=25c26a4"
try:
    data = json.loads(urllib.request.urlopen(url).read())
    print("Ratings array:")
    print(data.get('Ratings', 'No Ratings'))
except Exception as e:
    print("Error:", e)
