import urllib.request
import json

try:
    url = "http://213.21.240.78:8081/verify?uid=PO122004705"
    print(f"Pinging {url}...")
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode())
        print("Response for PO122004705:", data)
except Exception as e:
    print(f"Error checking PO122004705: {e}")

try:
    url = "http://213.21.240.78:8081/verify?uid=122004705"
    print(f"Pinging {url}...")
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode())
        print("Response for 122004705:", data)
except Exception as e:
    print(f"Error checking 122004705: {e}")
