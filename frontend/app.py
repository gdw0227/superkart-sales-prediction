import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend (container name "backend" on the Docker network)
BACKEND_URL = "http://backend:7860"

st.title("SuperKart Sales Prediction App")
st.write("Enter product and store details to predict total sales revenue for the product in that store.")

# ---- Online prediction ----
st.subheader("Single Prediction")

col1, col2 = st.columns(2)
with col1:
    Product_Weight = st.number_input("Product Weight", min_value=1.0, max_value=30.0, value=12.66, step=0.1)
    Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    Product_Allocated_Area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0, value=0.056, step=0.001, format="%.3f")
    Product_MRP = st.number_input("Product MRP", min_value=1.0, max_value=500.0, value=147.0, step=1.0)
    Product_Id_char = st.selectbox("Product Category (Product_Id prefix)", ["FD", "DR", "NC"])
with col2:
    Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])
    Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
    Store_Type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
    Store_Age_Years = st.number_input("Store Age (Years)", min_value=0, max_value=100, value=16, step=1)

# JSON keys must match the backend FEATURES list exactly
product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Product_Id_char": Product_Id_char,
    "Store_Age_Years": Store_Age_Years,
    "Product_Type_Category": Product_Type_Category,
}

if st.button("Predict", type="primary"):
    response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data, timeout=30)
    if response.status_code == 200:
        prediction = response.json()["Predicted_Product_Store_Sales_Total"]
        st.success(f"Predicted Product Store Sales Total: {prediction:,.2f}")
    else:
        st.error(f"Error in API request ({response.status_code}): {response.text}")

# ---- Batch prediction ----
st.subheader("Batch Prediction")
uploaded_file = st.file_uploader("Upload a CSV file with the same columns as above", type=["csv"])

if uploaded_file is not None:
    if st.button("Predict for Batch", type="primary"):
        response = requests.post(
            f"{BACKEND_URL}/v1/predictbatch",
            files={"file": ("batch.csv", uploaded_file.getvalue())},
            timeout=60,
        )
        if response.status_code == 200:
            predictions = response.json()
            results = pd.read_csv(uploaded_file)
            results["Predicted_Sales"] = [predictions[str(i)] for i in results.index]
            st.success("Batch predictions completed.")
            st.dataframe(results)
        else:
            st.error(f"Error in API request ({response.status_code}): {response.text}")
