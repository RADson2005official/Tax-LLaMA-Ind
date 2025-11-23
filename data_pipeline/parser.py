import json
import re
import os

INPUT_FILE = "data_pipeline/raw_act.jsonl"
OUTPUT_FILE = "data_pipeline/statutes.jsonl"

def clean_text(text):
    # Remove Indian Kanoon specific noise
    noise_patterns = [
        r"Share Link.*",
        r"Mobile View.*",
        r"Free features.*",
        r"Premium features.*",
        r"Case removal.*",
        r"Warning on translation.*",
        r"Get this document in PDF.*",
        r"Print it on a file/printer.*",
        r"\[Cites.*\]",
        r"\[Cited by.*\]",
        r"\[Entire Act\]",
        r"Take notes as you read.*",
        r"Union of India - .*",
        r"Section \d+.* in The Income Tax Act, 1961", # Redundant header
    ]
    
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        is_noise = False
        for pattern in noise_patterns:
            if re.search(pattern, line):
                is_noise = True
                break
        if not is_noise and line.strip():
            cleaned_lines.append(line.strip())
            
    return "\n".join(cleaned_lines)

def parse_structure(record):
    text = clean_text(record['text'])
    title = record['title']
    
    # Basic hierarchy detection
    # We can detect Provisos and Explanations
    
    segments = []
    
    # Regex for Provisos and Explanations
    # "Provided that...", "Explanation 1.-..."
    
    # We will split the text into chunks based on these keywords
    # This is a simplified parser. A full one would be a state machine.
    
    current_segment = {"type": "main", "content": "", "children": []}
    
    lines = text.split('\n')
    for line in lines:
        if line.startswith("Provided that") or line.startswith("Provided further that"):
            # Save current segment if not empty
            if current_segment["content"]:
                segments.append(current_segment)
            current_segment = {"type": "proviso", "content": line, "children": []}
        elif line.startswith("Explanation"):
             if current_segment["content"]:
                segments.append(current_segment)
             current_segment = {"type": "explanation", "content": line, "children": []}
        else:
            current_segment["content"] += " " + line
            
    if current_segment["content"]:
        segments.append(current_segment)
        
    return {
        "id": title,
        "url": record['url'],
        "segments": segments
    }

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found.")
        return

    processed_count = 0
    with open(INPUT_FILE, 'r', encoding='utf-8') as fin, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        
        for line in fin:
            if not line.strip(): continue
            try:
                record = json.loads(line)
                structured_data = parse_structure(record)
                fout.write(json.dumps(structured_data) + "\n")
                processed_count += 1
            except json.JSONDecodeError:
                continue
                
    print(f"Processed {processed_count} records. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
