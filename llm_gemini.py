import os
try:
    import google.generativeai as genai
except ImportError:
    raise ImportError("Please install the google-generativeai package: pip install google-generativeai")

def call_gemini_api(transcript_chunk, prompt):
    """
    Calls the Gemini API with the given transcript chunk and prompt.
    Returns the generated text response.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-pro")
    # Compose the full prompt
    full_prompt = prompt.replace("{transcript_chunk}", str(transcript_chunk))
    response = model.generate_content(full_prompt)
    # The response object has a .text attribute for the generated text
    return response.text 