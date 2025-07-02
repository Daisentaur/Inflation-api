from flask import Flask, jsonify, request
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
import os
import csv
import json
from dotenv import load_dotenv

# Initialize Flask
app = Flask(__name__)

# Configuration
load_dotenv()
DATA_FILE = "data.csv"
ADMIN_PASSWORD = "admin123"
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
os.environ['USER_AGENT'] = 'PriceTracker/1.0'

# Initialize OpenRouter LLM
llm = ChatOpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Indian Price Tracker"
    },
    model="openai/gpt-3.5-turbo",
    temperature=0.5
)

# Initialize Embeddings (using OpenRouter)
embeddings = OpenAIEmbeddings(
    api_key=OPENROUTER_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    headers={
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Indian Price Tracker"
    }
)

# RAG System
class RAGSystem:
    def __init__(self):
        self.vectorstore = None
        
    def update_index(self, products):
        """Update vector store with product data"""
        if not products:
            return
            
        docs = [
            Document(
                page_content=f"{p['product']} ({p['year']})",
                metadata={
                    "product": p["product"],
                    "year": p["year"],
                    "price": f"₹{float(p['price']):.2f}",
                    "raw_price": float(p["price"])
                }
            )
            for p in products
        ]
        
        self.vectorstore = FAISS.from_documents(docs, embeddings)

rag_system = RAGSystem()

# Helper functions
def load_data():
    try:
        with open(DATA_FILE, mode="r") as f:
            return list(csv.DictReader(f))
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

def save_data(data):
    try:
        with open(DATA_FILE, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["product", "year", "price"])
            writer.writeheader()
            writer.writerows(data)
        rag_system.update_index(data)  # Update search index
    except Exception as e:
        print(f"Error saving data: {e}")

# Initialize with existing data
save_data(load_data())  # This creates the initial index

# API Endpoints
@app.route("/")
def home():
    return "Indian Price Tracker API - Use /search, /add, /delete"

@app.route("/search", methods=["GET"])
def search():
    product = request.args.get("product")
    year = request.args.get("year")
    
    db_data = load_data()
    results = [
        {**p, "price": f"₹{float(p['price']):.2f}"} 
        for p in db_data 
        if (not product or p["product"] == product) and 
           (not year or p["year"] == year)
    ]
    
    return jsonify({"data": results})

@app.route("/add", methods=["POST"])
def add_product():
    # Authentication
    if request.headers.get("X-Admin-Password") != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 403
    
    # Validate input
    try:
        data = request.get_json()
        assert all(k in data for k in ["product", "year", "price"])
        float(data["price"])  # Test if price is numeric
    except:
        return jsonify({"error": "Invalid data format"}), 400
    
    # Add to database
    db_data = load_data()
    db_data.append(data)
    save_data(db_data)
    
    return jsonify({
        "message": "Added successfully",
        "price": f"₹{float(data['price']):.2f}"
    }), 201

@app.route("/delete", methods=["POST"])
def delete_product():
    # Authentication
    if request.headers.get("X-Admin-Password") != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 403
    
    # Validate input
    try:
        data = request.get_json()
        assert all(k in data for k in ["product", "year"])
    except:
        return jsonify({"error": "Invalid data format"}), 400
    
    # Delete from database
    db_data = load_data()
    original_count = len(db_data)
    db_data = [p for p in db_data if not (p["product"] == data["product"] and p["year"] == data["year"])]
    
    if len(db_data) == original_count:
        return jsonify({"error": "Product not found"}), 404
    
    save_data(db_data)
    return jsonify({"message": "Deleted successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
