import ingest
import os
import json
from time import time

# Assuming Groq API is similar to OpenAI's usage
from groq import Groq

index = ingest.load_index()

# Initialize Groq API client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Function to perform the search on supplier contracts based on query
def search(query, filter_dict=None, max_results=10):
    # Assuming df is a pre-existing dataframe containing supplier contracts
    # Filter the DataFrame based on risk level (if provided)
    if filter_dict:
        filtered_df = df[df['risk_level'] == filter_dict.get('risk_level', '')]
    else:
        filtered_df = df
    # Convert the filtered data to a list of dictionaries and limit the number of results
    results = filtered_df.to_dict(orient='records')[:max_results]
    return results

# Prompt templates
prompt_template = """
You're a contract advisor. Answer the QUESTION based on the CONTEXT from our supplier contracts database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
""".strip()

entry_template = """
Supplier_Type: {supplier_type}
Supplier_Name: {supplier_name}
Risk_Level: {risk_level}
Compliance_Issues: {compliance_issues}
Key_Terms: {key_terms}
Negotiate_Recommendation: {negotiate_recommendation}
Quality_Metrics: {quality_metrics}
Past_Performance: {past_performance}
Supply_Chain_Disruption: {supply_chain_disruption}
Cost_Metrics: {cost_metrics}
""".strip()

# Function to build a clear prompt for Groq API
def build_prompt(query, search_results):
    context = ""
    
    for doc in search_results:
        context += entry_template.format(**doc) + "\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

# Function to call the LLM (Groq API)
def llm(prompt, model='Llama3-groq-70b-8192-tool-use-preview'):
    # Assuming client is the Groq API client instance
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model
    )
    
    answer = response.choices[0].message.content

    # Assuming Groq API gives token usage details (adapt if necessary)
    token_stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return answer, token_stats

# Evaluation prompt template
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

# Function to evaluate the relevance of the generated answer
def evaluate_relevance(question, answer):
    prompt = evaluation_prompt_template.format(question=question, answer=answer)
    evaluation, tokens = llm(prompt, model='Llama3-groq-70b-8192-tool-use-preview')

    try:
        json_eval = json.loads(evaluation)
        return json_eval, tokens
    except json.JSONDecodeError:
        result = {"Relevance": "UNKNOWN", "Explanation": "Failed to parse evaluation"}
        return result, tokens

def calculate_openai_cost(model, tokens):
    openai_cost = 0

    if model == "llama3-8b-8192": 
        openai_cost = (
            tokens["prompt_tokens"] * 0.00015 + tokens["completion_tokens"] * 0.0006
        ) / 1000
    else:
        print("Model not recognized. OpenAI cost calculation failed.")

    return openai_cost

def rag(query, model='llama3-8b-8192'):
    t0 = time()

    # Search for high-risk contracts (you can modify filter_dict based on needs)
    search_results = search(query, filter_dict={'risk_level': 'High'})
    
    # Build the prompt using the search results
    prompt = build_prompt(query, search_results)
    
    # Get the LLM response based on the prompt
    answer, token_stats = llm(prompt, model=model)

    # Evaluate the relevance of the generated answer
    relevance, rel_token_stats = evaluate_relevance(query, answer)

    t1 = time()
    took = t1 - t0

    # Calculate cost for RAG and evaluation
    groq_cost_rag = calculate_groq_cost(token_stats)
    groq_cost_eval = calculate_groq_cost(rel_token_stats)

    total_cost = groq_cost_rag + groq_cost_eval

    # Gather all relevant data
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
        "total_cost": total_cost,
    }

    return answer_data