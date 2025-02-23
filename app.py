from flask import Flask, request, jsonify, send_from_directory
import os
from groq import Groq
from flask_cors import CORS  # Import CORS
import re  # For regex parsing

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Hardcoded Groq API key
GROQ_API_KEY = "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"

@app.route('/')
def home():
    # Serve the index.html file from the root directory
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/get-suggestions', methods=['POST'])
def get_suggestions():
    # Log the incoming request data for debugging
    print("Incoming request data:", request.json)

    # Get the most recent message from the frontend
    data = request.json
    message = data.get('message', '').strip()

    # Log the received message to the terminal
    print(f"Received message: '{message}'")  # Debugging: Print the received message

    if not message:
        print("No message received or message is empty.")
        return jsonify({
            "suggestions": [{"text": "I'm sorry, I couldn't think of any suggestions right now.", "convincePercentage": 0}],
            "overallConvincePercentage": 0
        })

    # Initialize Groq client with the hardcoded API key
    client = Groq(api_key=GROQ_API_KEY)

    # Use Groq API to analyze the most recent message and generate suggestions
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a romantic and flirtatious assistant tasked with helping User 2 win over User 1's heart. "
                        "Analyze the most recent message and suggest exactly 3 responses in the following format: "
                        "'Suggestion 1 (Convince Percentage: X%) - [SUGGESTION TEXT]', 'Suggestion 2 (Convince Percentage: Y%) - [SUGGESTION TEXT]', 'Suggestion 3 (Convince Percentage: Z%) - [SUGGESTION TEXT]'. "
                        "Ensure each response is playful, flirty, or slightly erotic, but still respectful."
                    )
                },
                {
                    "role": "user",
                    "content": f"Most Recent Message:\n{message}"
                }
            ],
            model="llama-3.3-70b-versatile"
        )

        # Parse Groq API response
        response_content = chat_completion.choices[0].message.content.strip()
        print("Raw API Response:", response_content)  # Debugging: Print raw response

        # Extract clean suggestions using regex
        pattern = r"Suggestion \d+ \(Convince Percentage: (\d+)%\) - (.+)"
        matches = re.findall(pattern, response_content)

        # Parse matches into suggestions
        suggestions = []
        for percentage, text in matches:
            suggestions.append({"text": text.strip(), "convincePercentage": int(percentage)})

        # If no valid suggestions were parsed, return a fallback suggestion
        if not suggestions:
            suggestions = [
                {"text": "I'm sorry, I couldn't think of any suggestions right now.", "convincePercentage": 0}
            ]

        # Calculate overall convince percentage
        overall_convince_percentage = (
            sum(s['convincePercentage'] for s in suggestions) / len(suggestions)
            if suggestions else 0
        )

        # Return suggestions and overall convince percentage
        return jsonify({
            "suggestions": suggestions,
            "overallConvincePercentage": round(overall_convince_percentage, 2)
        })

    except Exception as e:
        # Log the error and return a fallback response
        print("Error calling Groq API:", e)
        return jsonify({
            "suggestions": [{"text": "I'm sorry, I couldn't think of any suggestions right now.", "convincePercentage": 0}],
            "overallConvincePercentage": 0
        })

if __name__ == '__main__':
    app.run(debug=True)