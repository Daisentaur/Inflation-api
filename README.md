# InMemoryOff%

A simple yet effective Flask + Streamlit web app to track product prices over the years. Designed for clarity, speed, and local usability, **InMemoryOff%** uses a CSV file to keep product-year-price data easily accessible and editable.

UPDATES COMING SOON 
You Gemini integration along with web scraping for better mroe crowd source data. Smart searches also added

Currently sample data with randomly filled values is used in the csv file, but this can be integrated with a real data source of this kind without any changes.

This is a prototype, i might work on the UI and some more features if i think of any in the future

##  Features

- Search product price by year.
- Search all data for a product or a year.
- Add new product data (password-protected).
- Delete existing entries (password-protected).
- View all data.
- Download any result as a JSON file.
- Streamlit frontend for user-friendly interaction.
- Data stored in a CSV file for ease of editing.

##  Project Structure

```
InMemoryOff/
├── app.py              # Flask backend
├── frontend.py         # Streamlit frontend
├── data.csv            # Data store (product, year, price)
├── requirements.txt    # Dependencies
└── README.md           # This file
```

##  How It Works

The app uses:
- **Flask** to serve API endpoints for data operations.
- **Streamlit** to give users an interactive, minimal frontend.
- **CSV** as a backend-friendly, versionable data store.
- A basic `ADMIN_PASSWORD` header check for POST-based modifications.

All search requests are handled with `GET`, and create/delete operations use `POST` with appropriate validation.

## Tip (Important)

> If you're testing API endpoints using Postman, **ensure your requests have the proper `Content-Type` header (`application/json`)** and a valid body. Also, note that sending invalid JSON or missing headers often leads to confusing 500 errors — always check for the correct format first.

##  Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/InMemoryOff.git
cd InMemoryOff
```

### 2. Install Dependencies

Make sure you're in a virtual environment (optional but recommended):

```bash
pip install -r requirements.txt
```

### 3. Run the Backend (Flask)

```bash
python app.py
```

The API will be running at `http://127.0.0.1:5000`.

### 4. Run the Frontend (Streamlit)

In a new terminal:

```bash
streamlit run frontend.py
```

This will open up the user interface in your browser.

##  Admin Operations

I thought adding and deleting data from the dataset should have a layer of security to it, and for a prototype this is all i worked up a admin password which is hardcoded both in the back and frontend files (can obviously be bettered but eh)

To add or delete entries, the admin password must be passed in the headers:

- Header Key: `X-Admin-Password`
- Value: `admin123` (change it inside `app.py` if needed)

##  Sample CSV Format

```
product,year,price
milk,2020,40
milk,2021,45
bread,2020,30
bread,2021,33
```

> Make sure your CSV is always in this format for the app to parse it correctly.

##  API Endpoints Summary

| Method | Endpoint      | Description                       |
|--------|---------------|-----------------------------------|
| GET    | `/`           | Health check                      |
| GET    | `/list`       | Get full dataset                  |
| GET    | `/search`     | Search by product and/or year     |
| POST   | `/add`        | Add new product-year-price (admin)|
| POST   | `/delete`     | Delete specific entry (admin)     |



Built using Flask + Streamlit as part of a personal learning effort.
