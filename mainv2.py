import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
from pymongo import MongoClient
import json
import re

# Load environment variables from .env
load_dotenv()
# Set your Gemini API key
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# MongoDB settings from env
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "gemini_quiz_db")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "quizzes")

# Ask user for topic
topic = input("Enter the topic for your quiz: ")

# Define the prompt - ask Gemini to return the Mongo-ready shape
prompt = (
    f"Generate a quiz set of 40 questions about '{topic}' in strict JSON format. "
    "Return a JSON array where each item is an object with these fields: "
    "\"qid\" (string), \"question\" (string), \"category\" (string), "
    "\"options\" (array of strings), \"correct_index\" (integer index into options), "
    "\"backstory\" (string). Return only the JSON array, no extra text or code blocks."
)

# Send prompt to Gemini Flash / Pro
# model = genai.GenerativeModel("gemini-2.5-flash")
model = genai.GenerativeModel("gemini-2.5-pro")

response = model.generate_content(prompt)

# Extract JSON from response, handling code blocks and extra text
def extract_json(text):
    text = text.strip()
    if text.startswith('```json'):
        text = text[7:]
    if text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    match = re.search(r'(\[.*\])', text, re.DOTALL)
    if match:
        return match.group(1)
    return text

json_text = extract_json(response.text)

# Fallback colored function if termcolor not installed
try:
    from termcolor import colored
except ImportError:
    def colored(text, *args, **kwargs):
        return text

# Parse, normalize, and insert into MongoDB
try:
    quiz_set = json.loads(json_text)
    if not isinstance(quiz_set, list):
        raise ValueError("Quiz set is not a list. Raw response: " + str(json_text))

    # Connect to MongoDB if URI provided
    client = None
    db = None
    coll = None
    if MONGODB_URI:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DB]
        coll = db[MONGODB_COLLECTION]

    docs_to_insert = []
    base_qnum = 100  # qid will be q100, q101, ...

    for idx, item in enumerate(quiz_set, 1):
        # Accept both new schema and older schema variations
        # Normalize question text
        question_text = item.get("question") or item.get("q") or item.get("prompt") or "No question provided"

        # Category fallback
        category = item.get("category") or item.get("cat") or topic or "general"

        # Options: prefer explicit "options" array; otherwise gather ans1..ans5
        options = item.get("options")
        if not options:
            options = []
            for i in range(1, 6):
                v = item.get(f"ans{i}")
                if v:
                    options.append(v)
        # If still empty, try to split option-like string (not implemented here)
        if not options:
            options = ["A", "B", "C", "D"]

        # Determine correct_index
        if "correct_index" in item and isinstance(item.get("correct_index"), int):
            correct_index = item.get("correct_index")
        else:
            correct_ans = item.get("correctans") or item.get("answer") or item.get("correct") or ""
            correct_index = 0
            try:
                if correct_ans:
                    # If correct_ans is e.g. "A" or "1", try to map letters/numbers to index
                    if isinstance(correct_ans, str) and correct_ans.strip().upper() in ["A","B","C","D","E"]:
                        letter = correct_ans.strip().upper()
                        correct_index = ord(letter) - ord("A")
                    else:
                        correct_index = options.index(correct_ans)
                # clamp to valid range
                if correct_index < 0 or correct_index >= len(options):
                    correct_index = 0
            except ValueError:
                correct_index = 0

        backstory = item.get("backstory") or item.get("explanation") or ""

        qid = item.get("qid") or f"q{base_qnum + idx - 1}"

        doc = {
            "qid": qid,
            "question": question_text,
            "category": category,
            "options": options,
            "correct_index": int(correct_index),
            "backstory": backstory,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        docs_to_insert.append(doc)

        # Print to console
        print(colored("\n" + "="*60, 'blue'))
        print(colored(f"Q{idx} ({qid}): {doc['question']}", 'cyan', attrs=['bold']))
        for i, opt in enumerate(options, 1):
            prefix = "*" if (i-1) == doc["correct_index"] else " "
            print(colored(f" {prefix} {i}. {opt}", 'yellow'))
        print(colored(f"  Backstory: {doc['backstory']}", 'magenta'))
        print(colored("="*60, 'blue'))

    # Insert into MongoDB
    if coll and docs_to_insert:
        try:
            result = coll.insert_many(docs_to_insert)
            print(colored(f"Inserted {len(result.inserted_ids)} documents into {MONGODB_DB}.{MONGODB_COLLECTION}", 'green'))
        except Exception as e:
            print(colored("MongoDB insert failed: " + str(e), 'red'))
    else:
        if not MONGODB_URI:
            print(colored("MONGODB_URI not set; skipping DB insert.", 'yellow'))

except Exception as e:
    print(colored("Failed to parse or display quiz:", 'red', attrs=['bold']))
    print(e)
    print(colored("Raw response:", 'red'))
    print(json_text)