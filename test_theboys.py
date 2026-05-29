import urllib.request
import json
import urllib.parse

def test_search(title, type_str):
    url = f"https://v3-cinemeta.strem.io/catalog/{type_str}/top/search={urllib.parse.quote(title)}.json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            data = json.loads(body)
            print(f"=== TYPE: {type_str} ===")
            if data and 'metas' in data and len(data['metas']) > 0:
                for idx, m in enumerate(data['metas'][:3]):
                    print(f"{idx+1}: Name: \"{m.get('name')}\", Year: \"{m.get('releaseInfo') or m.get('year')}\", Type: \"{m.get('type')}\", ID: \"{m.get('id')}\"")
            else:
                print("No metas found.")
    except Exception as e:
        print("Error:", e)

test_search("The Boys", "movie")
test_search("The Boys", "series")
