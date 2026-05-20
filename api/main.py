import pandas as pd
from functools import lru_cache
from fastapi import FastAPI
from api.routes.recommendations import router
from pathlib import Path

app = FastAPI(
    title="E-commerce Recommendation API-DATA NOVA ANALYTICS",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTS_PATH = BASE_DIR / "data" / "processed" / "product_catalog.csv"
EVENTS_PATH   = BASE_DIR / "data" / "final" / "events_final.csv"
app.include_router(router)

@lru_cache(maxsize=1)
def _load_product_lookup():
    """Carga lazy info de productos desde eventos (product_id, brand, price, category). Se cachea."""
    df = pd.read_csv(EVENTS_PATH, usecols=["product_id", "brand", "price", "category_code"])
    return (
        df.groupby("product_id", as_index=False)
        .agg(brand=("brand", "first"), price=("price", "mean"), category=("category_code", "first"))
    )

@app.get("/")
def home():
    return {"message": "Recommendation API running"}

@app.get("/products")
def get_products():
    df = pd.read_csv(PRODUCTS_PATH)
    return df.to_dict(orient="records")

@app.get("/products/lookup")
def get_product_lookup(ids: str = ""):
    """Info básica de productos por id. ?ids=1,2,3 — vacío devuelve todos."""
    df = _load_product_lookup()
    if ids:
        id_list = [int(x) for x in ids.split(",") if x.strip().isdigit()]
        df = df[df["product_id"].isin(id_list)]
    return df.to_dict(orient="records")