import json
import os
import google.generativeai as genai
from pre_process import DataProcessor
from weavite_vector_db import WeaviateClient
from query_generation import QueryGeneration

# Load configuration from config.json
# This file likely contains API keys, file paths, and other configuration parameters
with open('config.json', 'r') as f:
    config = json.load(f)

# Set Gemini API key as an environment variable and configure the genai library
os.environ['GOOGLE_API_KEY'] = config['api_keys']['gemini_api_key']
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

def main(rag=True):
    """
    Main function to orchestrate the data processing, vector database operations, and query generation.

    :param rag: Boolean to determine whether to use RAG (Retrieval-Augmented Generation) or not.
    """
    # Initialize DataProcessor with CSV and TXT file paths from config
    csv_path = config['file_paths']['csv_path']
    txt_path = config['file_paths']['txt_path']
    processor = DataProcessor(csv_path, txt_path)
    
    # Process data and get a DataFrame
    processed_df = processor.process()
    
    # Initialize WeaviateClient for vector database operations
    db_client = WeaviateClient()
    
    # Get Weaviate class configuration from config
    class_name = config['weaviate']['class_name']
    properties = config['weaviate']['properties']
    
    # Create a class in Weaviate and add processed data
    db_client.create_class(class_name, properties)
    db_client.add_data_object(class_name, processed_df)
    
    # Initialize QueryGeneration with the sentence embedding model from the DataProcessor
    # Use different prompts based on whether RAG is enabled or not
    prompt = config['query_generation']['prompt_rag'] if rag else config['query_generation']['prompt_nonrag']
    query_gen = QueryGeneration(processor.model)
    
    # Define schemas for various data collections
    # These schemas describe the structure of MongoDB collections
    accounts_schema = '''{"collections": [{"name": "accounts", "indexes": [{"key": {"_id": 1}}, {"key": {"account_id": 1}}], "uniqueIndexes": [], "document": {"properties": {"_id": {"bsonType": "objectId"}, "account_id": {"bsonType": "int"}, "limit": {"bsonType": "int"}, "products": {"bsonType": "array", "items": {"bsonType": "string"}}}}}], "version": 1}'''
    trips_schema = '''{"collections": [{"name": "trips", "indexes": [{"key": {"_id": 1}}], "uniqueIndexes": [], "document": {"properties": {"_id": {"bsonType": "objectId"}, "tripduration": {"bsonType": "int"}, "start_station_id": {"bsonType": "int"}, "start_station_name": {"bsonType": "string"}, "end_station_id": {"bsonType": "int"}, "end_station_name": {"bsonType": "string"}, "bikeid": {"bsonType": "int"}, "usertype": {"bsonType": "string"}, "birth_year": {"bsonType": "int"}, "gender": {"bsonType": "int"}, "start_station_location": {"bsonType": "object", "properties": {"type": {"bsonType": "string", "enum": ["Point"]}, "coordinates": {"bsonType": "array", "items": {"bsonType": "double"}}}}, "end_station_location": {"bsonType": "object", "properties": {"type": {"bsonType": "string", "enum": ["Point"]}, "coordinates": {"bsonType": "array", "items": {"bsonType": "double"}}}}, "start_time": {"bsonType": "date"}, "stop_time": {"bsonType": "date"}}}}], "version": 1}'''
    posts_schema = '''{"collections": [{"name": "posts", "indexes": [{"key": {"_id": 1}}, {"key": {"permalink": 1}}, {"key": {"author": 1}}, {"key": {"title": 1}}, {"key": {"tags": 1}}, {"key": {"comments.date": 1}}], "uniqueIndexes": [], "document": {"properties": {"_id": {"bsonType": "string"}, "body": {"bsonType": "string"}, "permalink": {"bsonType": "string"}, "author": {"bsonType": "string"}, "title": {"bsonType": "string"}, "tags": {"bsonType": "array", "items": {"bsonType": "string"}}, "comments": {"bsonType": "array", "items": {"bsonType": "object", "properties": {"body": {"bsonType": "string"}, "email": {"bsonType": "string"}, "author": {"bsonType": "string"}, "date": {"bsonType": "date"}}}}}}}], "version": 1}'''
    inspections_schema = '''{"collections": [{"name": "inspections", "indexes": [{"key": {"_id": 1}}, {"key": {"id": 1}}, {"key": {"certificate_number": 1}}, {"key": {"date": 1}}, {"key": {"result": 1}}, {"key": {"sector": 1}}, {"key": {"address.city": 1}}, {"key": {"address.zip": 1}}], "uniqueIndexes": [], "document": {"properties": {"_id": {"bsonType": "string"}, "id": {"bsonType": "string"}, "certificate_number": {"bsonType": "int"}, "business_name": {"bsonType": "string"}, "date": {"bsonType": "string"}, "result": {"bsonType": "string"}, "sector": {"bsonType": "string"}, "address": {"bsonType": "object", "properties": {"city": {"bsonType": "string"}, "zip": {"bsonType": "int"}, "street": {"bsonType": "string"}, "number": {"bsonType": "int"}}}}}}], "version": 1}'''

    # Store schemas in a dictionary for easy access
    schemas = {
        'accounts': accounts_schema,
        'trips': trips_schema,
        'inspections': inspections_schema,
        'posts': posts_schema
    }

    # Generate a query using the RAG method or non-RAG method
    schema = 'posts'  # Choose the schema for the query
    question = 'Find all the "Sci-Fi" related posts written by me with post length longer than 50 characters'
    
    # Generate the query and get the result
    result = query_gen.generate_query(class_name, schemas[schema], question, db_client, prompt, rag)
    
    # Print the generated query or explanation
    print(result.text)

if __name__ == "__main__":
    # Run the main function with RAG disabled (set to False)
    main(rag=False)