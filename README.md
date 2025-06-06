# NLP To MONGODB Query

<p align="center">
<img src="images/workflow.png?raw=true" alt="GPT-Architecture" width="800"/>
</p>

Improve LLMs MongoDB query generation ability with the help of advanced retrieval augmented generation.
This project demonstrates a sophisticated approach for improving the generated MongoDB queries from natural language questions using the Large Language Models. It leverages state-of-the-art technologies in natural language processing, vector databases, and advanced retrieval augmented generation to create an efficient and accurate query generation pipeline. It also showcases the use of Weaviate, an open-source vector database, for efficient retrieval of similar questions and their corresponding MongoDB queries.

**Overview**
The project consists of five main components:

1. config.json: Configuration file containing API keys, file paths, and Weaviate schema.
2. main.py: Main script orchestrating data processing, vector database operations, and query generation.
3. pre_process.py: Data processing module for cleaning and embedding questions.
4. query_generation.py: Module for generating MongoDB queries using the Gemini Pro model.
5. weavite_vector_db.py: Weaviate client for vector database operations.
6. app.py: Web-based client for providing User Interface for API to communicate.

**Prerequisites**

1. Python 3.x.
2. Google Gemini API key or any other LLM model.
3. Weaviate (embedded mode used in this project).
4. sentence-transformers.

**Major Components**

1. Data Preprocessing: Utilizes pandas and sentence-transformers to clean and vectorize question-query pairs and schema information.
2. Vector Database: Implements weaviate-client for storing and retrieving semantically similar data objects.
3. Query Generation: Uses Google's generativeai (Gemini Pro) for generating MongoDB queries, with an option for Retrieval-Augmented Generation (RAG).
4. Similarity Re-ranking: Employs sentence-transformers for re-ranking retrieved examples to improve the relevance of context provided to the query generator.

**Installation**

1. Clone the repository:

```python
git clone https://github.com/VasuKashiv/NLP2MongoQ.git
cd NLP2Q

```

2. Install dependencies:

```python
pip install pandas sentence-transformers google-generativeai weaviate-client
```

3. Update config.json with your API keys:

```python
{
  "api_keys": {
    "gemini_api_key": "your-gemini-api-key",
    "weaviate_api_key": "your-weaviate-api-key"
  }
}
```

**Usage**

1. Prepare your data:

- mongodb_array_object.csv: Schema information
- mongodb_array_object.txt: Question-query pairs

2. Run the main script:
   - Set rag=True in main() to enable RAG, or rag=False for non-RAG query generation.
   - Update the parameters to the function: _query_gen.generate_query(class_name, schemas[schema], question, db_client, prompt, rag)_

```python
python main.py
```

3. The script will output the generated MongoDB query.

4. You can also follow procedure described in the workflow notebook as it is easy to modify at run-time.

**How It Works**

1. Data Preprocessing: The DataProcessor class reads and cleans schema and query data, then generates embeddings for each question using a pre-trained sentence transformer model.
2. Vector Database: The WeaviateClient class sets up an in-memory Weaviate database. It creates a class (like a table) with specified properties and adds data objects along with their vector representations.
3. Query Generation: The QueryGeneration class uses Google's Gemini Pro model to generate MongoDB queries. When RAG is enabled:
   - It encodes the input question and retrieves similar questions from the database.
   - It re-ranks these questions using a cross-encoder for better similarity matching.
   - It constructs a prompt with the top two similar questions, their schemas, and queries.
   - It feeds this prompt to Gemini Pro to generate the MongoDB query.
4. Re-ranking: The re-ranking step is crucial. It ensures that the examples provided to the model are not just superficially similar (based on word overlap) but semantically similar. This guides the model to generate more accurate queries.

**Why RAG?**

Retrieval-Augmented Generation significantly improves query generation:

- It provides context-specific examples, unlike static few-shot prompts.
- It handles complex or uncommon queries better by finding relevant past examples.
- It adapts to the nuances of each question, leading to more accurate and efficient queries.

Consider the following question: _Find all the "Sci-Fi" related posts written by VK with post length longer than 50 characters_,

```python
LLM enabled with RAG correctly generates

db.posts.find({
  $and: [
    { tags: "Sci-Fi" },
    { author: "VK" },
    { $expr: { $gt: [{ $strLenCP: "$body" }, 50] } }
  ]
}),
understanding that $strLenCP is needed for string length, the reason behind this generation is the use of relevant question-query-schema pairs fetched from the vector store.

While the LLM Without RAG, incorrectly generates

 { $and: [
    { tags: { $in: ["Sci-Fi"] } },
    { author: "VK" },
    { body: { $gt: 50 } }
  ]
}
, treating body as a number instead of string.
```
