import urllib.request
try:
    response = urllib.request.urlopen("https://api.ipify.org")
    print("My IP:", response.read().decode())
except Exception as e:
    print(e)
