import os
import sys
import time
import re
from typing import List, Dict

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.rag.retriever import retrieve_operational_knowledge, get_genai
# Use a high-throughput model for bulk evaluation to avoid strict rate limits
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# Define our evaluation dataset
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

# --- HELPER: ROBUST GENERATION WITH RETRIES ---
def safe_generate_content(prompt: str, is_integer: bool = False, max_retries: int = 3):
    """Wraps Gemini API calls with automatic retries for rate limits (429 errors)."""
    client = get_genai()
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=GEMINI_MODEL_NAME, contents=prompt)
            text = response.text.strip()
            
            if is_integer:
                match = re.search(r'\d', text)
                if match:
                    return int(match.group())
                return 1
            return text
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1)
                    print(f"    (Rate limit hit. Waiting {wait_time}s before retry...)")
                    time.sleep(wait_time)
                    continue
            
            if is_integer:
                print(f"    (LLM Error: {e})")
                return 0
            return f"Error generating answer: {error_str}"

# --- 1. RETRIEVAL EVALUATION (Context Relevance) ---

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

# --- 2. GENERATION (Drafting the Answer) ---

def generate_rag_answer(query: str, retrieved_docs: List[Dict]) -> str:
    context_text = "\\n\\n".join([
        f"Document: {doc['title']}\\nSource: {doc['source']}\\nContent: {doc['content']}" 
        for doc in retrieved_docs
    ])
    
    prompt = f"""
    You are an AI Incident Responder. Answer the user's query using ONLY the provided operational context.
    If the context does not contain the answer, say "I don't have enough information in the runbooks to answer this."
    
    Query: {query}
    
    Context:
    {context_text}
    """
    return safe_generate_content(prompt, is_integer=False)

# --- 3. LLM-AS-A-JUDGE EVALUATION (Faithfulness & Relevance) ---

def evaluate_faithfulness(answer: str, retrieved_docs: List[Dict]) -> int:
    context_text = "\\n\\n".join([doc['content'] for doc in retrieved_docs])
    
    prompt = f"""
    You are an expert evaluator. Your task is to evaluate the 'Faithfulness' of an AI-generated answer.
    Faithfulness measures whether the answer is strictly derived from the provided context without hallucinating external information.
    
    Score from 1 to 5, where:
    1 = Completely hallucinates or contradicts the context.
    5 = Strictly and perfectly grounded in the provided context.
    
    Context: {context_text}
    Answer: {answer}
    
    Output ONLY the integer score (1, 2, 3, 4, or 5).
    """
    return safe_generate_content(prompt, is_integer=True)

def evaluate_answer_relevance(query: str, answer: str) -> int:
    prompt = f"""
    You are an expert evaluator. Your task is to evaluate the 'Answer Relevance' of an AI-generated answer.
    Answer Relevance measures how directly and effectively the answer addresses the user's original query.
    
    Score from 1 to 5, where:
    1 = Completely irrelevant or fails to address the query.
    5 = Perfectly addresses the query, providing a direct and helpful response.
    
    Query: {query}
    Answer: {answer}
    
    Output ONLY the integer score (1, 2, 3, 4, or 5).
    """
    return safe_generate_content(prompt, is_integer=True)

# --- MAIN EVALUATION RUNNER ---

def run_full_rag_evaluation(k: int = 3):
    print(f"\\n--- Starting Full RAG Evaluation Suite (K={k}) ---")
    
    results = {
        "precision": [], "recall": [], "faithfulness": [], "relevance": []
    }
    
    for idx, data in enumerate(EVALUATION_DATASET):
        print(f"\\nEvaluating Case {idx + 1}: '{data['query']}'")
        
        # 1. Retrieval
        docs = retrieve_operational_knowledge(data["query"], limit=k)
        p_at_k = calculate_precision_at_k(docs, data, k)
        r_at_k = calculate_recall_at_k(docs, data, k)
        print(f"  - [Retrieval] Precision@{k}: {p_at_k:.2f}")
        print(f"  - [Retrieval] Recall@{k}:    {r_at_k:.2f}")
        
        # 2. Generation
        print(f"  - [Generation] Synthesizing answer...")
        answer = generate_rag_answer(data["query"], docs)
        
        # 3. LLM-as-a-Judge Evaluation
        faithfulness = evaluate_faithfulness(answer, docs)
        relevance = evaluate_answer_relevance(data["query"], answer)
        
        print(f"  - [Evaluation] Faithfulness Score: {faithfulness}/5")
        print(f"  - [Evaluation] Relevance Score:    {relevance}/5")
        
        results["precision"].append(p_at_k)
        results["recall"].append(r_at_k)
        results["faithfulness"].append(faithfulness)
        results["relevance"].append(relevance)
        
        time.sleep(5) # Small buffer between test cases
        
    # Summarize
    print("\\n--- Final RAG Evaluation Metrics ---")
    print(f"Retrieval - Mean Precision@{k}: {sum(results['precision'])/len(results['precision']):.2f}")
    print(f"Retrieval - Mean Recall@{k}:    {sum(results['recall'])/len(results['recall']):.2f}")
    print(f"Generation - Mean Faithfulness: {sum(results['faithfulness'])/len(results['faithfulness']):.2f} / 5.0")
    print(f"Generation - Mean Relevance:    {sum(results['relevance'])/len(results['relevance']):.2f} / 5.0")

if __name__ == "__main__":
    run_full_rag_evaluation(k=3)
