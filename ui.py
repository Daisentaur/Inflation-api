import streamlit as st
import requests
import json

# API configuration
API_BASE_URL = "http://127.0.0.1:5000"
ADMIN_PASSWORD = "admin123"

# Basic styling
st.markdown("""
    <style>
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        border: 1px solid #000;
        border-radius: 0;
    }
    .stButton button {
        border: 1px solid #000;
        background-color: white;
        color: black;
        border-radius: 0;
        padding: 0.25rem 1rem;
    }
    .stButton button:hover {
        background-color: #f0f0f0;
    }
    pre {
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    </style>
    """, unsafe_allow_html=True)

st.title(" InMemoryOff% ")
st.write("A simple interface for the Product API")

# Navigation
menu = st.sidebar.selectbox("Menu", ["Search", "Add Product", "Delete Product", "View All"])

if menu == "Search":
    st.header("Search Products")
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            product = st.text_input("Product Name")
        with col2:
            year = st.text_input("Year")
        
        download_requested = st.checkbox("Download results as JSON")
        submitted = st.form_submit_button("Search")
        
        if submitted:
            params = {}
            if product:
                params["product"] = product
            if year:
                params["year"] = year
            
            try:
                response = requests.get(f"{API_BASE_URL}/search", params=params)
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display results
                    st.subheader("Search Results")
                    st.json(result)
                    
                    # Handle download
                    if download_requested:
                        json_str = json.dumps(result, indent=2)
                        st.download_button(
                            label="⬇️ Download JSON",
                            data=json_str,
                            file_name=f"search_result_{product or 'all'}_{year or 'all'}.json",
                            mime="application/json",
                            key="download_json"
                        )
                else:
                    st.error(f"Error: {response.json().get('error')}")
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")

elif menu == "Add Product":
    st.header("Add New Product")
    with st.form("add_form"):
        product = st.text_input("Product Name*")
        year = st.text_input("Year*")
        price = st.text_input("Price*")
        password = st.text_input("Admin Password*", type="password")
        
        submitted = st.form_submit_button("Add Product")
        if submitted:
            if not all([product, year, price, password]):
                st.error("Please fill all required fields (*)")
            else:
                headers = {"X-Admin-Password": password}
                data = {
                    "product": product,
                    "year": year,
                    "price": price
                }
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/add",
                        json=data,
                        headers=headers
                    )
                    if response.status_code == 201:
                        st.success(response.json().get("message"))
                    else:
                        st.error(f"Error: {response.json().get('error')}")
                except Exception as e:
                    st.error(f"Failed to connect to API: {str(e)}")

elif menu == "Delete Product":
    st.header("Delete Product Entry")
    with st.form("delete_form"):
        product = st.text_input("Product Name*")
        year = st.text_input("Year*")
        password = st.text_input("Admin Password*", type="password")
        
        submitted = st.form_submit_button("Delete Entry")
        if submitted:
            if not all([product, year, password]):
                st.error("Please fill all required fields (*)")
            else:
                headers = {"X-Admin-Password": password}
                data = {
                    "product": product,
                    "year": year
                }
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/delete",
                        json=data,
                        headers=headers
                    )
                    if response.status_code == 200:
                        st.success(response.json().get("message"))
                    else:
                        st.error(f"Error: {response.json().get('error')}")
                except Exception as e:
                    st.error(f"Failed to connect to API: {str(e)}")

elif menu == "View All":
    st.header("All Product Data")
    if st.button("Refresh Data"):
        try:
            response = requests.get(f"{API_BASE_URL}/list")
            if response.status_code == 200:
                data = response.json()
                st.subheader("Complete Product List")
                st.json(data)  # Properly formatted JSON display
                
                # Add download button for the complete list
                json_str = json.dumps(data, indent=2)
                st.download_button(
                    label="⬇️ Download Complete List",
                    data=json_str,
                    file_name="complete_product_list.json",
                    mime="application/json",
                    key="download_full_list"
                )
            else:
                st.error(f"Error: {response.json().get('error')}")
        except Exception as e:
            st.error(f"Failed to connect to API: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.write("Simple API Frontend")
st.sidebar.write(f"API: {API_BASE_URL}")