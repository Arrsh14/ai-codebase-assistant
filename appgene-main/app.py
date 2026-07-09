import os
from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Load your OpenAI API key and development mode
openai.api_key = os.getenv("OPENAI_API_KEY")
USE_DUMMY = os.getenv("USE_DUMMY", "false").lower() == "true"

@app.route('/motivation', methods=['GET'])
def get_motivation():
    prompt = "Give me a short, original motivational quote."

    # ✅ Use dummy quote if development mode is enabled
    if USE_DUMMY:
        return jsonify({"quote": "🌟 Stay positive. Even the darkest night will end and the sun will rise."})

    try:
        # ✅ Live OpenAI call
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a motivational quote generator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )
        quote = response.choices[0].message.content.strip()
        return jsonify({"quote": quote})

    except openai.RateLimitError:
        return jsonify({"error": "❌ Rate limit exceeded or quota exhausted. Please check your OpenAI usage and billing."}), 429

    except openai.OpenAIError as e:
        return jsonify({"error": f"❌ OpenAI error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"❌ Unexpected error: {str(e)}"}), 500


@app.route('/health')
def health_check():
    return f"✅ Flask is running! API Key set: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}"

if __name__ == "__main__":
    app.run(debug=True, port=8080)