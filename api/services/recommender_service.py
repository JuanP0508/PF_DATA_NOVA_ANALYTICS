import pandas as pd
from pathlib import Path
from src.recommender.svd_recommender import (
    get_top_n_recommendations,
    get_onboarding_products,
    recomendar_por_cluster,
    is_known_user,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def get_all_records(user_id: int = None):
    csv_path = BASE_DIR / "data" / "final" / "events_final.csv"
    df = pd.read_csv(csv_path)
    if user_id is not None:
        df = df[df["user_id"] == user_id]
    return df.to_dict(orient="records")


def save_new_record(record_data: dict):
    csv_path = BASE_DIR / "data" / "final" / "events_final.csv"
    df = pd.read_csv(csv_path)
    df_updated = pd.concat([df, pd.DataFrame([record_data])], ignore_index=True)
    df_updated.to_csv(csv_path, index=False)
    return {"message": "Record saved successfully", "record": record_data}


def recommend_for_user(user_id: int, n: int = 10):
    return get_top_n_recommendations(user_id, n)
