---
name: pdf-to-markdown
description: |
  Convert a PDF file to well-formatted markdown using image-based OCR via Claude subagents.
  Processes pages in parallel batches with pypdf fallback for content-filtered pages.
  Use when the user wants to convert a PDF (especially academic papers with tables/diagrams) to markdown.
user-invocable: true
---

# PDF to Markdown Conversion

Convert a PDF file into a single well-formatted markdown file using image-based OCR via Claude subagents, with automatic pypdf fallback for pages that hit content filtering.

## Usage

```
/pdf-to-markdown <pdf_path> [output_path] [batch_size]
```

- `pdf_path`: Path to the PDF file (required)
- `output_path`: Path for the output markdown file (optional, defaults to `docs/<pdf_basename>.md`)
- `batch_size`: Number of pages to process in parallel (optional, defaults to 5)

## Procedure

Follow these steps exactly:

### Step 1: Setup and Page Count

1. Ensure `pdftoppm` is available. It may be in the conda environment:
   ```bash
   export PATH="/gscratch/argon/kahuja/miniconda3/envs/slop-analysis/bin:/usr/bin:/bin:$PATH"
   ```
2. Get the total page count:
   ```bash
   pdfinfo <pdf_path> | grep Pages
   ```
3. Create an output directory for page images alongside the PDF:
   ```bash
   mkdir -p <pdf_dir>/pdf_pages
   ```

### Step 2: Convert PDF Pages to PNG

Convert all pages to PNG at 300 DPI:
```bash
pdftoppm -png -r 300 <pdf_path> <pdf_dir>/pdf_pages/page
```

### Step 3: Extract pypdf Text as Fallback

Extract text from all pages using pypdf and save as JSON:
```python
import pypdf, json

reader = pypdf.PdfReader('<pdf_path>')
pages = {}
for i in range(len(reader.pages)):
    pages[str(i+1)] = reader.pages[i].extract_text()

with open('<pdf_dir>/pdf_pages/pypdf_all.json', 'w') as f:
    json.dump(pages, f)
```

### Step 4: Process Pages in Batches

Process pages in batches of `batch_size` (default 5) using the Task tool with subagents. For each page in the batch, launch a background subagent:

```
Task(
    description="Convert PDF page N to md",
    subagent_type="general-purpose",
    run_in_background=True,
    prompt="""Read the image file at `<pdf_dir>/pdf_pages/page-NN.png` and convert its contents to well-formatted markdown. This is a page from a document. Pay careful attention to:
- Headings and section numbers
- Bold and italic text
- Block quotes and examples
- Any tables or diagrams (represent them in markdown)
- Do NOT include page numbers or running chapter title headers — skip these entirely.

Return ONLY the markdown text, nothing else."""
)
```

Wait for all agents in a batch to complete before launching the next batch. Track which pages succeed and which hit content filtering errors.

### Step 5: Merge Results

After all batches complete, write a Python script to merge results:

1. For each page, check if the subagent succeeded or was content-filtered
2. For succeeded pages: extract the markdown from the agent output file
   - Output files are JSONL format at the task output path
   - Each line is a JSON object with a `"message"` field containing `"role"` and `"content"`
   - Extract the last assistant message's text content
3. For content-filtered pages: use the pypdf fallback text, wrapped with an HTML comment:
   ```
   <!-- NOTE: Page N was extracted using pypdf due to API content filtering. This text may need manual formatting corrections. -->
   ```
4. Join all pages with `\n\n---\n\n` separators
5. Write to the output markdown file

### Agent Output File Parsing

The agent output files are JSONL where each line has this structure:
```json
{
  "message": {
    "role": "assistant",
    "content": [
      {"type": "text", "text": "...the markdown content..."}
    ]
  }
}
```

To extract the final markdown from an agent output file:
```python
import json

def extract_agent_markdown(filepath):
    last_text = None
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                msg = entry.get("message", {})
                if msg.get("role") == "assistant":
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                last_text = block["text"]
            except json.JSONDecodeError:
                continue
    return last_text
```

## Important Notes

- Some pages may trigger API content filtering (error 400: "Output blocked by content filtering policy"). This is expected for pages containing sensitive quoted material in academic texts. The pypdf fallback handles these automatically.
- The pypdf fallback text is raw/unformatted — it preserves content but loses formatting like bold, italic, tables, and diagrams. These pages are marked with HTML comments for manual review.
- Always use the `education-env` conda environment for running Python scripts.
- Page images should be stored in the project directory (not `/tmp`) so subagents can access them.
