import requests
import json
url = "https://fake-detector-n4ca.onrender.com/predict-news"
res = requests.post(url, json={"text": "hello world"})
print(res.text)
