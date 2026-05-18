import random

def get_top_n_recommendations(user_id: int):

    # Simulación de recomendaciones SVD
    simulated_products = random.sample(range(1000, 1100), 5)

    recommendations = []

    for product in simulated_products:

        recommendations.append({
            "product_id": product,
            "score": round(random.uniform(3.5, 5.0), 2)
        })

    return recommendations