# Youtube2LectureNotes

This project converts a YouTube lecture video into structured, illustrated lecture notes in PDF format using AI and screenshots.

## Workflow Overview

1. **Download** the YouTube video and its transcript.
2. **Parse** the transcript into timestamped segments.
3. **Chunk** the transcript for LLM context limits.
4. **Generate** structured markdown notes for each chunk using an LLM (Claude or OpenAI), including standard markdown image links for screenshots.
5. **Concatenate** all markdown outputs into a single markdown file.
6. **Extract** all screenshot timestamps from the markdown.
7. **Capture** screenshots from the video at the specified timestamps.
8. **Save** the final markdown file.
9. **Convert** the markdown to PDF using Pandoc (with images included).

## Setup

1. **Install dependencies:**
   - Python 3.8+
   - `yt-dlp`, `opencv-python`, `pandoc`, and your LLM API dependencies (`openai`, `anthropic`, etc.)
   - Install Pandoc: https://pandoc.org/install.html
   - Install yt-dlp: `pip install yt-dlp`
   - Install OpenCV: `pip install opencv-python`

2. **Set up API keys:**
   - For OpenAI: set `OPENAI_API_KEY` in your environment.
   - For Claude: set `ANTHROPIC_API_KEY` or `CLAUDE_API_KEY`.

3. **Edit `prompt.txt`:**
   - The prompt instructs the LLM to use standard markdown image links for screenshots:
     ```
     ![](screenshot_00-12-34.png)
     _Timestamp: 00:12:34_
     ```
   - The prompt encourages the LLM to include screenshots for all significant visuals.

## Usage

```sh
python youtube2lecturenotes.py "<YouTube URL>"
```
- All intermediate files and outputs are saved in the `temp/` directory.
- The final PDF will be at `temp/lecture_notes.pdf`.

## Notes on Image Handling

- **Screenshots** are referenced in the markdown as `![](screenshot_00-12-34.png)`.
- **Pandoc must be run from the `temp/` directory** (the script does this automatically) so that images are found and included in the PDF.
- If you run Pandoc manually, always `cd temp` first, then run:
  ```sh
  pandoc final.md -o lecture_notes.pdf
  ```

## Color Support in Markdown

- **Standard Markdown does not support colored text.**
- For PDF output via Pandoc/LaTeX, you can use LaTeX color commands (e.g., `\textcolor{red}{text}`) and set `--pdf-engine=xelatex` with the xcolor package.
- For HTML output, you can use inline HTML: `<span style="color: red;">text</span>`.
- GitHub and most markdown viewers do **not** support color.

## Example Output

- Structured notes with headings, bullet points, and embedded screenshots at the correct timestamps.
- PDF file suitable for study or review.

## Troubleshooting

- If images do not appear in the PDF, ensure all `screenshot_*.png` files are present in the `temp/` directory and that Pandoc is run from that directory.
- If important screenshots are missing, review and strengthen the cues in `prompt.txt`.

---

Feel free to open issues or PRs for improvements! 