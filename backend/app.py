import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize the Flask app
superkart_api = Flask("SuperKart Sales Predictor")

# Load the trained model pipeline (preprocessing + XGBoost)
model = joblib.load("superkart_model.joblib")

# Feature columns the model was trained on (JSON keys and CSV headers must match)
FEATURES = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
    "Store_Size", "Store_Location_City_Type", "Store_Type",
    "Product_Id_char", "Store_Age_Years", "Product_Type_Category",
]

# Home page (health check)
@superkart_api.get('/')
def home():
    return "Welcome to the SuperKart Sales Prediction API"

# Single prediction: JSON with one product/store record
@superkart_api.post('/v1/predict')
def predict_sales():
    sales_data = request.get_json()
    sample = {feature: sales_data[feature] for feature in FEATURES}
    input_data = pd.DataFrame([sample])
    prediction = model.predict(input_data).tolist()[0]
    return jsonify({'Predicted_Product_Store_Sales_Total': round(prediction, 2)})

# Batch prediction: CSV file upload
@superkart_api.post('/v1/predictbatch')
def predict_sales_batch():
    file = request.files['file']
    input_data = pd.read_csv(file)
    predictions = model.predict(input_data[FEATURES]).tolist()
    result = {str(i): round(p, 2) for i, p in zip(input_data.index, predictions)}
    return jsonify(result)

# Run locally for testing (gunicorn ignores this block)
if __name__ == '__main__':
    superkart_api.run(debug=True)
