import json
import re
import os

INPUT_FILE = "data_pipeline/statutes.jsonl"
NODES_FILE = "data_pipeline/kg_nodes.jsonl"
EDGES_FILE = "data_pipeline/kg_edges.jsonl"

def extract_citations(text):
    # Regex to find "section X", "clause Y", etc.
    # Examples: "section 10", "clause (23C) of section 10"
    citations = []
    
    # Pattern for "section <number>"
    section_pattern = r"section\s+(\d+[A-Z]*)"
    matches = re.findall(section_pattern, text, re.IGNORECASE)
    for m in matches:
        citations.append({"target": m, "type": "CITES"})
        
    return citations

def extract_definitions(text):
    # Regex for definitions: '"term" means ...'
    definitions = []
    pattern = r'"([^"]+)"\s+means'
    matches = re.findall(pattern, text)
    for m in matches:
        definitions.append({"term": m, "type": "DEFINES"})
    return definitions

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found.")
        return

    nodes = []
    edges = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try:
                record = json.loads(line)
                node_id = record['id']
                
                # Create main node
                nodes.append({
                    "id": node_id,
                    "label": "Statute",
                    "url": record['url'],
                    "text": record['segments'][0]['content'] if record['segments'] else ""
                })
                
                # Process segments
                for segment in record['segments']:
                    text = segment['content']
                    
                    # Extract citations
                    citations = extract_citations(text)
                    for cit in citations:
                        edges.append({
                            "source": node_id,
                            "target": cit['target'], # This might need normalization to match node IDs
                            "relation": cit['type']
                        })
                        
                    # Extract definitions
                    defs = extract_definitions(text)
                    for d in defs:
                        # Create a concept node for the defined term
                        term_id = f"Concept:{d['term']}"
                        nodes.append({
                            "id": term_id,
                            "label": "Concept",
                            "name": d['term']
                        })
                        edges.append({
                            "source": node_id,
                            "target": term_id,
                            "relation": "DEFINES"
                        })
                        
            except json.JSONDecodeError:
                continue

    # Deduplicate nodes
    unique_nodes = {n['id']: n for n in nodes}.values()
    
    # Save
    with open(NODES_FILE, 'w', encoding='utf-8') as f:
        for n in unique_nodes:
            f.write(json.dumps(n) + "\n")
            
    with open(EDGES_FILE, 'w', encoding='utf-8') as f:
        for e in edges:
            f.write(json.dumps(e) + "\n")
            
    print(f"Extracted {len(unique_nodes)} nodes and {len(edges)} edges.")

if __name__ == "__main__":
    main()
