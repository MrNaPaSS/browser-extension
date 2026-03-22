import urllib.request
import json
try:
    url = "http://213.21.240.78:8081/verify?uid=PO122004705"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode())
        print("Success!", data)
except Exception as e:
    print(f"Error checking: {e}")
