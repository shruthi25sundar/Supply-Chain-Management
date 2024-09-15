**Supplier Performance Analysis**

![Supplier_management_image_Feb_17__1_](https://github.com/user-attachments/assets/fa6a82f9-1690-4f58-89ea-acfb27e23c82)


**Purpose**
The primary goal of this analysis is to leverage Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs) to enhance the evaluation and management of supplier performance. By integrating advanced natural language processing techniques, the analysis aims to provide insightful and actionable answers to various queries related to suppliers, compliance issues, cost metrics, and other performance indicators.

##Problem Statement
Managing supplier performance involves handling vast amounts of data and addressing numerous factors that can impact the overall supply chain efficiency. Traditional methods of performance evaluation can be time-consuming and may not provide comprehensive insights. This analysis addresses the following challenges:

1. Data Overload: Large volumes of data from multiple suppliers need to be processed and analyzed efficiently.
2. Complex Queries: Answering specific and complex questions about supplier performance, compliance, and risk management can be difficult with traditional methods.
3. Timely Decision-Making: The need for quick and accurate decision-making based on the latest supplier data.
4. Risk Mitigation: Identifying and mitigating risks related to compliance, quality issues, and supply chain disruptions.


**Dataset Overview**

**Supplier Contracts**:

Includes detailed information about supplier contracts, such as:
1. Contract ID, Date Signed, Contract Type, Supplier Name, Risk Level
2. Compliance Issues, Key Terms, Past Performance Score, Negotiation Recommendations
3. Quality Issues, Supply Chain Disruptions, Increased Costs, Compliance and Legal Risks
4. Missed Opportunities, Damaged Relationships, Quality Metrics, Delivery Metrics, Cost Metrics, Relationship Metrics

**End to End Rag Project**

**Methodologies**

### Ingestion Pipeline

- Automated ingestion using a Python script to rename columns, convert text fields to strings, and index the documents using `minsearch`.

### RAG Flow

- **Knowledge Base**: Used `minsearch` for indexing and searching the supplier data.
- **LLM**: Used Groq API to generate answers based on the search results.

### Retrieval Evaluation

#### Approach 1: Minsearch with Boosting

1. **Ground Truth Data**: Loaded and split into validation and test sets.
2. **Evaluation Metrics**: Hit Rate and Mean Reciprocal Rank (MRR).
3. **Parameter Optimization**: Optimized boost parameters using random search to improve MRR.
- Hit rate: 93.7%
- MRR: 93.4%

#### Approach 2: TF-IDF Vectorizer

1. **Preprocessing**: Applied text preprocessing to the questions.
2. **TF-IDF Vectorizer**: Configured with bi-grams, English stop words, and sublinear term frequency scaling.
3. **Evaluation**: Evaluated TF-IDF retrieval approach using the same ground truth data.

- Hit rate: 97.2%
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

### Interface and Ingestion

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

### Implementation Steps

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

If you previously started all applications with Docker Compose, stop the `app` service:

```bash
docker-compose stop app
```

Then run the app on your host machine:

```bash
pipenv shell

cd supply_chain_management

export POSTGRES_HOST=localhost
python app.py
```

**Running with Docker (without Compose)**

To run the application in Docker without Docker Compose, follow these steps:

1. Prepare the environment by running Docker Compose as in the previous section.
2. Build the Docker image:

   ```bash
   docker build -t Supply-Chain-Management .
   ```

3. Run the Docker container:

   ```bash
   docker run -it --rm \
       --network="Supply-Chain-Management_default" \
       --env-file=".env" \
       -e GROQ_API_KEY=${GROQ_API_KEY} \
       -e DATA_PATH="Data/supplier_contracts_dataset.csv" \
       -p 5000:5000 \
       Supply-Chain-Management
   ```

### Time Configuration

Ensure the timestamps are correct when inserting logs into the database. You can check and change the timezone by modifying the `TZ` variable in `.env`.

If the clock in Docker gets out of sync with the host system, you can sync the clock:

```bash
wsl

sudo apt install ntpdate
sudo ntpdate time.windows.com
```

### Using the Application

**CLI**

Start the interactive CLI application:

```bash
pipenv run python cli.py
```

You can also make it randomly select a question from the ground truth dataset:

```bash
pipenv run python cli.py --random
```

**Using `requests`**

Use `requests` to send questions to the running application:

```bash
pipenv run python test.py
```

## Monitoring

Grafana for monitoring the application 

It's accessible at [localhost:3000](http://localhost:3000):

- Login: "admin"
- Password: "admin"

### Dashboards

![dashboard](https://github.com/user-attachments/assets/809aa2dd-33cb-4f78-9007-6f835df9fde7)

