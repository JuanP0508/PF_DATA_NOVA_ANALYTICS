from fastapi import APIRouter
from api.services.recommender_service import recommend_for_user
from api.services.recommender_service import get_all_records
from api.services.recommender_service import save_new_record
from api.models.record import EventRecord
router = APIRouter()

@router.get("/recommend/{user_id}")
def recommend(user_id: int):

    recommendations = recommend_for_user(user_id)

    return {
        "user_id": user_id,
        "recommendations": recommendations
    }

@router.get("/records")
def get_records():
    """Devuelve todos los registros del archivo inferido_listo.csv"""
    
    records = get_all_records()
    
    return {
        "total_records": len(records),
        "records": records
    }

@router.get("/records/{user_id}")
def get_records(user_id: int):
    """Devuelve todos los registros del usuario especificado"""
    
    records = get_all_records(user_id)
    
    return {
        "user_id": user_id,
        "total_records": len(records),
        "records": records
    }

@router.post("/records")
def create_record(event: EventRecord):
    """Guarda un nuevo evento en el CSV"""
    
    try:
        result = save_new_record(event.dict())
        return result
    except Exception as e:
        return {"error": str(e)}