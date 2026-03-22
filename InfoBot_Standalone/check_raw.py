import urllib.request
try:
    url = "http://213.21.240.78:8081/verify?uid=122004705"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        raw_data = response.read().decode('utf-8')
        print("RAW RESPONSE:", repr(raw_data))
except Exception as e:
    print(f"Error checking: {e}")
