import pickle
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ── Carga de modelos (una sola vez) ──────────────────────────────────────────

def _build_taxonomy_profile(df, taxonomy_col):
    profile = (
        df.groupby(["user_id", taxonomy_col], as_index=False)["interaction_weight"]
        .sum()
        .rename(columns={"interaction_weight": "taxonomy_weight"})
    )
    user_total = (
        profile.groupby("user_id", as_index=False)["taxonomy_weight"]
        .sum()
        .rename(columns={"taxonomy_weight": "user_total_taxonomy_weight"})
    )
    profile = profile.merge(user_total, on="user_id", how="left")
    profile["taxonomy_preference"] = profile["taxonomy_weight"] / profile["user_total_taxonomy_weight"]
    return profile.drop(columns=["user_total_taxonomy_weight"])


def _load():
    with open(BASE_DIR / "models" / "als_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open(BASE_DIR / "models" / "user_profile_als.pkl", "rb") as f:
        user_profile = pickle.load(f)
    with open(BASE_DIR / "models" / "id_maps_als.pkl", "rb") as f:
        id_maps = pickle.load(f)
    cold_start = pd.read_csv(BASE_DIR / "data" / "final" / "recomendaciones_cold_start.csv")
    gmm_df = pd.read_csv(BASE_DIR / "data" / "final" / "user_clustering_gmm_results.csv",
                         usecols=["user_id", "gmm_cluster"])
    user_gmm_map = dict(zip(gmm_df["user_id"], gmm_df["gmm_cluster"]))

    # Cargar eventos para perfiles taxonómicos y mapa de categorías
    ev = pd.read_csv(BASE_DIR / "data" / "final" / "events_final.csv",
                     usecols=["user_id", "product_id", "event_type", "category_code"])
    ev["interaction_weight"] = ev["event_type"].map({"view": 1, "cart": 2, "purchase": 3}).fillna(0)
    parts = ev["category_code"].fillna("").str.split(".", expand=True).reindex(columns=[0, 1, 2])
    ev["nivel1"]      = parts[0].str.lower().fillna("other")
    ev["nivel2_norm"] = parts[1].str.lower().fillna("other")
    ev["nivel3_norm"] = parts[2].str.lower().fillna("other")

    profile_nivel1   = _build_taxonomy_profile(ev, "nivel1")
    profile_nivel2   = _build_taxonomy_profile(ev, "nivel2_norm")
    profile_nivel3   = _build_taxonomy_profile(ev, "nivel3_norm")
    product_taxonomy = ev[["product_id", "nivel1", "nivel2_norm", "nivel3_norm"]].drop_duplicates("product_id")
    product_category_map = ev.drop_duplicates("product_id").set_index("product_id")["nivel1"].to_dict()

    return (model, user_profile, id_maps, cold_start, user_gmm_map,
            product_category_map, profile_nivel1, profile_nivel2, profile_nivel3, product_taxonomy)


(_model, _user_profile, _id_maps, _cold_start_recs, _user_gmm_map,
 _product_category_map, _profile_nivel1, _profile_nivel2, _profile_nivel3, _product_taxonomy) = _load()

_unique_products = [_id_maps["reverse_product_id_map"][i]
                    for i in range(len(_id_maps["reverse_product_id_map"]))]
_N_USERS = len(_user_profile)
_N_ITEMS = len(_unique_products)

# ── Helpers ALS ───────────────────────────────────────────────────────────────

def _user_vec(user_idx):
    if _model.user_factors.shape[0] == _N_USERS:
        return _model.user_factors[user_idx]
    return _model.item_factors[user_idx]

def _item_matrix():
    if _model.user_factors.shape[0] == _N_ITEMS:
        return _model.user_factors
    return _model.item_factors

def _score_items(profile):
    return _item_matrix() @ _user_vec(profile["user_idx"])

# ── Semantic re-ranking ──────────────────────────────────────────────────────

def _semantic_rerank(recs_df, user_id):
    df = recs_df.copy()
    df["user_id"] = user_id

    score_min = df["score"].min()
    score_max = df["score"].max()
    df["score_norm"] = np.where(
        score_max > score_min,
        (df["score"] - score_min) / (score_max - score_min),
        1.0
    )

    df = df.merge(_product_taxonomy, on="product_id", how="left")

    df = df.merge(
        _profile_nivel1[["user_id", "nivel1", "taxonomy_preference"]],
        on=["user_id", "nivel1"], how="left"
    ).rename(columns={"taxonomy_preference": "pref_nivel1"})

    df = df.merge(
        _profile_nivel2[["user_id", "nivel2_norm", "taxonomy_preference"]],
        on=["user_id", "nivel2_norm"], how="left"
    ).rename(columns={"taxonomy_preference": "pref_nivel2"})

    df = df.merge(
        _profile_nivel3[["user_id", "nivel3_norm", "taxonomy_preference"]],
        on=["user_id", "nivel3_norm"], how="left"
    ).rename(columns={"taxonomy_preference": "pref_nivel3"})

    df[["pref_nivel1", "pref_nivel2", "pref_nivel3"]] = (
        df[["pref_nivel1", "pref_nivel2", "pref_nivel3"]].fillna(0)
    )

    df["taxonomic_score"] = (
        0.2 * df["pref_nivel1"] +
        0.3 * df["pref_nivel2"] +
        0.5 * df["pref_nivel3"]
    )

    df["score_final"] = 0.4 * df["score_norm"] + 0.6 * df["taxonomic_score"]

    return df.sort_values(by=["score_final", "score_norm"], ascending=[False, False])


# ── Lógica de recomendación ───────────────────────────────────────────────────

def _recomendar_nuevo_usuario(n=20):
    cluster_default = int(_cold_start_recs["cluster_id"].value_counts().idxmax())
    recs = _cold_start_recs[_cold_start_recs["cluster_id"] == cluster_default].copy()
    recs = recs.head(n)[["product_id", "score_cluster"]].rename(columns={"score_cluster": "score"})
    recs["method"] = "global-popular"
    return recs.reset_index(drop=True)

def _recomendar_por_cluster(cluster_id, n=20):
    recs = _cold_start_recs[_cold_start_recs["cluster_id"] == cluster_id].copy()
    recs = recs.head(n)[["product_id", "score_cluster"]].rename(columns={"score_cluster": "score"})
    recs["method"] = f"cluster-{cluster_id}"
    return recs.reset_index(drop=True)

def recomendar(user_id: int, n: int = 20):
    """
    Retorna (recs_df, meta_dict).
    Tier 0 (desconocido): cold-start global o por cluster (onboarding).
    Tier 1 (1-5 eventos):  blend K-means + ALS ponderado por GMM.
    Tier 2 (>5 eventos):   ALS puro.
    """
    if user_id not in _user_profile:
        return _recomendar_nuevo_usuario(n), None

    profile = _user_profile[user_id]
    tier    = profile["tier"]
    cluster = profile["cluster_id"]
    meta    = {"tier": tier, "cluster_id": cluster}

    if tier == 1:
        gmm_cluster = _user_gmm_map.get(user_id, 1)
        tipo        = "activo" if gmm_cluster == 0 else "pasivo"

        # ALS top 100 → re-ranking semántico
        scores  = _score_items(profile)
        als_df  = pd.DataFrame({"product_id": _unique_products, "score": scores})
        als_df  = als_df.sort_values("score", ascending=False).head(100)
        als_df  = _semantic_rerank(als_df, user_id)

        # Split activo: 70% ALS re-rankeado + 30% cluster / pasivo: 30% + 70%
        als_n   = round(n * 0.7) if tipo == "activo" else round(n * 0.3)
        clus_n  = n - als_n

        als_top  = als_df.head(als_n)[["product_id", "score_final"]].rename(columns={"score_final": "score"})
        clus_top = (_cold_start_recs[_cold_start_recs["cluster_id"] == cluster]
                    .head(clus_n)[["product_id", "score_cluster"]]
                    .rename(columns={"score_cluster": "score"}))

        final = pd.concat([als_top, clus_top], ignore_index=True).drop_duplicates("product_id").head(n)
        final["method"] = f"semantic-hybrid ({tipo})"
        return final[["product_id", "score", "method"]].reset_index(drop=True), {**meta, "gmm": tipo}

    else:
        scores = _score_items(profile)
        recs   = pd.DataFrame({"product_id": _unique_products, "score": scores})
        recs   = recs.sort_values("score", ascending=False).head(100)
        recs   = _semantic_rerank(recs, user_id)
        recs   = recs.head(n)
        recs["method"] = "ALS+semantic"
        return recs[["product_id", "score_final", "method"]].rename(columns={"score_final": "score"}).reset_index(drop=True), {**meta, "gmm": "-"}


def get_top_n_recommendations(user_id: int, n: int = 20):
    """Interfaz simple para la API — devuelve lista de dicts."""
    recs, meta = recomendar(user_id, n)
    result = recs.to_dict(orient="records")
    if meta:
        for r in result:
            r["tier"]       = meta.get("tier")
            r["cluster_id"] = meta.get("cluster_id")
            r["gmm"]        = meta.get("gmm", "-")
    return result


def get_onboarding_products():
    """Un producto representativo por cluster con categorías distintas para el onboarding."""
    used_products, used_categories = set(), set()
    rows = []
    ranked = _cold_start_recs.sort_values("score_cluster", ascending=False)

    for cluster_id in sorted(_cold_start_recs["cluster_id"].unique()):
        cluster_ranked = ranked[ranked["cluster_id"] == cluster_id]
        chosen = None

        # Intentar producto con categoría no usada todavía
        for _, row in cluster_ranked.iterrows():
            pid = int(row["product_id"])
            cat = _product_category_map.get(pid, f"_unk_{pid}")
            if pid not in used_products and cat not in used_categories:
                chosen = {"cluster_id": int(cluster_id), "product_id": pid,
                          "score": float(row["score_cluster"])}
                used_products.add(pid)
                used_categories.add(cat)
                break

        # Fallback: si todas las categorías ya están usadas, tomar el top producto no repetido
        if chosen is None:
            for _, row in cluster_ranked.iterrows():
                pid = int(row["product_id"])
                if pid not in used_products:
                    chosen = {"cluster_id": int(cluster_id), "product_id": pid,
                              "score": float(row["score_cluster"])}
                    used_products.add(pid)
                    break

        if chosen:
            rows.append(chosen)

    return rows


def recomendar_por_cluster(cluster_id: int, n: int = 20):
    """Para usar después del onboarding."""
    return _recomendar_por_cluster(cluster_id, n).to_dict(orient="records")


def is_known_user(user_id: int) -> bool:
    return user_id in _user_profile
