from fastapi import APIRouter
from api.services.recommender_service import (
    recommend_for_user,
    get_all_records,
    save_new_record,
)
from api.models.record import EventRecord
from src.recommender.svd_recommender import (
    get_onboarding_products,
    recomendar_por_cluster,
    is_known_user,
)

router = APIRouter()


@router.get("/recommend/{user_id}")
def recommend(user_id: int, n: int = 20):
    return {
        "user_id": user_id,
        "known_user": is_known_user(user_id),
        "recommendations": recommend_for_user(user_id, n),
    }


@router.get("/onboarding/products")
def onboarding_products():
    """Un producto por cluster para mostrar en el onboarding."""
    return {"products": get_onboarding_products()}


@router.get("/onboarding/recommend/{cluster_id}")
def onboarding_recommend(cluster_id: int, n: int = 20):
    """Recomendaciones para un usuario nuevo según el cluster elegido en onboarding."""
    return {
        "cluster_id": cluster_id,
        "recommendations": recomendar_por_cluster(cluster_id, n),
    }


@router.get("/users/{user_id}/exists")
def user_exists(user_id: int):
    return {"user_id": user_id, "exists": is_known_user(user_id)}


@router.get("/records")
def get_records():
    records = get_all_records()
    return {"total_records": len(records), "records": records}


@router.get("/records/{user_id}")
def get_user_records(user_id: int):
    records = get_all_records(user_id)
    return {"user_id": user_id, "total_records": len(records), "records": records}


@router.post("/records")
def create_record(event: EventRecord):
    try:
        return save_new_record(event.dict())
    except Exception as e:
        return {"error": str(e)}
