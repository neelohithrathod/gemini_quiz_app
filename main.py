
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()
# Set your Gemini API key
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)


# Ask user for topic
topic = input("Enter the topic for your quiz: ")

# Define the prompt
prompt = (
    f"Generate a quiz set of 10 questions about '{topic}' in strict JSON format. "
    "Each question should follow this predefined JSON response: "
    "{q, correctans, ans1, ans2, ans3, backstory}. "
    "Return only the JSON array, no extra text."
)

# Send prompt to Gemini Flash
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content(prompt)

# Parse and display questions

import json
from pprint import pprint
from termcolor import colored

try:
    quiz_set = json.loads(response.text)
    for idx, q in enumerate(quiz_set, 1):
        print(colored(f"\nQ{idx}: {q['q']}", 'cyan', attrs=['bold']))
        print(colored(f"  1. {q['ans1']}", 'yellow'))
        print(colored(f"  2. {q['ans2']}", 'yellow'))
        print(colored(f"  3. {q['ans3']}", 'yellow'))
        print(colored(f"  Correct Answer: {q['correctans']}", 'green', attrs=['bold']))
        print(colored(f"  Backstory: {q['backstory']}", 'magenta'))
except Exception as e:
    print("Failed to parse response:", e)
    print("Raw response:", response.text)