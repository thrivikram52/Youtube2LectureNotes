import os
import anthropic
from typing import List, Tuple

def call_claude_api(transcript_segments: List[Tuple[str, str]], prompt: str) -> str:
    script_content = "\n".join([
        f"Timestamp: [{ts}]\n{text}" for ts, text in transcript_segments
    ])
    full_prompt = prompt + "\n\n" + script_content
    CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    message = client.messages.create(
        model="claude-3-opus-latest",
        max_tokens=4096,
        temperature=1,
        system="You are a helpful assistant that processes lecture transcripts into structured notes.",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": full_prompt}
                ]
            }
        ]
    )
    return "\n".join([part.text for part in message.content if getattr(part, 'type', None) == "text"]) 