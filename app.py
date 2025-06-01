#testing note to add to readme in chatgpt

from flask import Flask, jsonify, request, Response #response needed for download
import csv
import json

app = Flask(__name__) 

DATA_FILE = "data.csv"
ADMIN_PASSWORD = "admin123"

def load_data():
    with open(DATA_FILE, mode="r", newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)
    
def save_data(data):
    with open(DATA_FILE, mode="w", newline='') as f:
        fieldnames = ["product", "year", "price"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

@app.before_request 
def log_path():#for testing (POSTMAN errors)
    print(f"Raw path: '{request.path}'")

@app.route('/')
def home():
    return "Hello, Flask is working!"


@app.route('/add', methods=['POST'])
def add_product(): #works 
    data = request.get_json()

    product = data.get('product')
    year = data.get('year')
    price = data.get('price')

    password = request.headers.get("X-Admin-Password")
    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized. Invalid password."}), 403

    if not all ([product, year, price]):
        return jsonify({"error": "Missing required fields"}), 400
    
    product_data = load_data()

    if product in product_data and year in product_data[product]:
        return jsonify({"error": "Duplicate data. This entry already exists."}), 409

    if product not in product_data: 
        product_data.append({
        "product": data["product"],
        "year": data["year"],
        "price": str(data["price"])  
    })

    save_data(product_data)

    return jsonify({
        "message": f"Product added successfully. Price for {product} in {year} added."
        }), 201

@app.route('/delete', methods=['POST'])
def delete_product(): #works
    data = request.get_json()
    product = data.get('product')
    year = data.get('year')
    

    password = request.headers.get("X-Admin-Password")
    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized. Invalid password."}), 403

    if not all ([product, year]):
        return jsonify({"error": "Missing required fields"}), 400
    
    product_data = load_data()

    original_len = len(product_data) #to check change
    product_data = [entry for entry in product_data if not (entry['product'] == product and entry['year'] == year)]

    if len(product_data) == original_len:
        return jsonify({"error": f"No entry found for {product} in {year}."}), 404

    save_data(product_data)
    return jsonify({"message": f"Deleted {product} for year {year} successfully."}), 200


@app.route('/search', methods=['GET'])
def search_data(): #works 
    product = request.args.get("product")
    year = request.args.get("year")
    download = request.args.get("download", "false").lower() == "true"

    print(f"Search request received for: product='{product}', year='{year}', download={download}")

    product_data = load_data()

    if not product and not year:
        return jsonify({"error": "Please provide at least a product or year."}), 400

    result = {}

    # 1 - both product and year
    if product and year:
        for entry in product_data:
            if entry["product"] == product and entry["year"] == year:
                result = {
                    "product": product,
                    "year": year,
                    "price": entry["price"]
                }
                break
        else:
            return jsonify({"error": f"No data found for {product} in {year}"}), 404

    # 2 - only product (show all years rates for product)
    elif product:
        matches = [
            {"year": entry["year"], "price": entry["price"]}
            for entry in product_data if entry["product"] == product
        ]
        if matches:
            result = {"product": product, "data": matches}
        else:
            return jsonify({"error": f"No data found for product '{product}'"}), 404

    # 3 - only year (show all products rates of year)
    elif year:
        matches = [
            {"product": entry["product"], "price": entry["price"]}
            for entry in product_data if entry["year"] == year
        ]
        if matches:
            result = {"year": year, "data": matches}
        else:
            return jsonify({"error": f"No data found for year '{year}'"}), 404

    # download requested, send as file
    if download:
        response = Response(
            json.dumps(result, indent=2),
            mimetype="application/json"
        )
        response.headers["Content-Disposition"] = "attachment; filename=search_result.json"
        return response

    # Normal API JSON response
    return jsonify(result), 200

@app.route('/list')
def whole_list():#for testing (POSTMAN errors)
    product_data = load_data()  
    return jsonify({"data": product_data})



if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
