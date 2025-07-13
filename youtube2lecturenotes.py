import os
import re
import shutil
import subprocess
import cv2
from llm_openai import call_openai_api
from llm_claude import call_claude_api
from llm_gemini import call_gemini_api

LLM = "gemini"  # or "openai" or "gemini" or "claude"

def download_youtube_transcript_and_video(youtube_url: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    transcript_path = os.path.join(out_dir, "transcript.vtt")
    video_path = os.path.join(out_dir, "video.mp4")
    subprocess.run([
        "yt-dlp", "--write-auto-sub", "--sub-lang", "en", "--skip-download",
        "--output", os.path.join(out_dir, "video"), youtube_url
    ], check=True)
    for f in os.listdir(out_dir):
        if f.endswith(".en.vtt"):
            os.rename(os.path.join(out_dir, f), transcript_path)
            break
    subprocess.run([
        "yt-dlp", "-f", "mp4", "-o", video_path, youtube_url
    ], check=True)
    return transcript_path, video_path

def parse_vtt_transcript(vtt_path: str):
    segments = []
    with open(vtt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    timestamp = None
    text_lines = []
    for line in lines:
        line = line.strip()
        if re.match(r"\d{2}:\d{2}:\d{2}\.\d{3} --> ", line):
            if timestamp and text_lines:
                segments.append((timestamp, " ".join(text_lines).strip()))
                text_lines = []
            timestamp = line.split(" --> ")[0][:8]
        elif line and not line.startswith("WEBVTT") and not re.match(r"^\d+$", line):
            text_lines.append(line)
    if timestamp and text_lines:
        segments.append((timestamp, " ".join(text_lines).strip()))
    return segments

def chunk_transcript_segments(transcript_segments, max_chars=12000):
    chunks = []
    current_chunk = []
    current_len = 0
    for ts, text in transcript_segments:
        entry = f"Timestamp: [{ts}]\n{text}"
        if current_len + len(entry) > max_chars and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_len = 0
        current_chunk.append((ts, text))
        current_len += len(entry)
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def extract_screenshot_timestamps_from_markdown(markdown: str):
    matches = re.findall(r'!\[\]\(screenshot_(\d{2})-(\d{2})-(\d{2})\.png\)', markdown)
    return [f"{h}:{m}:{s}" for h, m, s in matches]

def capture_screenshots(video_path, timestamps, out_dir):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video file: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    for ts in timestamps:
        t_sec = sum(int(x) * 60 ** i for i, x in enumerate(reversed(ts.split(':'))))
        frame_number = int(fps * t_sec)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        if ret:
            img_name = f"screenshot_{ts.replace(':', '-')}" + ".png"
            img_path = os.path.join(out_dir, img_name)
            cv2.imwrite(img_path, frame)
        else:
            print(f"Warning: Could not capture frame at {ts}")
    cap.release()

def save_final_markdown(llm_outputs, out_path, video_url=None):
    with open(out_path, "w", encoding="utf-8") as f:
        if video_url:
            f.write(f"[Watch the original video]({video_url})\n\n")
        f.write("\n".join(llm_outputs))

def get_llm_outputs(transcript_chunks, prompt, llm_type, work_dir):
    llm_outputs = []
    if llm_type == "openai":
        for i, chunk in enumerate(transcript_chunks):
            print(f"Calling OpenAI API for chunk {i+1}/{len(transcript_chunks)}...")
            llm_output = call_openai_api(chunk, prompt)
            chunk_file = os.path.join(work_dir, f"llm_response_chunk{i+1}.txt")
            with open(chunk_file, "w", encoding="utf-8") as f:
                f.write(llm_output)
            llm_outputs.append(llm_output)
    elif llm_type == "claude":
        for i, chunk in enumerate(transcript_chunks):
            print(f"Calling Claude API for chunk {i+1}/{len(transcript_chunks)}...")
            llm_output = call_claude_api(chunk, prompt)
            chunk_file = os.path.join(work_dir, f"llm_response_chunk{i+1}.txt")
            with open(chunk_file, "w", encoding="utf-8") as f:
                f.write(llm_output)
            llm_outputs.append(llm_output)
    elif llm_type == "gemini":
        for i, chunk in enumerate(transcript_chunks):
            print(f"Calling Gemini API for chunk {i+1}/{len(transcript_chunks)}...")
            llm_output = call_gemini_api(chunk, prompt)
            chunk_file = os.path.join(work_dir, f"llm_response_chunk{i+1}.txt")
            with open(chunk_file, "w", encoding="utf-8") as f:
                f.write(llm_output)
            llm_outputs.append(llm_output)
    else:
        raise ValueError("LLM must be 'openai', 'claude', or 'gemini'")
    return llm_outputs

def main(youtube_url: str):
    work_dir = os.path.join(os.getcwd(), "temp")
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    os.makedirs(work_dir, exist_ok=True)
    prompt_filename="prompt.txt"
    prompt_path = os.path.join(os.path.dirname(__file__), prompt_filename)
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read()
    print(f"Working directory: {work_dir}")
    print("Downloading transcript and video...")
    transcript_path, video_path = download_youtube_transcript_and_video(youtube_url, work_dir)
    print("Parsing transcript...")
    transcript_segments = parse_vtt_transcript(transcript_path)
    print("Chunking transcript...")
    transcript_chunks = chunk_transcript_segments(transcript_segments, max_chars=12000)
    llm_outputs = get_llm_outputs(transcript_chunks, prompt, LLM, work_dir)
    full_markdown = "\n".join(llm_outputs)
    timestamps = extract_screenshot_timestamps_from_markdown(full_markdown)
    print(f"Found {len(timestamps)} screenshots to capture.")
    capture_screenshots(video_path, timestamps, work_dir)
    final_md_path = os.path.join(work_dir, "final.md")
    save_final_markdown(llm_outputs, final_md_path, youtube_url)
    pdf_path = os.path.join(work_dir, "lecture_notes.pdf")
    print("Converting markdown to PDF with Pandoc...")
    try:
        subprocess.run(["pandoc", "final.md", "-o", "lecture_notes.pdf", "--pdf-engine=xelatex"], check=True, cwd=work_dir)
        print(f"Done! PDF saved at: {pdf_path}")
    except Exception as e:
        print(f"Pandoc conversion failed: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube to Lecture Notes Creator")
    parser.add_argument("youtube_url", help="YouTube video URL")
    args = parser.parse_args()
    main(args.youtube_url) 