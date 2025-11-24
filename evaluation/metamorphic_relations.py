import json
import random

# Metamorphic Relations (MRs)

def mr_monotonicity(income_tax_calculator_fn, base_income):
    """
    MR1: Monotonicity
    If Income A > Income B, and all else equal, Tax A >= Tax B.
    """
    income_a = base_income
    income_b = base_income + 50000 # Increase income
    
    tax_a = income_tax_calculator_fn(income_a)
    tax_b = income_tax_calculator_fn(income_b)
    
    # Note: This is a simplified check. In reality, we'd parse the model output.
    # For this protocol, we assume the model outputs a number or we extract it.
    
    return {
        "relation": "Monotonicity",
        "input_a": income_a,
        "input_b": income_b,
        "output_a": tax_a,
        "output_b": tax_b,
        "passed": tax_b >= tax_a # Tax should increase or stay same
    }

def mr_inclusion(retrieval_fn, query):
    """
    MR2: Inclusion
    Retrieving for "Query" should be a subset of retrieving for "Query + Noise" 
    (or at least the core relevant sections should still be found).
    """
    results_a = retrieval_fn(query)
    results_b = retrieval_fn(query + " ignoring irrelevant details about the weather.")
    
    # Check if top result of A is in top 5 of B
    top_a = results_a[0] if results_a else None
    passed = top_a in results_b[:5] if top_a else True
    
    return {
        "relation": "Inclusion",
        "query_a": query,
        "query_b": query + "...",
        "passed": passed
    }

def generate_test_suite():
    """
    Generates synthetic test cases for MRs.
    """
    suite = []
    
    # Monotonicity Cases
    incomes = [500000, 800000, 1200000, 2000000, 5000000]
    for inc in incomes:
        suite.append({
            "type": "monotonicity",
            "base_income": inc
        })
        
    # Inclusion Cases
    queries = [
        "deduction under section 80C",
        "tax rate for domestic company",
        "definition of agricultural income",
        "penalty for late filing"
    ]
    for q in queries:
        suite.append({
            "type": "inclusion",
            "query": q
        })
        
    return suite

if __name__ == "__main__":
    suite = generate_test_suite()
    with open("evaluation/metamorphic_suite.jsonl", "w") as f:
        for case in suite:
            f.write(json.dumps(case) + "\n")
    print(f"Generated {len(suite)} metamorphic test cases.")
