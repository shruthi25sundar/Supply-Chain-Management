import ingest
import os
import json
from time import time
from groq import Groq

index = ingest.load_index()

# Initialize Groq API client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def search(query):
    results = index.search(
        query=query, filter_dict={}, num_results=10
    )
    return results

# prompt_template = """
# You're a contract advisor. Answer the QUESTION based on the CONTEXT from our supplier contracts database.
# Use only the facts from the CONTEXT when answering the QUESTION.

# QUESTION: {question}

# CONTEXT:
# {context}
# """.strip()

# entry_template = """
# Supplier_Type: {supplier_type}
# Supplier_Name: {supplier_name}
# Risk_Level: {risk_level}
# Compliance_Issues: {compliance_issues}
# Key_Terms: {key_terms}
# Negotiate_Recommendation: {negotiate_recommendation}
# Quality_Metrics: {quality_metrics}
# Past_Performance: {past_performance}
# Supply_Chain_Disruption: {supply_chain_disruption}
# Cost_Metrics: {cost_metrics}
# """.strip()

def build_prompt(query, search_results):
    context = ""
    
    for doc in search_results:
        context += (
            f"- **Supplier_Type**: {doc['supplier_type']}\n"
            f"  **Supplier_Name**: {doc['supplier_name']}\n"
            f"  **Risk_Level**: {doc['risk_level']}\n"
            f"  **Compliance_Issues**: {doc['compliance_issues']}\n"
            f"  **Key_Terms**: {doc['key_terms']}\n"
            f"  **Negotiate_Recommendation**: {doc['negotiate_recommendation']}\n"
            f"  **Quality_Metrics**: {doc['quality_metrics']}\n"
            f"  **Past_Performance**: {doc['past_performance']}\n"
            f"  **Supply_Chain_Disruption**: {doc['supply_chain_disruption']}\n"
            f"  **Cost_Metrics**: {doc['cost_metrics']}\n\n"
        )
    
    prompt = (
        f"QUESTION: {query}\n\n"
        f"CONTEXT:\n{context}"
    )
    
    return prompt

def llm(prompt, model='Llama3-groq-70b-8192-tool-use-preview'):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model
    )
    answer = response.choices[0].message.content
    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }
    return answer, token_stats

evaluation_prompt_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()

def evaluate_relevance(question, answer):
    prompt = evaluation_prompt_template.format(question=question, answer=answer)
    evaluation, tokens = llm(prompt, model='Llama3-groq-70b-8192-tool-use-preview')
    try:
        json_eval = json.loads(evaluation)
        return json_eval, tokens
    except json.JSONDecodeError:
        result = {"Relevance": "UNKNOWN", "Explanation": "Failed to parse evaluation"}
        return result, tokens

def calculate_groq_cost(model, tokens):
    groq_cost = 0
    if model == "Llama3-groq-70b-8192-tool-use-preview": 
        groq_cost = (
            tokens["prompt_tokens"] * 0.00015 + tokens["completion_tokens"] * 0.0006
        ) / 1000
    else:
        print("Model not recognized. Groq cost calculation failed.")
    return groq_cost

def rag(query, model='Llama3-groq-70b-8192-tool-use-preview'):
    t0 = time()
    search_results = search(query)
    prompt = build_prompt(query, search_results)
    answer, token_stats = llm(prompt, model=model)
    relevance, rel_token_stats = evaluate_relevance(query, answer)
    t1 = time()
    took = t1 - t0

    groq_cost_rag = calculate_groq_cost(model, token_stats)
    groq_cost_eval = calculate_groq_cost(model, rel_token_stats)
    groqai_cost = groq_cost_rag + groq_cost_eval

    answer_data = {
        "answer": answer,
        "model_used": model,
        "response_time": took,
        "relevance": relevance.get("Relevance", "UNKNOWN"),
        "relevance_explanation": relevance.get("Explanation", "Failed to parse evaluation"),
        "prompt_tokens": token_stats["prompt_tokens"],
        "completion_tokens": token_stats["completion_tokens"],
        "total_tokens": token_stats["total_tokens"],
        "eval_prompt_tokens": rel_token_stats["prompt_tokens"],
        "eval_completion_tokens": rel_token_stats["completion_tokens"],
        "eval_total_tokens": rel_token_stats["total_tokens"],
        "groqai_cost": groqai_cost,
    }
    return answer_data
