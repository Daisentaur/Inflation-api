import streamlit as st
import requests
import json

# Config
API_URL = "http://localhost:5000"
ADMIN_PASS = "admin123"

# UI Setup
st.set_page_config(layout="wide")
st.title("Product Manager")
st.markdown("""
    <style>
    .gemini-response { border-left: 4px solid #4285F4; padding: 1rem; margin: 1rem 0; }
    </style>
""", unsafe_allow_html=True)

# Pages
page = st.sidebar.selectbox("Menu", ["Search", "Add Product", "View All"])

if page == "Search":
    st.header("🔍 Search Products")
    col1, col2 = st.columns(2)
    with col1:
        product = st.text_input("Product Name")
    with col2:
        year = st.text_input("Year")

    if st.button("Search"):
        params = {"product": product} if product else {}
        if year: params["year"] = year

        try:
            response = requests.get(f"{API_URL}/search", params=params).json()
            
            if "error" in response:
                st.error(response["error"])
            elif response.get("source") == "gemini":
                st.markdown("### Gemini Suggestion")
                st.markdown(f'<div class="gemini-response">', unsafe_allow_html=True)
                st.write(f"**Description:** {response.get('description', 'N/A')}")
                st.write(f"**Price Range:** {response.get('price_range', 'N/A')}")
                st.write(f"**Suggested Price:** {response.get('suggested_price', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.json(response)
        except Exception as e:
            st.error(f"API Error: {e}")

elif page == "Add Product":
    st.header("➕ Add Product")
    with st.form("add_form"):
        product = st.text_input("Product Name*")
        year = st.text_input("Year*")
        price = st.text_input("Price*")
        password = st.text_input("Admin Password*", type="password")
        
        if st.form_submit_button("Add"):
            if not all([product, year, price, password]):
                st.error("Missing fields")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/add",
                        json={"product": product, "year": year, "price": price},
                        headers={"X-Admin-Password": password}
                    )
                    st.success(response.json().get("message", "Added!"))
                except Exception as e:
                    st.error(f"Failed: {e}")

elif page == "View All":
    st.header("📋 All Products")
    if st.button("Refresh"):
        try:
            data = requests.get(f"{API_URL}/list").json()
            for product in set(p["product"] for p in data["data"]):
                with st.expander(product):
                    for item in [p for p in data["data"] if p["product"] == product]:
                        st.write(f"Year: {item['year']} | Price: {item['price']}")
        except Exception as e:
            st.error(f"Error: {e}")
