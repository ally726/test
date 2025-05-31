# test_dalle.py
import os, requests
TOKEN = os.environ["TOKEN"]
url = "http://127.0.0.1:5000/api/dalle/generate"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}
data = {"palette_id":1,"context":"ppt","size":"512x512"}
resp = requests.post(url, json=data, headers=headers)
print(resp.status_code, resp.json())
