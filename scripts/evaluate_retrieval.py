import os
import sys
from typing import List, Dict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.rag.retriever import retrieve_operational_knowledge

EVALUATION_DATASET = [
    {
        "query": "Payment API is returning a spike in HTTP 500 errors. Customers unable to checkout.",
        "relevant_services": ["payment-service"],
        "relevant_titles_keywords": ["payment", "checkout", "stripe", "500"]
    },
    {
        "query": "P99 latency on JWT authentication jumped from 5ms to 900ms. Token verification spike.",
        "relevant_services": ["auth-service"],
        "relevant_titles_keywords": ["auth", "jwt", "latency", "token"]
    },
    {
        "query": "Inventory reservation locks causing deadlocks on concurrent flash sale checkout.",
        "relevant_services": ["order-service", "inventory-service"],
        "relevant_titles_keywords": ["deadlock", "order", "inventory", "lock"]
    }
]

def calculate_precision_at_k(retrieved_docs: List[Dict], query_data: Dict, k: int) -> float:
    if k == 0: return 0.0
    top_k = retrieved_docs[:k]
    relevant_count = sum(1 for doc in top_k if doc["service"] in query_data["relevant_services"] or any(kw.lower() in doc["title"].lower() for kw in query_data["relevant_titles_keywords"]))
    return relevant_count / k

def calculate_recall_at_k(retrieved_docs: List[Dict], query_data: Dict, k: int) -> float:
    if k == 0: return 0.0
    top_k = retrieved_docs[:k]
    relevant_count = sum(1 for doc in top_k if doc["service"] in query_data["relevant_services"] or any(kw.lower() in doc["title"].lower() for kw in query_data["relevant_titles_keywords"]))
    return min(1.0, relevant_count / 1.0) 

def run_retrieval_evaluation(k: int = 3):
    print(f"\\n--- 🔍 RAG Evaluation: Context Relevance (K={k}) ---")
    results = {"precision": [], "recall": []}
    
    for idx, data in enumerate(EVALUATION_DATASET):
        print(f"\\nEvaluating Case {idx + 1}: '{data['query']}'")
        docs = retrieve_operational_knowledge(data["query"], limit=k)
        
        p_at_k = calculate_precision_at_k(docs, data, k)
        r_at_k = calculate_recall_at_k(docs, data, k)
        
        print(f"  - Precision@{k}: {p_at_k:.2f}")
        print(f"  - Recall@{k}:    {r_at_k:.2f}")
        
        results["precision"].append(p_at_k)
        results["recall"].append(r_at_k)
        
    print("\\n--- Final Retrieval Metrics ---")
    print(f"Mean Precision@{k}: {sum(results['precision'])/len(results['precision']):.2f}")
    print(f"Mean Recall@{k}:    {sum(results['recall'])/len(results['recall']):.2f}")

if __name__ == "__main__":
    run_retrieval_evaluation(k=3)
