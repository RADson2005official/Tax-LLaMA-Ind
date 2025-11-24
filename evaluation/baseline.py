import json
import random
import time

# Placeholder for actual model inference
# In a real scenario, we would import torch and transformers here
# from transformers import AutoModelForCausalLM, AutoTokenizer

def mock_inference(question):
    """
    Simulates LLaMA 3.2 8B output for the purpose of the research protocol.
    """
    # Simulate some latency
    time.sleep(0.1)
    
    # Hallucination simulation (randomly cite wrong sections)
    if random.random() < 0.2:
        return f"According to Section {random.randint(100, 200)}, the tax is calculated..."
    
    return "The Income Tax Act defines this in Section 10..."

def evaluate_silver_set():
    print("Running Zero-Shot Baseline on Silver Set...")
    results = []
    with open("evaluation/silver_set.jsonl", "r") as f:
        questions = [json.loads(line) for line in f]
        
    for q in questions:
        prediction = mock_inference(q['question'])
        results.append({
            "question": q['question'],
            "gold": q['gold_answer'],
            "prediction": prediction,
            "match": "Section" in prediction # Simplified metric
        })
        
    # Save results
    with open("evaluation/baseline_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Baseline evaluation complete. Processed {len(results)} questions.")

if __name__ == "__main__":
    evaluate_silver_set()
