import streamlit as st
import requests
import json
from datetime import datetime

# Config
API_URL = "http://localhost:5000"
ADMIN_PASS = "admin123"

# UI Setup
st.set_page_config(
    page_title="InMemoryOff",
    layout="wide",
    page_icon="📊"
)

# Custom CSS
st.markdown("""
    <style>
    .header { color: #4a4a4a; font-family: 'Arial'; }
    .stTextInput input, .stNumberInput input {
        border: 1px solid #4a4a4a;
        border-radius: 4px;
    }
    .stButton button {
        background-color: #4285F4;
        color: white;
        border-radius: 4px;
    }
    .price-card {
        border-left: 4px solid #4285F4;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)

# App Title
st.markdown('<h1 class="header">InMemoryOff</h1>', unsafe_allow_html=True)
st.caption("A price tracker for Indian market products using RAG and OpenRouter AI")

# Pages
page = st.sidebar.selectbox("Menu", ["📊 Dashboard", "➕ Add Product", "🗑️ Delete Product", "🔍 Raw Data"])

if page == "📊 Dashboard":
    st.header("Price Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        product = st.selectbox(
            "Select Product",
            options=["milk", "rice", "eggs", "potatoes", "onions", "wheat", "sugar", "oil", "tea", "salt"],
            index=0
        )
    with col2:
        year = st.slider(
            "Select Year",
            min_value=1990,
            max_value=2022,
            value=2022
        )

    if st.button("Get Price Analysis", type="primary"):
        with st.spinner("Fetching data..."):
            try:
                response = requests.get(
                    f"{API_URL}/search",
                    params={"product": product, "year": year}
                ).json()

                if "data" in response:
                    for item in response["data"]:
                        st.markdown(f"""
                            <div class="price-card">
                                <h3>{item['product'].title()} ({item['year']})</h3>
                                <p><b>Price:</b> {item['price']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                
                # AI Insights Section
                st.markdown("---")
                st.subheader("Market Insights")
                if "source" in response and response["source"] == "openai+rag":
                    insights = response["data"]
                    st.markdown(f"""
                        <div class="price-card">
                            <p><b>Trend Analysis:</b> {insights.get('price_trend', 'N/A')}</p>
                            <p><b>Inflation Adjusted:</b> {insights.get('inflation_adjusted', 'N/A')}</p>
                            <p><b>Description:</b> {insights.get('description', 'N/A')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No AI insights available for this product/year combination")

            except Exception as e:
                st.error(f"API Error: {str(e)}")

elif page == "➕ Add Product":
    st.header("Add New Product")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            product = st.text_input("Product Name*")
        with col2:
            year = st.number_input("Year*", min_value=1990, max_value=2030, step=1)
        
        price = st.number_input("Price (₹)*", min_value=0.0, format="%.2f")
        password = st.text_input("Admin Password*", type="password")
        
        if st.form_submit_button("Add Product", type="primary"):
            if not all([product, year, price, password]):
                st.error("Please fill all required fields")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/add",
                        json={
                            "product": product.lower(),
                            "year": str(year),
                            "price": str(price)
                        },
                        headers={"X-Admin-Password": password}
                    )
                    if response.status_code == 201:
                        st.success(f"Added {product.title()} ({year}) at ₹{price:.2f}")
                    else:
                        st.error(response.json().get("error", "Failed to add product"))
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")

elif page == "🗑️ Delete Product":
    st.header("Delete Product Entry")
    with st.form("delete_form"):
        # Get current products for selection
        try:
            products = requests.get(f"{API_URL}/search").json()["data"]
            product_list = list(set([p["product"] for p in products]))
        except:
            product_list = []
        
        col1, col2 = st.columns(2)
        with col1:
            product = st.selectbox(
                "Product to Delete*",
                options=product_list,
                disabled=not product_list
            )
        with col2:
            year = st.selectbox(
                "Year*",
                options=sorted(list(set(
                    p["year"] for p in products 
                    if p["product"] == product
                ))) if product else [],
                disabled=not product
            )
        
        password = st.text_input("Admin Password*", type="password", key="del_pass")
        
        if st.form_submit_button("Delete Entry", type="primary"):
            if not all([product, year, password]):
                st.error("Please fill all required fields")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/delete",
                        json={
                            "product": product,
                            "year": year
                        },
                        headers={"X-Admin-Password": password}
                    )
                    if response.status_code == 200:
                        st.success(f"Deleted {product.title()} ({year})")
                    else:
                        st.error(response.json().get("error", "Deletion failed"))
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")

elif page == "🔍 Raw Data":
    st.header("Complete Product Data")
    if st.button("Refresh Data", type="primary"):
        with st.spinner("Loading..."):
            try:
                response = requests.get(f"{API_URL}/search").json()
                if "data" in response:
                    # Group by product
                    products = {}
                    for item in response["data"]:
                        if item["product"] not in products:
                            products[item["product"]] = []
                        products[item["product"]].append(item)
                    
                    # Display in expanders
                    for product, items in products.items():
                        with st.expander(f"{product.title()} ({len(items)} entries)"):
                            for item in sorted(items, key=lambda x: x["year"]):
                                st.write(f"**{item['year']}:** {item['price']}")
                else:
                    st.error("No data available")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Data export
    st.markdown("---")
    st.subheader("Export Data")
    if st.button("Download as JSON"):
        try:
            data = requests.get(f"{API_URL}/search").json()
            json_str = json.dumps(data["data"], indent=2)
            st.download_button(
                label="⬇️ Download Now",
                data=json_str,
                file_name=f"prices_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        except Exception as e:
            st.error(f"Export failed: {str(e)}")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("""
**InMemoryOff** v1.0  
Indian Market Price Tracker  
[API Status: ](http://localhost:5000) 🟢 Online
""")
