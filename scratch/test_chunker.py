import sys
import os

# Add root folder to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')


from ingestion.indexing import parse_markdown_sections

txt_file = "data/processed/hdfc_defence.txt"
scheme_name = "HDFC Defence Fund Direct Growth"

if not os.path.exists(txt_file):
    print("Processed text file not found!")
    sys.exit(1)

chunks = parse_markdown_sections(txt_file, scheme_name)
print(f"Total chunks generated: {len(chunks)}")
print("=" * 60)

for idx, chunk in enumerate(chunks[:10]):
    print(f"--- Chunk {idx+1} (Section Type: {chunk['section_type']}) ---")
    print(f"Path: {chunk['section_path']}")
    text_snippet = chunk['text']
    if len(text_snippet) > 200:
        print(text_snippet[:200] + "\n... [TRUNCATED] ...")
    else:
        print(text_snippet)
    print(f"Length (chars): {len(chunk['text'])}")
    print("=" * 60)
