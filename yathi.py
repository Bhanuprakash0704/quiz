from flask import Flask, request, render_template_string
import pandas as pd
import random
import os

app = Flask(__name__)

# Global variable to store shuffled questions
shuffled_questions = []

# Automatically detect if the app is running on PythonAnywhere

    # Path for PythonAnywhere
file_path = './myfile.xlsx'

    # # Path for local development (change this to your local file path)
    # file_path = r"C:\Users\aitha\OneDrive\Desktop\Quick_APP\9 sem-Infection diseases-Open.xlsx"

print(f"Using file path: {file_path}")

# Function to load the quiz data
def load_quiz_data(file_path):
    global shuffled_questions
    print(f"Checking if file exists: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: The file at {file_path} was not found.")
        return

    try:
        # Load the Excel file and print its sheet names for debugging
        print("Attempting to load the Excel file...")
        xls = pd.ExcelFile(file_path, engine="openpyxl")
        print(f"Sheet names in the Excel file: {xls.sheet_names}")  # Debugging - check sheet names

        if "200" not in xls.sheet_names:
            print("Error: The sheet '200' is not present in the file.")
            return

        # Load the specific sheet
        sheet_data = pd.read_excel(file_path, sheet_name="200")
        print(f"Sheet '200' loaded. First few rows:\n{sheet_data.head()}")  # Print first few rows of the sheet for debugging

        # Adjusted row limit to load data from row 1 to row 200 (inclusive)
        quiz_data = sheet_data.iloc[1:201, 1:7]  # Changed to load rows 1–200
        print(f"Extracted quiz data (first 5 rows):\n{quiz_data.head()}")  # Display first few rows of quiz data

        # Ensure the data has enough rows
        if quiz_data.shape[0] == 0:
            print("Error: No quiz data found in the specified range.")
            return

        # Rename columns to match the options
        quiz_data.columns = ["Question", "Option1", "Option2", "Option3", "Option4", "Option5"]
        quiz_data = quiz_data.reset_index(drop=True)

        # Shuffle options for each question while keeping labels consistent
        shuffled_questions = []
        for i in range(len(quiz_data)):
            options = [
                ("A", quiz_data.loc[i, "Option1"]),
                ("B", quiz_data.loc[i, "Option2"]),
                ("C", quiz_data.loc[i, "Option3"]),
                ("D", quiz_data.loc[i, "Option4"]),
                ("E", quiz_data.loc[i, "Option5"]),
            ]
            random.shuffle(options)
            shuffled_questions.append({
                "question": quiz_data.loc[i, "Question"],
                "options": options,
                "correct_answer": quiz_data.loc[i, "Option1"],  # Assuming Option1 is the correct answer
                "question_id": i,
            })
        
        # Debugging: Print the number of questions loaded
        print(f"Loaded {len(shuffled_questions)} questions.")
        
        # If no questions were loaded, print an error
        if len(shuffled_questions) == 0:
            print("Error: No questions were loaded.")
    except Exception as e:
        print(f"Error while processing the file: {e}")

# Call the function to load the data initially
load_quiz_data(file_path)

@app.route("/", methods=["GET", "POST"])
def quiz():
    global shuffled_questions
    try:
        # Check if shuffled_questions is populated
        if not shuffled_questions:
            return "Quiz data not loaded properly. Please check the file or initialization process."

        # Debugging: Print shuffled_questions to ensure it is being passed to the template
        print(f"Shuffled Questions: {shuffled_questions}")

        if request.method == "POST":
            user_answers = request.form
            score = 0
            results = []

            # Loop through shuffled questions and check the answers
            for question in shuffled_questions:
                correct_answer = question["correct_answer"]
                user_answer = user_answers.get(f"q{question['question_id']}")
                results.append({
                    "question": question["question"],
                    "options": question["options"],
                    "correct_answer": correct_answer,
                    "user_answer": user_answer,
                })
                if user_answer == correct_answer:
                    score += 1

            # Render the result page with score and results using render_template_string
            result_html = '''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Quiz Results</title>
                    <style>
                        .correct { color: green; }
                        .wrong { color: red; }
                    </style>
                </head>
                <body>
                    <h1>Quiz Results</h1>
                    <p>Your Score: {{ score }} / {{ total }}</p>
                    <hr>
                    {% for result in results %}
                        <div>
                            <p><strong>{{ result.question }}</strong></p>
                            <ul>
                                {% for label, option in result.options %}
                                    <li
                                        {% if option == result.correct_answer %}
                                            class="correct"
                                        {% elif option == result.user_answer and result.user_answer != result.correct_answer %}
                                            class="wrong"
                                        {% endif %}
                                    >
                                        {{ label }}. {{ option }}
                                    </li>
                                {% endfor %}
                            </ul>
                        </div>
                        <hr>
                    {% endfor %}
                    <a href="/">Take Quiz Again</a>
                </body>
                </html>
            '''
            return render_template_string(result_html, results=results, score=score, total=len(shuffled_questions))

        # If GET request, render the quiz with shuffled questions using render_template_string
        quiz_html = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Quiz</title>
        </head>
        <body>
            <h1>Quiz</h1>
            <form method="POST">
                {% for question in shuffled_questions %}
                    <div>
                        <p><strong>Q{{ loop.index }}:</strong> {{ question['question'] }}</p>
                        {% for label, option in question['options'] %}
                            <label>
                                <input type="radio" name="q{{ question['question_id'] }}" value="{{ option }}" required> 
                                {{ label }}. {{ option }}
                            </label><br>
                        {% endfor %}
                    </div>
                    <hr>
                {% endfor %}
                <button type="submit">Submit</button>
            </form>
        </body>
        </html>
        '''
        return render_template_string(quiz_html, shuffled_questions=shuffled_questions)

    except Exception as e:
        print(f"Error during quiz handling: {e}")
        return f"An error occurred: {e}"

if __name__ == "__main__":
    app.run(debug=True, port=5003)  # Or any other available port
