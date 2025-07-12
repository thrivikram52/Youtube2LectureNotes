import os
import openai
from typing import List, Tuple

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def call_openai_api(transcript_segments: List[Tuple[str, str]], prompt: str) -> str:
    script_content = "\n".join([
        f"Timestamp: [{ts}]\n{text}" for ts, text in transcript_segments
    ])
    full_prompt = prompt + "\n\n" + script_content
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",  # or "gpt-4-turbo" or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a helpful assistant that processes lecture transcripts into structured notes."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=1,
    )
    return response.choices[0].message.content 