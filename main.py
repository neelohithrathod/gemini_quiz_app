
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
    f"Generate a quiz set of 40 questions about '{topic}' in strict JSON format. "
    "Each question should follow this predefined JSON response: "
    "{q, correctans, ans1, ans2, ans3, backstory}. "
    "Return only the JSON array, no extra text."
)


# Send prompt to Gemini Flash
# model = genai.GenerativeModel("gemini-2.5-flash")
model = genai.GenerativeModel("gemini-2.5-pro")

response = model.generate_content(prompt)

# Extract JSON from response, handling code blocks and extra text
import re
def extract_json(text):
    # Remove code block markers if present
    text = text.strip()
    if text.startswith('```json'):
        text = text[7:]
    if text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    # Find first [ and last ] for JSON array
    match = re.search(r'(\[.*\])', text, re.DOTALL)
    if match:
        return match.group(1)
    return text

json_text = extract_json(response.text)

# Parse and display questions

import json

try:
    from termcolor import colored
except ImportError:
    def colored(text, *args, **kwargs):
        return text

try:
    quiz_set = json.loads(json_text)
    if not isinstance(quiz_set, list):
        raise ValueError("Quiz set is not a list. Raw response: " + str(json_text))
    for idx, q in enumerate(quiz_set, 1):
        print(colored("\n" + "="*60, 'blue'))
        print(colored(f"Q{idx}: {q.get('q', 'No question provided')}", 'cyan', attrs=['bold']))
        print(colored(f"  1. {q.get('ans1', '-')}", 'yellow'))
        print(colored(f"  2. {q.get('ans2', '-')}", 'yellow'))
        print(colored(f"  3. {q.get('ans3', '-')}", 'yellow'))
        print(colored(f"  Correct Answer: {q.get('correctans', '-')}", 'green', attrs=['bold']))
        print(colored(f"  Backstory: {q.get('backstory', '-')}", 'magenta'))
        print(colored("="*60, 'blue'))
except Exception as e:
    print(colored("Failed to parse or display quiz:", 'red', attrs=['bold']))
    print(e)
    print(colored("Raw response:", 'red'))
    print(json_text)