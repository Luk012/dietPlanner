import requests
import json

subscription_key = "22a07174f6fd4ab49af70404259f51b2"
endpoint = "https://visiondiet.cognitiveservices.azure.com/"

image_path = "/Users/luk012/Downloads/chargrilled-fish-with-green-chilli-coriander-and-coconut-relish-70446-1.jpeg"

analyze_url = f"{endpoint}/vision/v3.2/analyze"

params = {
    'visualFeatures': 'Description,Tags,Objects,Categories,Color',
    'language': 'en'
}

headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-Type': 'application/octet-stream'
}

with open(image_path, "rb") as image_file:
    image_data = image_file.read()
    response = requests.post(analyze_url, headers=headers, params=params, data=image_data)

response.raise_for_status()

analysis = response.json()

main_description = analysis["description"]["captions"][0]["text"]

food_tags = [tag['name'] for tag in analysis.get('tags', [])]

food_objects = [
    {"name": obj["object"], "confidence": obj["confidence"], "bounding_box": obj["rectangle"]}
    for obj in analysis.get("objects", [])
]

categories = [category["name"] for category in analysis.get("categories", [])]

dominant_colors = analysis.get("color", {}).get("dominantColors", [])

detailed_description = f"Main Description: {main_description}.\n"
detailed_description += f"Detected Categories: {', '.join(categories)}.\n"
detailed_description += f"Identified Food Tags: {', '.join(food_tags)}.\n"

detailed_description += "Detected Objects:\n"
for obj in food_objects:
    bbox = obj['bounding_box']
    area = bbox['w'] * bbox['h']
    detailed_description += (
        f"  - {obj['name']} with confidence {obj['confidence']:.2f}, "
        f"covering an area of {area} pixels (bounding box: x={bbox['x']}, y={bbox['y']}, "
        f"width={bbox['w']}, height={bbox['h']}).\n"
    )

detailed_description += f"Dominant Colors: {', '.join(dominant_colors)}."

print(f"Detailed Description of the image:\n{analysis}")