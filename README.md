# Supplier Performance Analysis Assistant

## Overview
This project focuses on using Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs) to enhance supplier performance evaluation. The application retrieves and processes large volumes of supplier data, helping organizations gain quick insights into supplier performance, compliance, cost metrics, and risk management.

![Supplier_management_image_Feb_17__1_](https://github.com/user-attachments/assets/fa6a82f9-1690-4f58-89ea-acfb27e23c82)


## Objective
The aim is to build an end-to-end RAG project to streamline supplier performance analysis by:

1. Ingesting supplier contract data.
2. Implementing a RAG system using a knowledge base and LLM.
3. Evaluating the retrieval and RAG flow for relevance.
4. Creating an interface for interacting with the application.
5. Collecting user feedback and monitoring the system's performance.

## Problem Statement
Supplier performance management often requires analyzing large amounts of data. Traditional methods of performance evaluation are often inefficient, leading to delays in decision-making and a lack of actionable insights. This project tackles the following challenges:

1. **Data Overload**: Supplier data comes in vast amounts, making it hard to analyze.
2. **Complex Queries**: Specific supplier queries (e.g., cost, compliance, risk) are difficult to handle with traditional tools.
3. **Quick Decision-Making**: There is a need for fast, reliable, and actionable insights.
4. **Risk Identification**: Monitoring and mitigating risks related to suppliers' compliance, performance, and supply chain issues.

## Solution
This project implements a system that uses RAG and LLMs to efficiently retrieve and analyze supplier data. The solution offers:

1. **Data Processing**: Automated data ingestion and indexing using in-memory search.
2. **Enhanced Query Resolution**: LLMs generate specific answers from supplier data.
3. **Improved Decision-Making**: Faster insights support timely and accurate decisions.
4. **Risk Mitigation**: Automatically identify compliance risks and quality issues.
5. **Strategic Insights**: Help businesses improve negotiation strategies with suppliers.

## Dataset Overview

**Supplier Contracts**:

Includes detailed information about supplier contracts, such as:
1. Contract ID, Date Signed, Contract Type, Supplier Name, Risk Level
2. Compliance Issues, Key Terms, Past Performance Score, Negotiation Recommendations
3. Quality Issues, Supply Chain Disruptions, Increased Costs, Compliance and Legal Risks
4. Missed Opportunities, Damaged Relationships, Quality Metrics, Delivery Metrics, Cost Metrics, Relationship Metrics

## Project Structure
### Ingestion Pipeline

- Automated ingestion using a Python script to rename columns, convert text fields to strings, and index the documents using `minsearch`.

### RAG Flow

- **Knowledge Base**: Used `minsearch` for indexing and searching the supplier data.
- **LLM**: Used Groq API to generate answers based on the search results.

### Retrieval Evaluation

**Approach 1: Minsearch with Boosting**
- Used boosting techniques to enhance search accuracy.
- **Metrics**:
  - Hit Rate: 93.7%
  - Mean Reciprocal Rank (MRR): 93.4%

**Approach 2: TF-IDF Vectorizer**
- Applied TF-IDF vectorizer with bi-grams for retrieval.
- **Metrics**:
  - Hit Rate: 97.2%
  - MRR: 95.5%
  
**Result**: TF-IDF showed better performance in terms of Hit Rate and MRR.

### RAG Evaluation

1. **Prompt Template**: Created a template to evaluate the relevance of generated answers.
2. **Sample Size**: Evaluated on a sample size of 1,250 records.
3. **Models Compared**:
   - **Llama3-groq-70b-8192-tool-use-preview**:This model is designed to handle complex and extensive prompts, making it suitable for tasks requiring a large context window. It excels in providing detailed and contextually relevant responses, making it a strong candidate for tasks that involve extensive background information and intricate query handling.
   - **llama3-8b-8192**:  This smaller model is optimized for efficiency and speed while still maintaining a reasonably large context window. It is suitable for applications where computational resources are limited or where response time is critical. Despite its smaller size, it can handle moderately complex queries and provide relevant answers.

**Relevance Scores**:
- **Llama3-groq-70b-8192-tool-use-preview**:
  - RELEVANT: 52.72%
  - NON_RELEVANT: 39.60%
  - PARTLY_RELEVANT: 7.68%
- **llama3-8b-8192**:
  - PARTLY_RELEVANT: 57.92%
  - RELEVANT: 29.36%
  - NON_RELEVANT: 12.72%

Llama3-groq-70b-8192-tool-use-preview is better performing model. 

## Code Overview

Supply-Chain-Management/supply_chain_management/

1. **ingest.py**
   - **Purpose**: Loads and processes the supplier contracts dataset. It creates an index for the text-based fields, making them searchable.
   - **Functions**:
     - `load_index(data_path)`: Loads the dataset, processes it, and creates an index using `minsearch`.

2. **db.py**
   - **Purpose**: Handles database operations, including initializing the database, saving conversations, saving feedback, and retrieving recent conversations.
   - **Functions**:
     - `get_db_connection()`: Establishes a connection to the PostgreSQL database.
     - `init_db()`: Initializes the database by creating the necessary tables.
     - `save_conversation(conversation_id, question, answer_data, timestamp)`: Saves a conversation to the database.
     - `save_feedback(conversation_id, feedback, timestamp)`: Saves feedback for a conversation to the database.
     - `get_recent_conversations(limit, relevance)`: Retrieves recent conversations from the database.
     - `get_feedback_stats()`: Retrieves feedback statistics from the database.
     - `check_timezone()`: Checks and prints the timezone settings for the database and Python.

3. **db_prep.py**
   - **Purpose**: Initializes the database by calling the `init_db` function from `db.py`.
   - **Execution**: Run this script to set up the database before starting the application.

4. **rag.py**
   - **Purpose**: Implements the Retrieval-Augmented Generation (RAG) system, including querying the index, building prompts, calling the Groq API, and evaluating relevance.
   - **Functions**:
     - `search(query)`: Searches the supplier contracts based on the query.
     - `build_prompt(query, search_results)`: Builds a prompt for the Groq API based on the search results.
     - `llm(prompt, model)`: Calls the Groq API with the given prompt and model.
     - `evaluate_relevance(question, answer)`: Evaluates the relevance of the generated answer.
     - `calculate_openai_cost(model, tokens)`: Calculates the cost of using the Groq API.
     - `rag(query, model)`: Orchestrates the RAG process, including search, LLM call, and relevance evaluation.

5. **app.py**
   - **Purpose**: Implements the Flask web application that handles incoming questions and feedback using flask
   - **Routes**:
     - `POST /question`: Handles a question by calling the `rag` function and saving the conversation to the database.
     - `POST /feedback`: Handles feedback for a conversation and saves it to the database.

## Implementation Steps to run the application

#### 1. Dependency Management

First, install `pipenv` for dependency management:

```bash
pip install pipenv
```

Then, install the application dependencies:

```bash
pipenv install --dev
```

#### 2. Database Configuration

Before starting the application for the first time, initialize the database.

1. Start the PostgreSQL database using Docker Compose:

   ```bash
   docker-compose up postgres
   ```

2. Run the `db_prep.py` script to set up the database:

   ```bash
   pipenv shell

   cd supply_chain_management

   export POSTGRES_HOST=localhost
   python db_prep.py
   ```

3. Optionally, check the content of the database using `pgcli`:

   ```bash
   pipenv run pgcli -h localhost -U your_username -d fact_supplier -W
   ```

   You can view the schema using the `\d` command:

   ```sql
   \d conversations;
   ```

   And select from the table:

   ```sql
   select * from conversations;
   ```

#### 3. Running the Application

You can run the application using Docker Compose or locally.

**Running with Docker-Compose**

The easiest way to run the application is with Docker Compose:

```bash
docker-compose up
```

**Running Locally**

To run the application locally, start only PostgreSQL and Grafana using Docker Compose:

```bash
docker-compose up postgres grafana
```


Then run the app on your host machine:

```bash
pipenv shell

cd supply_chain_management

export POSTGRES_HOST=localhost
python app.py
```

## Using the Application

**CLI**

Start the interactive CLI application:

```bash
pipenv run python cli.py
```

![image](https://github.com/user-attachments/assets/292361a2-e783-4f3a-b632-85af91bdb0ae)



]![image](https://github.com/user-attachments/assets/299b86ae-2719-4cca-a589-8cd99aacce52)



![image](https://github.com/user-attachments/assets/c67f4fe2-1191-4ce1-b69e-a326070c4649)


## Monitoring

### Grafana

Building a monitoring dashboard in Grafana provides:

1. **Real-Time Monitoring**: Track system performance and detect issues early.
2. **Performance Tracking**: Monitor response times and resource usage.
3. **Historical Analysis**: Analyze trends and review past incidents.
4. **User Feedback Integration**: Assess user satisfaction and quality of responses.
5. **Alerting and Notifications**: Set up alerts for timely issue management.
6. **Improved Decision-Making**: Make data-driven decisions on scaling and optimization.
7. **Enhanced Collaboration**: Share insights and facilitate team discussions.
8. **Customization and Flexibility**: Create tailored dashboards and integrate multiple data sources.

Grafana helps maintain system health, optimize performance, and ensure timely responses to issues.

It's accessible at [localhost:3000](http://localhost:3000):

- Login: "admin"
- Password: "admin"

### Dashboards

![dashboard](https://github.com/user-attachments/assets/809aa2dd-33cb-4f78-9007-6f835df9fde7)


### Insights on Monitoring Dashboard

### Response Time
- **Response Time Graph**: The response time for the queries has been consistently low, mostly under 2 seconds, with one notable spike reaching slightly above 8 seconds around 17:00. This indicates the system generally responds quickly, but occasional delays may occur.

### Relevance Distribution
- **Relevance Metrics**:
  - **Relevant**: 16 responses are marked as relevant.
  - **Partly Relevant**: 1 response is marked as partly relevant.
  - **Non-Relevant**: 2 responses are marked as non-relevant.

  The majority of the responses are relevant, suggesting the system is performing well in terms of providing useful information.

### Conversations Panel
- **Question and Answer Pairs**:
  - "high risk level" -> "Supplier 2482, Supplier 2481, Supplier 2480, Supplier"
  - "how is past performance of supplier 2482" -> "The past performance of Supplier 2482 is poor."
  - "what is the cost metric of supplier 2483" -> "The cost metric for Supplier 2483 is $56.32/unit."
  - "Give supplier types, quality metrics, supply chain dis" -> "Supplier Types: Retailer, Manufacturer, Service Provider"
  - "Which suppliers have the most non-compliance issues" -> "Supplier 637, Supplier 1488, Supplier 1450, Supplier"
  - "Opportunity and Innovation Queries" -> "I'm sorry but I do not have the capability to perform th"

  These questions and answers demonstrate the system's ability to handle diverse queries related to supplier performance, cost metrics, compliance issues, and general supplier information.

### Feedback Statistics
- **Thumbs Up**: 14
- **Thumbs Down**: 3

  The feedback statistics indicate that users have generally been satisfied with the responses, with a significant majority of positive feedback.

### Summary
- The system responds quickly to queries with occasional spikes in response time.
- Most responses are marked as relevant, indicating high accuracy in information retrieval.
- The system covers a range of supplier-related questions effectively.
- User feedback is largely positive, which suggests good performance in meeting user expectations.

These insights suggest that the monitoring system is functioning effectively, providing timely and relevant information to users, with room for occasional improvements to address response time spikes and ensure even higher relevance in responses.

## Technologies
1. Python 3.12
2. Minsearch for in memory full-text search
3. GroqAI as an LLM
4. Docker and Docker Compose for containerization
5. Flask as the API interface - to be used by any other UX
6. Grafana for monitoring and PostgreSQL as the backend for it

## Conclusion:

The codebase for the **Supply-Chain-Management Assistant** application demonstrates a complete pipeline for a Retrieval-Augmented Generation (RAG) system. The system integrates data ingestion, RAG, database management, and a Flask-based web API. The core functionality revolves around retrieving relevant supplier contracts using a text-based search index and augmenting this with a language model to generate responses, then logging these interactions for further feedback analysis.

The key components of the system are:
1. **Data Ingestion (`ingest.py`)**: Indexing text data from supplier contracts.
2. **Database Management (`db.py` and `db_prep.py`)**: Storing conversations and feedback.
3. **RAG System (`rag.py`)**: Conducting search and generating relevant responses.
4. **Web Application (`app.py`)**: Managing the user interface and API endpoints.

## Next Steps for Improvement:

1. **Improved Search Capabilities**:
   - Enhance the text search index to allow more advanced querying features such as fuzzy matching, synonyms, and context-aware searches. Using tools like Elasticsearch or extending the current `minsearch` indexing with advanced NLP techniques (e.g., sentence embeddings) could improve retrieval accuracy.

2. **Response Quality Enhancement**:
   - Implement more sophisticated prompt engineering in `rag.py` to build more contextual prompts for the language model. For example, dynamically adjusting prompt length based on the complexity of the query or previous user interactions could improve answer quality.
   - Fine-tune the language model based on domain-specific supplier contract data to improve its understanding of supply chain management topics.

3. **Feedback Loop Integration**:
   - Leverage user feedback stored in the database to continuously improve the RAG model. You could implement active learning techniques to use highly rated answers to refine the model's performance over time.

4. **User Interaction Personalization**:
   - Enhance the Flask API by personalizing responses based on user profiles or past queries. A recommendation system could suggest similar or follow-up questions to improve the user experience.

5. **Scalability & Performance**:
   - If the application grows in usage, consider scaling the database and search infrastructure to handle larger datasets and more concurrent users. A switch to cloud-based hosting solutions and distributed databases might be necessary for greater performance.
  
