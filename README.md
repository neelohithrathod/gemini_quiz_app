# Gemini Quiz App

A simple Python CLI app that generates a set of 10 quiz questions on a topic of your choice using Google's Gemini Flash API, and displays them in a colorized, readable format in your terminal.

## Features
- Prompts user for quiz topic
- Fetches quiz questions from Gemini Flash API
- Pretty prints questions, answers, correct answer, and backstory
- Uses `.env` for API key management

## Setup

1. **Clone the repository** (if not already):
   ```sh
   git clone <repo-url>
   cd gemini_quiz_app
   ```

2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
   Ensure `termcolor` and `python-dotenv` are included in `requirements.txt`.

3. **Set up your `.env` file**:
   Create a `.env` file in the project root with:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## Usage

Run the app:
```sh
python main.py
```

- Enter your desired quiz topic when prompted.
- The app will display 10 questions with options, correct answer, and backstory in the terminal.

## Example
```
Enter the topic for your quiz: Solar System

============================================================
Q1: What is the largest planet in our Solar System?
  1. Saturn
  2. Neptune
  3. Earth
  Correct Answer: Jupiter
  Backstory: Jupiter is so massive that it is more than twice as massive as all the other planets in our Solar System combined.
============================================================
```

## Notes
- Requires a valid Google Gemini API key.
- Works best in terminals that support ANSI colors.

## Contributors
-Neelohith Rathod
-AmarjithTK
