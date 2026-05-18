import pandas as pd
from pathlib import Path

def get_all_records(user_id: int):
    """Lee el archivo inferido_listo.csv y devuelve solo los registros del usuario especificado"""
    
    # Ruta al archivo CSV
    csv_path = Path(__file__).parent.parent.parent / "data" / "processed" / "inferido_listo.csv"
    
    # Leer el CSV
    df = pd.read_csv(csv_path)
    
    # Filtrar por user_id (asumiendo que existe una columna 'user_id')
    user_records = df[df['user_id'] == user_id]
    
    # Convertir cada fila a un diccionario (JSON)
    records = user_records.to_dict(orient='records')
    
    return records

# Recomendador  
from src.recommender.svd_recommender import get_top_n_recommendations

def recommend_for_user(user_id: int):

    recommendations = get_top_n_recommendations(user_id)

    return recommendations
# records
def save_new_record(record_data: dict):
    """Guarda un nuevo registro en el archivo inferido_listo.csv"""
    
    # Ruta al archivo CSV
    csv_path = Path(__file__).parent.parent.parent / "data" / "raw" / "events.csv"
    
    # Leer el CSV existente
    df = pd.read_csv(csv_path)
    
    # Crear un DataFrame con el nuevo registro
    new_record = pd.DataFrame([record_data])
    
    # Concatenar con los datos existentes
    df_updated = pd.concat([df, new_record], ignore_index=True)
    
    # Guardar el archivo actualizado
    df_updated.to_csv(csv_path, index=False)
    
    return {"message": "Record saved successfully", "record": record_data}