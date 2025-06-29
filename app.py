from flask import Flask, jsonify, request, Response
import csv
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

app = Flask(__name__)

# Config
DATA_FILE = "data.csv"
ADMIN_PASSWORD = "admin123"
GEMINI_API_KEY = "your-api-key-here"  # ← Replace with your key

# Initialize Gemini
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)

# Prompt Template
product_prompt = ChatPromptTemplate.from_template("""
    Provide details about the product '{product}' (year: {year}) in JSON with:
    - "description": 1-2 sentence description
    - "price_range": Typical price range
    - "common_years": List of common model years
    - "suggested_price": Estimated price for {year}

    Example:
    {{
        "description": "...",
        "price_range": "$X-$Y",
        "common_years": ["2020", "2021"],
        "suggested_price": "$Z"
    }}
""")

product_chain = product_prompt | llm | StrOutputParser()

# Helper Functions
def load_data():
    try:
        with open(DATA_FILE, mode="r") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []

def save_data(data):
    with open(DATA_FILE, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["product", "year", "price"])
        writer.writeheader()
        writer.writerows(data)

# Routes
@app.route("/")
def home():
    return "Product API with Gemini Integration"

@app.route("/search", methods=["GET"])
def search():
    product = request.args.get("product")
    year = request.args.get("year")
    
    if not product and not year:
        return jsonify({"error": "Provide at least product or year"}), 400

    db_data = load_data()
    result = {}

    # Case 1: Search by product + year
    if product and year:
        match = next((p for p in db_data if p["product"] == product and p["year"] == year), None)
        if match:
            result = {"product": product, "year": year, "price": match["price"], "source": "database"}
        else:
            try:
                gemini_response = product_chain.invoke({"product": product, "year": year})
                result = {**json.loads(gemini_response), "source": "gemini"}
            except Exception as e:
                return jsonify({"error": f"Gemini error: {str(e)}"}), 500

    # Case 2: Search by product only
    elif product:
        matches = [{"year": p["year"], "price": p["price"]} for p in db_data if p["product"] == product]
        result = {"product": product, "data": matches} if matches else {"error": "Not found"}, 404

    # Case 3: Search by year only
    elif year:
        matches = [{"product": p["product"], "price": p["price"]} for p in db_data if p["year"] == year]
        result = {"year": year, "data": matches} if matches else {"error": "Not found"}, 404

    return jsonify(result)

@app.route("/add", methods=["POST"])
def add_product():
    if request.headers.get("X-Admin-Password") != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    if not all(k in data for k in ["product", "year", "price"]):
        return jsonify({"error": "Missing fields"}), 400

    db_data = load_data()
    if any(p["product"] == data["product"] and p["year"] == data["year"] for p in db_data):
        return jsonify({"error": "Duplicate entry"}), 409

    db_data.append(data)
    save_data(db_data)
    return jsonify({"message": "Added successfully"}), 201

@app.route("/list")
def list_all():
    return jsonify({"data": load_data()})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
