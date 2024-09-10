import json
import os
from openai import AzureOpenAI
import base64

client = AzureOpenAI(
    azure_endpoint='https://dietplan.openai.azure.com/',
    api_key="25f39bc49c8b4e259aeba01405e9714a",
    api_version="2023-10-01-preview"
)

deployment = 'gpt4o'

MAX_QUESTIONS = 20

def decode_data(encoded_data):
    return json.loads(base64.b64decode(encoded_data).decode('utf-8'))

def analyze_profile_completeness(encoded_qa_data, encoded_chat_history):
    qa_data = decode_data(encoded_qa_data)
    chat_history = decode_data(encoded_chat_history)

    if len(chat_history) // 2 >= MAX_QUESTIONS:
        return "COMPLETE"

    prompt = f"""
    You are an expert nutritionist analyzing a user profile for a personalized diet plan. Based on the following Q&A information we've gathered so far and the chat history, determine if the profile is complete or if we need more information:

    Current Q&A data:
    {json.dumps(qa_data, indent=2)}

    Chat history:
    {json.dumps(chat_history, indent=2)}

    If the profile is complete, respond with "COMPLETE". Otherwise, generate a new question to ask the user that will help complete the profile. The question should be:
    1. Relevant and personalized based on previous answers and chat history
    2. Different from any questions already asked
    3. Designed to gather more in-depth information for creating a comprehensive diet plan
    4. Focused on dietary preferences, allergies, medical conditions, lifestyle, exercise habits, stress levels, sleep patterns, or previous diet experiences if not already covered
    5. Specific and targeted to uncover important details
    6. Phrased in a friendly and conversational manner
    7. Prioritize the most important questions first to ensure the most essential information is collected efficiently
    8. Always ask about the user’s food preferences, specifically what they like to eat and what they don't like to eat, if that information hasn’t been gathered yet


    Provide only "COMPLETE" or the new question without any additional text.
    """

    messages = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(model=deployment, messages=messages, max_tokens=100)

    return completion.choices[0].message.content.strip()

def get_clarification(question, clarification_prompt, encoded_chat_history):
    chat_history = decode_data(encoded_chat_history)

    prompt = f"""
    You are an expert nutritionist creating a detailed user profile for a personalized diet plan. The user has asked for clarification about a question you asked:

    Original question: {question}
    User's clarification request: {clarification_prompt}

    Chat history:
    {json.dumps(chat_history, indent=2)}

    Provide a clear and helpful explanation to address the user's request for clarification. Your response should be:
    1. Directly related to the user's specific clarification request
    2. Informative and easy to understand
    3. Helpful in guiding the user to provide the information needed for their diet plan
    4. Friendly and encouraging

    Provide only the clarification response without any additional text.
    """

    messages = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(model=deployment, messages=messages, max_tokens=150)

    return completion.choices[0].message.content.strip()

if __name__ == "__main__":
    import sys
    
    if sys.argv[1] == "analyze_profile_completeness":
        print(analyze_profile_completeness(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "get_clarification":
        print(get_clarification(sys.argv[2], sys.argv[3], sys.argv[4]))