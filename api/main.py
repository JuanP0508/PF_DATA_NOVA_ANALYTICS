import pandas as pd
from fastapi import FastAPI
from api.routes.recommendations import router
from pathlib import Path

app = FastAPI(
    title="E-commerce Recommendation API-DATA NOVA ANALYTICS",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTS_PATH = BASE_DIR / "data" / "processed" / "product_catalog.csv"
app.include_router(router)

@app.get("/")
def home():
    return {
        "message": "Recommendation API running"
    }
    
# Endpoint to get the product catalog
@app.get("/products")
def get_products():

    df = pd.read_csv(
        PRODUCTS_PATH
    )

    return df.to_dict(orient="records")