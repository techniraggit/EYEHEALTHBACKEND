import google.generativeai as gen_ai
import os
from django.conf import settings

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PROMPT_FILE = f"{settings.BASE_DIR}/ai_doctor/prompts.txt"

# Cache the prompt content to avoid reading the file repeatedly
prompt_content = None


def get_prompt(user_prompt: str):
    try:
        with open(PROMPT_FILE, "r") as file:
            prompt_content = file.read()
    except FileNotFoundError:
            print(f"Prompt file not found: {PROMPT_FILE}")
            raise
    except Exception as e:
        print(f"Error loading prompt file: {e}")
        raise

    return prompt_content.format(user_query=user_prompt)


def make_request(user_query: str):
    try:
        if not GOOGLE_API_KEY:
            raise ValueError("Google API key is missing.")

        gen_ai.configure(api_key=GOOGLE_API_KEY)
        prompt = get_prompt(user_query)

        vision_model = gen_ai.GenerativeModel("gemini-1.5-flash")
        response = vision_model.generate_content([prompt])

        return response.text
    except ValueError as ve:
        print(f"ValueError: {ve}")
        return None
    except Exception as e:
        print(f"Error during API request: {e}")
        return None
