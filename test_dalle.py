# test_dalle.py
import requests

url = "http://127.0.0.1:5000/api/dalle/generate"
headers = {
    "Content-Type": "application/json",
}

# 測試不同的色彩組合和場景
test_cases = [
    {
        "hex_list": ["#0E2148", "#483AA0", "#7965C1", "#E3D095"],
        "context": "ppt",
        "size": "512x512",
        "palette_name": "Ocean Breeze",
        "palette_description": "Cool and calm ocean colors"
    },
    {
        "hex_list": ["#FF6B35", "#F7931E", "#FFD23F", "#FFF1C1"],
        "context": "abstract",
        "size": "512x512",
        "palette_name": "Sunset Warmth",
        "palette_description": "Warm sunset gradient"
    },
    {
        "hex_list": ["#2D5016", "#518235", "#7FB069"],
        "context": "nature",
        "palette_name": "Forest Green",
        "palette_description": "Natural forest tones"
    },
    {
        "hex_list": ["#FF0000", "#00FF00", "#0000FF"],
        "context": "geometric",
        "palette_name": "Primary Colors"
    }
]

for i, data in enumerate(test_cases, 1):
    print(f"\n=== Test Case {i} ===")
    print(f"Colors: {data['hex_list']}")
    print(f"Context: {data['context']}")
    print(f"Name: {data.get('palette_name', 'N/A')}")
    
    resp = requests.post(url, json=data, headers=headers)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"Success! Generated image")
        print(f"Prompt: {result.get('prompt', 'N/A')}")
        print(f"Image URL length: {len(result.get('url', ''))}")
    else:
        error_data = resp.json()
        print(f"Error: {error_data}")

# 測試錯誤情況
print(f"\n=== Error Test Cases ===")

error_cases = [
    {"context": "ppt"},  # Missing hex_list
    {"hex_list": [], "context": "ppt"},  # Empty hex_list
    {"hex_list": ["invalid"], "context": "ppt"},  # Invalid color format
    {"hex_list": ["#FF0000"], "context": ""},  # Empty context
]

for i, data in enumerate(error_cases, 1):
    print(f"\nError Test {i}: {data}")
    resp = requests.post(url, json=data, headers=headers)
    print(f"Status: {resp.status_code}, Response: {resp.json()}")