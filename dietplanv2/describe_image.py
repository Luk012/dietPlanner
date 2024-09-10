import json
import base64
import os
import dotenv
from openai import AzureOpenAI

dotenv.load_dotenv()

client = AzureOpenAI(
    azure_endpoint='https://dietplan.openai.azure.com/',
    api_key="25f39bc49c8b4e259aeba01405e9714a",
    api_version="2023-10-01-preview"
)

deployment = 'gpt4o'

def describe_image(image_data):
   
    image_prompt = (
        "Tell me how many caloires does the following meal have:\n"
        f"[Image base64 data: {image_data}]"
    )


    messages = [
        {"role": "user", "content": image_prompt}
    ]
    completion = client.chat.completions.create(model=deployment, messages=messages, max_tokens=50, temperature=0.5)

    description = completion.choices[0].message.content.strip()

    return description

if __name__ == '__main__':
    with open('uploaded_image.txt', 'r') as file:
        image_data = file.read()

    description = describe_image(image_data)

    with open('image_description.json', 'w') as file:
        json.dump({'description': description}, file)
