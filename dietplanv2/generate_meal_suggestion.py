import json
import os
from openai import AzureOpenAI
import time

client = AzureOpenAI(
    azure_endpoint='https://dietplan.openai.azure.com/',
    api_key="25f39bc49c8b4e259aeba01405e9714a",
    api_version="2023-10-01-preview"
)

deployment = 'gpt4o'

def load_user_qa():
    with open('user_qa.json', 'r') as f:
        return json.load(f)

def read_meal_request():
    with open('meal_request.txt', 'r') as f:
        return json.load(f)

def generate_meal_suggestion(meal_type, user_message, user_qa):
    prompt = f"""
    Based on the following user profile Q&A, suggest a {meal_type} meal:
    
    {json.dumps(user_qa, indent=2)}
    User's request: {user_message}
    
    Please follow these guidelines:
    1. Carefully consider the user's dietary preferences, restrictions, and allergies mentioned in their Q&A.
    2. If the user requests a food they're allergic to or they don't like, suggest a safe and suitable alternative that aligns with their dietary needs.
    3. Ensure the meal suggestion is diverse from previous recommendations.
    4. Tailor the meal to the user's health goals and nutritional requirements.
    5. Provide a detailed description of the meal, including ingredients and their quantities.
    6. Include nutritional information for the suggested meal.

    Generate an HTML snippet for the meal suggestion with the following structure:
    PLEASE PROVIDE ONLY THE CODE SNIPPET AS SHOWN BELOW WITHOUT ANY ADDITIONAL TEXT!
    
    <h1>Your {meal_type.capitalize()} Meal Plan</h1>
    <h2>Meal Suggestion: [Meal Name]</h2>
    <p class="description">[Brief description]</p>
    <h3>Main Ingredients:</h3>
    <ul>
        [List of ingredients with quantities]
    </ul>
    <h3>Nutritional Information:</h3>
    <ul>
        [List of key nutritional facts]
    </ul>
    <h3>How to Prepare:</h3>
    <ol>
        [Step-by-step instructions on how to prepare the meal]
    </ol>
    Ensure the HTML is well-formatted and the content is appropriate for the user's diet plan. PLEASE PROVIDE ONLY THE CODE SNIPPET AS SHOWN ABOVE WITHOUT ANY ADDITIONAL TEXT.
    """
    messages = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(model=deployment, messages=messages, max_tokens=700)
    meal_content = completion.choices[0].message.content

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your {meal_type.capitalize()} Meal Plan</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
            .meal-suggestion {{ max-width: 800px; margin: 0 auto; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .description {{ font-style: italic; color: #34495e; }}
            ul, ol {{ padding-left: 20px; }}
            ol li {{ margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="meal-suggestion">
            {meal_content}
        </div>
    </body>
    </html>
    """
    
    filename = f"meal_plan_{meal_type}_{int(time.time())}.html"
    
    with open(f"public/{filename}", "w") as f:
        f.write(html_content)
    
    return filename

def write_meal_suggestion(filename):
    with open('meal_suggestion.txt', 'w') as f:
        f.write(filename)

if __name__ == '__main__':
    user_qa = load_user_qa()
    meal_request = read_meal_request()
    filename = generate_meal_suggestion(meal_request['mealType'], meal_request['userMessage'], user_qa)
    write_meal_suggestion(filename)
    result = {
        "filename": filename,
        "message": "Meal suggestion generated and saved."
    }
    print(json.dumps(result))